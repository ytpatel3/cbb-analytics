# The Impact of Advanced Efficiency Metrics on NCAA Division I Basketball Success

A data visualization project built for DS 4200. Five visualizations, three static
(Matplotlib) and two interactive (Altair and D3.js v7), to examine how
BARTHAG, ADJOE, ADJDE, WAB, and shooting metrics relate to NCAA Tournament outcomes
across 3,885 team-seasons from 2013–2024.

**Live site:** `https://<your-github-username>.github.io/<repo-name>/`

---

## Data Source

Kaggle: [College Basketball Dataset](https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset?select=cbb.csv)
* Originally sourced from [barttorvik.com](https://barttorvik.com).
* Covers NCAA Division I, seasons 2013–2019 and 2021–2024 (2020 omitted since tournament was canceled).

### References
1. [Predicting the Unpredictable: Predicting the March Madness Champion Using Statistical Modeling by Jack Sweeney (2025).](https://digitalcommons.bryant.edu/cgi/viewcontent.cgi?article=1010&context=honors_cis)
2. [Seed Distribution and Upset Probabilities in the NCAA Men’s Basketball Tournament by S. H. Jacobson, J. G. King, & E. C. Sewell (2011).](https://bracketodds.cs.illinois.edu/2011%20Omega.pdf)

---

## Visualizations

| # | Type | Tool | Description |
|---|------|------|-------------|
| 1 | Static | Matplotlib | Box plot: BARTHAG distribution by major conference |
| 2 | Static | Matplotlib | Radar chart: performance profiles of champions vs. runners-up |
| 3 | Static | Matplotlib | Multi-faceted scatter: WAB vs. ADJOE, 2P_O, 3P_O |
| 4 | Interactive | Altair | Efficiency scatter plot: (ADJOE vs. ADJDE) with season dropdown and legend click |
| 5 | Interactive | D3.js | Stacked bar chart: tournament outcome distribution by efficiency tier, with metric dropdown and click-to-highlight |

### 3 Interaction Functions

| Interaction | Visualization(s) |
|-------------|-----------------|
| Hover tooltip | Viz 4, Viz 5 |
| Dropdown filter | Viz 4 (season), Viz 5 (metric tier) |
| Click to highlight / isolate | Viz 4 (legend click), Viz 5 (segment click) |

---
