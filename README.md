# MAY Guide Navigator

A simple viewer for the Manulife Assist You (MAY) guide: part buttons, contents, full-text search and a list of all questions.

## Files
- `index.html` – the viewer (no build step)
- `guide.pdf` – the guide itself
- `data.json` – contents and question list, generated from the PDF
- `build_data.py` – generates `data.json`
- `.github/workflows/build-data.yml` – regenerates `data.json` automatically when `guide.pdf` changes

## Set up
1. Create a repository and upload all files (keep the folder `.github/workflows`).
2. Settings → Pages → Deploy from a branch → `main` / root.
3. Open the link GitHub gives you.

## Update the guide
Replace `guide.pdf` (same file name) and commit. The workflow rebuilds `data.json` in about a minute; refresh the page.
To rebuild by hand: `pip install pdfplumber && python build_data.py`

## Assumptions
The script reads the guide's formatting: bold "Q123 …" question lines, bold numbered topic headings, and a "MAY Part X – Name" page header. If a future edition changes these, check `data.json` after the build (the script prints counts).

## Privacy
GitHub Pages sites are public to anyone with the link, even if the repository is private (except on GitHub Enterprise Cloud with private Pages). Confirm that publishing this internal guide is allowed before using it.
