-- _repo-links.lua
-- Injects GitHub repository action links into Quarto manuscript HTML output.
--
-- Configure in _quarto.yml (update repo-url when using the template):
--   repo-url: https://github.com/owner/repo
--   repo-actions: [edit, source]
--
-- Produces:
--   • A GitHub icon in the title banner (links to the repo root)
--   • "Edit this page" / "View source" links appended to the TOC sidebar

local repo_url = nil
local want_edit = false
local want_source = false

function Meta(meta)
  if meta["repo-url"] then
    repo_url = pandoc.utils.stringify(meta["repo-url"])
  end
  local actions = meta["repo-actions"]
  if actions and pandoc.utils.type(actions) == "List" then
    for _, v in ipairs(actions) do
      local a = pandoc.utils.stringify(v)
      if a == "edit"   then want_edit   = true end
      if a == "source" then want_source = true end
    end
  end
  return meta
end

function Pandoc(doc)
  if not FORMAT:match("html") then return doc end
  if not repo_url then return doc end
  if not (want_edit or want_source) then return doc end

  -- quarto.doc.input_file reads quarto-source param — the actual .qmd source.
  -- Strip the project root to get a repo-relative path.
  local abs_input    = quarto.doc.input_file or ""
  local project_root = os.getenv("QUARTO_PROJECT_DIR") or pandoc.system.get_working_directory()
  -- +2: skip trailing separator after project root
  local rel_path = abs_input:sub(#project_root + 2)
  if rel_path == "" then rel_path = abs_input end

  local toc_items = {}
  if want_edit then
    table.insert(toc_items, string.format(
      '<li><a href="%s/edit/main/%s" class="toc-action">' ..
        '<i class="bi bi-github"></i>Edit this page</a></li>',
      repo_url, rel_path
    ))
  end
  if want_source then
    table.insert(toc_items, string.format(
      '<li><a href="%s/blob/main/%s" class="toc-action">' ..
        '<i class="bi empty"></i>View source</a></li>',
      repo_url, rel_path
    ))
  end

  local toc_html = "<ul>" .. table.concat(toc_items, "") .. "</ul>"

  local script = string.format([[
<script>
(function () {
  function inject() {
    // toc-actions appended to the TOC nav
    var toc = document.querySelector("nav#TOC");
    if (toc) {
      var el = document.createElement("div");
      el.className = "toc-actions";
      el.innerHTML = %q;
      toc.appendChild(el);
    }
    // GitHub icon in the title banner
    var banner = document.querySelector(".quarto-title-banner");
    if (banner && !banner.querySelector(".quarto-repo-link")) {
      banner.style.position = "relative";
      var a = document.createElement("a");
      a.href = %q;
      a.className = "quarto-repo-link";
      a.setAttribute("aria-label", "GitHub repository");
      a.style.cssText =
        "position:absolute;top:1rem;right:1rem;color:inherit;" +
        "opacity:0.7;font-size:1.4rem;text-decoration:none;line-height:1;";
      a.innerHTML = '<i class="bi bi-github"></i>';
      banner.appendChild(a);
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inject);
  } else {
    inject();
  }
})();
</script>]], toc_html, repo_url)

  doc.blocks:insert(pandoc.RawBlock("html", script))
  return doc
end
