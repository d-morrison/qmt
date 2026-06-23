# Contributing to Your Quarto Manuscript

Thank you for your interest in contributing to this manuscript!

## How to contribute

### For manuscript authors

If you're working on content for this manuscript:

1. **Create a new branch** for your work:
   ```bash
   git checkout -b section/your-topic
   ```

2. **Edit `index.qmd`** or add supplementary notebooks in `notebooks/`

3. **Preview your changes** locally:
   ```bash
   quarto preview
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add section on your topic"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin section/your-topic
   ```

### Content guidelines

- Use clear, concise language
- Include code examples where appropriate
- Add references to `references.bib` for any citations
- Use appropriate headings (`#` for top-level sections, `##` for subsections)
- Include figures in an `images/` directory
- Test code examples to ensure they run

### Markdown formatting

- Use **bold** for emphasis on terms
- Use `code` formatting for inline code, file names, and commands
- Use code blocks with language specification for longer code examples
- Use callout boxes for important information:
  ```markdown
  ::: {.callout-note}
  Important information here
  :::
  ```

### Adding figures

1. Place images in the `images/` directory
2. Reference them in your `.qmd` file:
   ```markdown
   ![Caption text](images/your-image.png){#fig-label}
   ```

### Adding supplementary notebooks

1. Create a new `.qmd` file in the `notebooks/` directory
2. Register it in `_quarto.yml` under `manuscript: notebooks:`
3. Reference computations from the main article using `{{< embed notebooks/your-notebook.qmd#label >}}`

### Adding URLs

When adding external links to your content, please ensure:

1. **URLs are valid and reachable** — the repository has an automated link checker that runs weekly and on every push/pull request
2. **Use HTTPS when possible** — prefer secure URLs over HTTP
3. **Check link stability** — use permanent links (permalinks) when available rather than URLs that might change

The link checker workflow will automatically:

- Check all URLs in `.qmd`, `.md`, and `.html` files
- Report broken or unreachable links
- Create issues for broken links that need attention

If you need to exclude certain URLs from checking (e.g., example URLs), add them to the `lychee.toml` configuration file.

#### Manual override for link checking

If you have manually verified all links in your pull request and want to skip the automated link checker, you can add the **`links checked by hand`** label to your PR. This will cause the link checker workflow to skip the check for that specific pull request, while still running on the main branch and scheduled checks.

### Citations

Add BibTeX entries to `references.bib`:

```bibtex
@article{authorYEAR,
  title={Article Title},
  author={Author, First and Author, Second},
  journal={Journal Name},
  year={2024},
  doi={10.xxxx/xxxxx}
}
```

Then cite in text: `@authorYEAR`

## Questions?

If you have questions about contributing, please open an issue in the repository.
