# Repository Guidelines

## Project Structure & Module Organization
- `_posts/`: Markdown content. Use `YYYY-MM-DD-struggle-N.markdown` and include front matter: `layout`, `title`, `date`, `author`, `categories`, `tags`.
- `_layouts/`, `_includes/`, `_data/`: Jekyll templates and shared snippets.
- `staff/`: Team profile page and data.  `img/`: images (e.g., `img/struggle/<N>/...`).
- `less/`, `css/`, `js/`: Source styles/scripts (edit `less/` and `js/`; generated files in `css/`/`js/*.min.js`).
- `_config.yml`: Site settings. `_site/`: build output (do not edit).
- `script/cibuild`: CI build entry.

## Build, Test, and Development Commands
- Docker (recommended):
  - First time: `docker run -it -p 4000:4000 -v $PWD:/srv/jekyll --name kodevops-blog jekyll/jekyll bash` then inside: `bundle update`.
  - Serve: `docker start kodevops-blog && docker exec -it kodevops-blog jekyll serve` → http://localhost:4000
- Local Ruby: `bundle install && bundle exec jekyll serve` (build only: `bundle exec jekyll build`).
- Assets: `npm install && npx grunt` (watcher: `npx grunt watch`).
- Link checks (optional): `bundle exec htmlproofer ./_site`.

## Coding Style & Naming Conventions
- Markdown/HTML/Liquid: 2-space indentation; wrap lines thoughtfully; use meaningful headings.
- Posts: `YYYY-MM-DD-struggle-N.markdown` under `_posts/`; keep metadata accurate and localized titles where appropriate.
- Images: place under `img/` with clear folders (e.g., `img/struggle/30/…`) and reference using absolute paths (`/img/...`).
- Styles: edit `less/` sources; do not hand-edit generated `css/*.css`; run Grunt to compile/minify.

## Testing Guidelines
- No unit tests; builds must pass locally: `bundle exec jekyll build` (or `script/cibuild`).
- Before opening a PR, verify pages render and links/images resolve; run optional `htmlproofer` for external link validation.

## Commit & Pull Request Guidelines
- Commits: prefer Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, `ci:`). Keep messages concise and scoped.
- PRs: include a clear description, linked issues, and screenshots/GIFs for visual changes. One logical change per PR.
- CI/Deploy: pushes to `master` trigger Travis (`.travis.yml`) which runs `script/cibuild` and deploys `_site` to `kodevops/kodevops.github.io`. Keep secrets (e.g., `GITHUB_TOKEN`) out of commits.

## Security & Configuration Tips
- Do not edit `CNAME` unless changing the domain. Review `_config.yml` for navigation/SNS updates.
- Never commit credentials; use CI secrets. Large images should be optimized before adding.

