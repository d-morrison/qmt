#!/usr/bin/env python3
"""
Script to detect changed sections by comparing rendered HTML files.
This compares the PR's rendered files with the published versions from gh-pages.
Adapted from detect-changed-chapters.py for the manuscript project type.
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def checkout_base_files(base_ref='origin/gh-pages', target_dir='/tmp/base-files'):
    """
    Check out the base HTML files from gh-pages for comparison.

    Returns:
        Path to directory with base files, or None if checkout failed
    """
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ['git', 'fetch', 'origin', 'gh-pages:gh-pages'],
            check=False,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Could not fetch gh-pages branch: {result.stderr}")
            print("This is expected for:")
            print("  - First PR to a new repository")
            print("  - Repositories not using gh-pages for deployment")
            return None

        result = subprocess.run(
            ['git', 'ls-tree', '-r', '--name-only', base_ref],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            files = [f for f in result.stdout.split('\n')
                    if f.endswith('.html') or f.endswith('.docx')]

            for file in files:
                output_path = target_path / file
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, 'wb') as f:
                    subprocess.run(
                        ['git', 'show', f'{base_ref}:{file}'],
                        stdout=f,
                        check=False
                    )

            return target_path if files else None

        return None
    except Exception as e:
        print(f"Could not check out base files: {e}", file=sys.stderr)
        return None


def files_differ(file1, file2):
    """Check if two files differ."""
    if not file1.exists() or not file2.exists():
        return file1.exists() or file2.exists()

    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() != f2.read()
    except Exception:
        return True


def main():
    rendered_dir = Path(os.getenv('HTML_DIR', './_manuscript'))

    if not rendered_dir.exists():
        print("Rendered files directory does not exist yet")
        return

    print("Checking out base files from gh-pages for comparison...")
    base_dir = checkout_base_files()

    if not base_dir:
        print("\nWARNING: Could not check out base files from gh-pages")
        print("Treating all rendered files as changed.")

        html_files = list(rendered_dir.rglob("*.html"))
        changed_chapters = [
            str(f.relative_to(rendered_dir).with_suffix(''))
            for f in html_files
            if f.stem != 'index'
        ]
    else:
        print(f"Base files checked out successfully to {base_dir}\n")

        html_files = list(rendered_dir.rglob("*.html"))

        changed_chapters = []
        for html_file in html_files:
            if html_file.stem == 'index':
                continue

            rel_path = html_file.relative_to(rendered_dir)
            base_html = base_dir / rel_path

            html_changed = files_differ(html_file, base_html)

            docx_file = html_file.with_suffix('.docx')
            base_docx = base_dir / rel_path.with_suffix('.docx')
            docx_changed = docx_file.exists() and files_differ(docx_file, base_docx)

            if html_changed or docx_changed:
                chapter_id = str(rel_path.with_suffix(''))
                changed_chapters.append(chapter_id)
                print(f"  Changed: {chapter_id} (HTML: {html_changed}, DOCX: {docx_changed})")

    if not changed_chapters:
        print("No sections changed")
        env_file = os.getenv('GITHUB_ENV')
        if env_file:
            with open(env_file, 'a') as f:
                f.write("PREVIEW_CHANGED_CHAPTERS=\n")
                f.write("PREVIEW_SHOW_HIGHLIGHTS=false\n")

        json_path = rendered_dir / 'changed-chapters.json'
        with open(json_path, 'w') as f:
            json.dump({'changed_chapters': [], 'count': 0}, f)
        print("Created empty changed-chapters.json file")
        return

    print(f"\nChanged sections: {', '.join(changed_chapters)}")

    env_file = os.getenv('GITHUB_ENV')
    if env_file:
        with open(env_file, 'a') as f:
            f.write("PREVIEW_CHANGED_CHAPTERS<<EOF\n")
            f.write('\n'.join(changed_chapters) + '\n')
            f.write("EOF\n")
            disable_highlights = os.getenv('DISABLE_PREVIEW_HIGHLIGHTS', 'false').lower() == 'true'
            if disable_highlights:
                f.write("PREVIEW_SHOW_HIGHLIGHTS=false\n")
            else:
                f.write("PREVIEW_SHOW_HIGHLIGHTS=true\n")

    json_path = rendered_dir / 'changed-chapters.json'
    with open(json_path, 'w') as f:
        json.dump({
            'changed_chapters': changed_chapters,
            'count': len(changed_chapters)
        }, f)


if __name__ == '__main__':
    main()
