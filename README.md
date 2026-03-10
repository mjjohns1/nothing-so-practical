## Local Development Guide

### Prerequisites

- [Hugo](https://gohugo.io/installation/) (extended version)
- [Node.js / npx](https://nodejs.org/) (for Pagefind search indexing)

### Running the dev server

```bash
hugo server --baseURL http://localhost:1313/
```

Opens at `http://localhost:1313`. Live-reloads on file changes.

> **Note:** Search will not work in the dev server. See below for previewing search locally.

### Previewing search locally

Search requires Pagefind to index the built site output. To test it:

```bash
hugo && npx pagefind --site public
cd public && python3 -m http.server 1313
```

Then open `http://localhost:1313`.

## Writing Posts

### Creating a new post

```bash
hugo new post/my-post-title.md
```

This creates `content/post/my-post-title.md` as a draft. Edit the file, then set `draft: false` when ready to publish. Use lowercase-hyphenated filenames — the filename becomes the URL slug (e.g. `my-post-title` → `/post/my-post-title/`).

### Front matter

All fields are optional except `title` and `date`:

```yaml
---
title:       "Post Title"           # required
subtitle:    ""                     # shown below title on the post page
description: ""                     # used for SEO meta and post cards
date:        2026-01-01             # required; controls sort order
author:      "MJ"
image:       "img/post-bg.jpg"      # hero/banner image; place file in static/img/
tags:        ["tag1", "tag2"]       # shown in sidebar and used for filtering
categories:  ["Category"]
draft:       false                  # set to false to publish
---
```

- **`image`** — path is relative to `static/`. Place images in `static/img/` and reference them as `"img/filename.jpg"`.
- **`tags`** — tags with `featured_condition_size: 1` or more posts appear in the sidebar.
- **`draft: true`** — drafts are excluded from builds and not deployed. Use `hugo server -D` to preview drafts locally.

### Images in post body

Place images in `static/img/` and reference them in Markdown:

```markdown
![Alt text](/img/my-image.png)
```

### Math / LaTeX

Not enabled by default. Check the theme's example posts for KaTeX/MathJax options if needed.

## Writing Posts from a Jupyter Notebook

The recommended workflow is to convert a notebook to Markdown using `nbconvert`, then clean up the output for Hugo.

### 1. Convert the notebook

```bash
jupyter nbconvert --to markdown my-analysis.ipynb
```

This produces `my-analysis.md` and a `my-analysis_files/` folder containing any output images.

### 2. Move files into the Hugo content directory

```bash
# Move the markdown file
mv my-analysis.md content/post/my-analysis.md

# Move the images into static
mv my-analysis_files/ static/img/my-analysis_files/
```

### 3. Fix image paths

`nbconvert` generates image paths like `my-analysis_files/figure-markdown_strict/cell-1-output-1.png`. Update them to Hugo's static path:

Find and replace in the markdown file:
- **Find:** `my-analysis_files/`
- **Replace:** `/img/my-analysis_files/`

Using sed:
```bash
sed -i '' 's|my-analysis_files/|/img/my-analysis_files/|g' content/post/my-analysis.md
```

### 4. Add Hugo front matter

`nbconvert` output has no front matter. Add it at the top of the file:

```yaml
---
title:       "My Analysis"
subtitle:    ""
description: ""
date:        2026-01-01
author:      "MJ"
tags:        ["tag1", "tag2"]
categories:  ["Category"]
draft:       false
---
```

### 5. Clean up (optional but recommended)

- Remove any raw HTML `<div>`/`<style>` blocks nbconvert may emit for Jupyter widgets
- Tidy up code block language hints (nbconvert uses ` ```python ` which Hugo renders correctly)
- Check that DataFrames rendered as HTML tables look acceptable, or replace with images

## Deployment

Pushing to `main` triggers the GitHub Actions workflow (`.github/workflows/hugo.yaml`), which:

1. Builds the site with `hugo --minify`
2. Runs `npx pagefind --site public` to generate the search index
3. Deploys to GitHub Pages
