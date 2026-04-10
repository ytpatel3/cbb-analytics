# The Impact of Advanced Efficiency Metrics on NCAA Division I Basketball Success

A data visualization project built for CS 4460. Five visualizations — three static
(Matplotlib) and two interactive (Altair/Vega-Lite and D3.js v7) — examine how
BARTHAG, ADJOE, ADJDE, WAB, and shooting metrics relate to NCAA Tournament outcomes
across 3,885 team-seasons from 2013–2024.

**Live site:** `https://<your-github-username>.github.io/<repo-name>/`

---

## Repository Structure

```
.
├── index.html                  # Main website (GitHub Pages entry point)
├── css/
│   └── style.css               # Site-wide styles
├── js/
│   └── d3_viz.js               # D3 interactive stacked bar chart (Viz 5)
├── python/
│   └── generate_charts.py      # Generates all static PNGs and Altair JSON
├── charts/                     # Generated output — commit these files
│   ├── viz1_boxplot.png
│   ├── viz2_radar.png
│   ├── viz3_scatter_facet.png
│   └── viz4_altair.json
├── data/
│   ├── cbb.csv                 # Source data from Kaggle
│   └── cbb_clean.csv           # Cleaned version with tier columns (generated)
└── README.md
```

---

## Step 1 — Prerequisites

Install Python dependencies (once):

```bash
pip install pandas numpy matplotlib seaborn altair
```

---

## Step 2 — Generate Static Assets

Run this from the **repo root** (not from inside `python/`):

```bash
python python/generate_charts.py
```

This writes four files into `charts/` and one cleaned CSV into `data/`:
- `charts/viz1_boxplot.png`
- `charts/viz2_radar.png`
- `charts/viz3_scatter_facet.png`
- `charts/viz4_altair.json`
- `data/cbb_clean.csv`

You must regenerate these any time you change the Python script and commit the output files.

---

## Step 3 — Preview Locally

Because the site loads files via `fetch()` and `d3.csv()`, you need a local HTTP server
(opening `index.html` directly as a `file://` URL will fail for those requests).

```bash
# From the repo root — any of the following work:
python -m http.server 8000
# then open http://localhost:8000 in your browser
```

---

## Step 4 — Initialize a Git Repository

If this folder is not yet a Git repo:

```bash
# Navigate to the project folder
cd path/to/cbb-analytics

# Initialize Git
git init

# Set the default branch name to 'main'
git branch -M main

# Stage everything
git add .

# Initial commit
git commit -m "Initial commit: site, charts, and data"
```

---

## Step 5 — Create a GitHub Repository and Push

1. Go to [github.com/new](https://github.com/new).
2. Name your repo (e.g., `cbb-analytics`). Keep it **public**.
3. Do **not** initialize with a README, .gitignore, or license — your local repo already has files.
4. Copy the remote URL shown on the page (HTTPS form: `https://github.com/<username>/<repo>.git`).

```bash
# Add the remote
git remote add origin https://github.com/<your-username>/<repo-name>.git

# Push to GitHub
git push -u origin main
```

---

## Step 6 — Enable GitHub Pages

1. On GitHub, go to your repo → **Settings** → **Pages** (left sidebar).
2. Under **Build and deployment**, set:
   - **Source:** `Deploy from a branch`
   - **Branch:** `main`
   - **Folder:** `/ (root)`
3. Click **Save**.
4. After ~60 seconds, your site will be live at:
   ```
   https://<your-github-username>.github.io/<repo-name>/
   ```
   GitHub will show the URL in the Pages settings panel once it deploys.

---

## Step 7 — Updating the Site

Whenever you make changes (e.g., edit a chart, update a paragraph):

```bash
# If you changed the Python script, regenerate assets first:
python python/generate_charts.py

# Stage and commit all changes
git add .
git commit -m "Update: <brief description of what changed>"

# Push — GitHub Pages redeploys automatically within ~60 seconds
git push
```

---

## Visualizations

| # | Type | Tool | Description |
|---|------|------|-------------|
| 1 | Static | Matplotlib | Box plot — BARTHAG distribution by major conference |
| 2 | Static | Matplotlib | Radar chart — performance profiles of champions vs. runners-up |
| 3 | Static | Matplotlib | Multi-faceted scatter — WAB vs. ADJOE, 2P_O, 3P_O |
| 4 | Interactive | Altair / Vega-Lite | Efficiency scatter (ADJOE vs. ADJDE) with season dropdown and legend click |
| 5 | Interactive | D3.js v7 | Stacked bar — tournament outcome distribution by efficiency tier, with metric dropdown and click-to-highlight |

### Interaction Types

| Interaction | Visualization(s) |
|-------------|-----------------|
| Hover tooltip | Viz 4, Viz 5 |
| Dropdown filter | Viz 4 (season), Viz 5 (metric tier) |
| Click to highlight / isolate | Viz 4 (legend click), Viz 5 (segment click) |

---

## Data Source

Kaggle — [College Basketball Dataset](https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset?select=cbb.csv)
Originally sourced from [barttorvik.com](https://barttorvik.com).
Covers NCAA Division I, seasons 2013–2019 and 2021–2024 (2020 omitted — tournament canceled).
