/**
 * Viz 5 — Tournament Outcome Distribution by Efficiency Tier
 * D3 v7 stacked bar chart
 *
 * Interactions:
 *   1. Dropdown — switch the tiering metric (BARTHAG / ADJOE / ADJDE)
 *   2. Hover tooltip — exact count and percentage per segment
 *   3. Click segment — highlight that postseason round across all tiers
 */

(function () {
  "use strict";

  /* ── Design tokens ─────────────────────────────────────────────────────── */
  const BG     = "#0c1420";
  const CARD   = "#111d2e";
  const BORDER = "#1e3050";
  const TEXT   = "#dce3ee";
  const MUTED  = "#7a90aa";
  const ACCENT = "#d4890a";

  const ROUND_ORDER = [
    "No Tournament", "R68", "R64", "R32", "S16", "E8", "F4", "2ND", "Champions",
  ];
  const ROUND_COLORS = {
    "No Tournament": "#2d3f55",
    "R68":           "#445e7a",
    "R64":           "#5b7ea0",
    "R32":           "#6096c4",
    "S16":           "#3cb87a",
    "E8":            "#d4890a",
    "F4":            "#e06b1a",
    "2ND":           "#c03a2b",
    "Champions":     "#f0c040",
  };

  /* ── Metric options available in the dropdown ───────────────────────────── */
  const METRICS = [
    { value: "BARTHAG_TIER", label: "Power Rating (BARTHAG)" },
    { value: "ADJOE_TIER",   label: "Adj. Offensive Efficiency (ADJOE)" },
    { value: "ADJDE_TIER",   label: "Adj. Defensive Efficiency (ADJDE)" },
  ];

  const TIER_LABELS = ["Tier 1\n(Weakest)", "Tier 2", "Tier 3", "Tier 4", "Tier 5\n(Strongest)"];
  const TIER_KEYS   = ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"];

  /* ── Layout ─────────────────────────────────────────────────────────────── */
  const MARGIN = { top: 30, right: 24, bottom: 90, left: 60 };
  const W      = 760;
  const H      = 440;
  const IW     = W - MARGIN.left - MARGIN.right;
  const IH     = H - MARGIN.top  - MARGIN.bottom;

  /* ── State ───────────────────────────────────────────────────────────────── */
  let allData       = null;
  let selectedRound = null;   // for click-to-highlight

  /* ── DOM references ─────────────────────────────────────────────────────── */
  const wrapper = d3.select("#viz5-chart");

  /* ── Tooltip ─────────────────────────────────────────────────────────────── */
  const tooltip = d3.select("body")
    .append("div")
    .attr("id", "d3-tooltip")
    .style("position", "absolute")
    .style("background", CARD)
    .style("border", `1px solid ${BORDER}`)
    .style("border-radius", "6px")
    .style("padding", "10px 14px")
    .style("color", TEXT)
    .style("font-size", "12px")
    .style("line-height", "1.6")
    .style("pointer-events", "none")
    .style("opacity", 0)
    .style("z-index", 9999)
    .style("max-width", "200px");

  /* ── Dropdown control ───────────────────────────────────────────────────── */
  const controlRow = wrapper.append("div")
    .style("display", "flex")
    .style("align-items", "center")
    .style("gap", "10px")
    .style("margin-bottom", "14px");

  controlRow.append("label")
    .attr("for", "d3-metric-select")
    .style("color", TEXT)
    .style("font-size", "13px")
    .style("font-family", "IBM Plex Sans, sans-serif")
    .text("Tier metric:");

  const select = controlRow.append("select")
    .attr("id", "d3-metric-select")
    .style("background", CARD)
    .style("color", TEXT)
    .style("border", `1px solid ${BORDER}`)
    .style("border-radius", "4px")
    .style("padding", "5px 10px")
    .style("font-size", "13px")
    .style("font-family", "IBM Plex Sans, sans-serif")
    .style("cursor", "pointer");

  METRICS.forEach(m => {
    select.append("option").attr("value", m.value).text(m.label);
  });

  controlRow.append("span")
    .style("color", MUTED)
    .style("font-size", "11.5px")
    .style("font-family", "IBM Plex Sans, sans-serif")
    .text("Click a bar segment to highlight that round across all tiers.");

  /* ── SVG scaffold ───────────────────────────────────────────────────────── */
  const svg = wrapper.append("svg")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .attr("width", "100%")
    .attr("preserveAspectRatio", "xMidYMid meet")
    .style("background", BG)
    .style("border-radius", "8px")
    .style("display", "block");

  const g = svg.append("g")
    .attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

  /* Gridlines layer (drawn first so bars appear on top) */
  const gridG = g.append("g").attr("class", "gridlines");

  /* Bars layer */
  const barsG = g.append("g").attr("class", "bars");

  /* Axes layers */
  const xAxisG = g.append("g").attr("transform", `translate(0,${IH})`);
  const yAxisG = g.append("g");

  /* Axis labels */
  const xLabel = g.append("text")
    .attr("text-anchor", "middle")
    .attr("x", IW / 2)
    .attr("y", IH + 72)
    .attr("fill", MUTED)
    .attr("font-size", 11)
    .attr("font-family", "IBM Plex Sans, sans-serif");

  g.append("text")
    .attr("text-anchor", "middle")
    .attr("transform", `rotate(-90)`)
    .attr("x", -IH / 2)
    .attr("y", -46)
    .attr("fill", MUTED)
    .attr("font-size", 11)
    .attr("font-family", "IBM Plex Sans, sans-serif")
    .text("Percentage of Teams (%)");

  /* ── Scales ──────────────────────────────────────────────────────────────── */
  const xScale = d3.scaleBand()
    .domain(TIER_KEYS)
    .range([0, IW])
    .padding(0.28);

  const yScale = d3.scaleLinear()
    .domain([0, 100])
    .range([IH, 0]);

  /* ── Legend ──────────────────────────────────────────────────────────────── */
  const legendSvg = wrapper.append("svg")
    .attr("viewBox", `0 0 ${W} 36`)
    .attr("width", "100%")
    .attr("preserveAspectRatio", "xMidYMid meet")
    .style("background", BG)
    .style("border-radius", "0 0 8px 8px")
    .style("display", "block")
    .style("margin-top", "2px");

  const legendG = legendSvg.append("g")
    .attr("transform", "translate(16, 10)");

  // Exclude R68 from the visual legend (only 44 teams, visually indistinct)
  const legendRounds = ROUND_ORDER.filter(r => r !== "R68");
  const legendItemW  = (W - 32) / legendRounds.length;

  legendRounds.forEach((r, i) => {
    const lg = legendG.append("g")
      .attr("transform", `translate(${i * legendItemW}, 0)`)
      .style("cursor", "pointer")
      .on("click", () => handleLegendClick(r));

    lg.append("rect")
      .attr("width", 13)
      .attr("height", 13)
      .attr("rx", 2)
      .attr("fill", ROUND_COLORS[r])
      .attr("class", `legend-rect-${r.replace(/\//g, "-")}`);

    lg.append("text")
      .attr("x", 17)
      .attr("y", 11)
      .attr("fill", TEXT)
      .attr("font-size", 10)
      .attr("font-family", "IBM Plex Sans, sans-serif")
      .text(r);
  });

  /* ── Data aggregation ───────────────────────────────────────────────────── */
  function aggregate(data, metricCol) {
    // For each tier (1–5), compute the count and % for each postseason round
    const result = TIER_KEYS.map(tier => {
      const tierRows = data.filter(d => d[metricCol] === tier);
      const total = tierRows.length;
      const row = { tier, _total: total };
      ROUND_ORDER.forEach(r => {
        const n = tierRows.filter(d => d["POSTSEASON"] === r).length;
        row[r]          = n;
        row[r + "_pct"] = total > 0 ? (n / total) * 100 : 0;
      });
      return row;
    });
    return result;
  }

  /* ── Render / update ─────────────────────────────────────────────────────── */
  function render(metricCol) {
    const data   = aggregate(allData, metricCol);
    const pctKeys = ROUND_ORDER.map(r => r + "_pct");

    // Stack
    const stack  = d3.stack().keys(pctKeys);
    const series = stack(data);

    // Gridlines
    gridG.selectAll("line").remove();
    [20, 40, 60, 80, 100].forEach(v => {
      gridG.append("line")
        .attr("x1", 0).attr("x2", IW)
        .attr("y1", yScale(v)).attr("y2", yScale(v))
        .attr("stroke", BORDER)
        .attr("stroke-dasharray", "4,4")
        .attr("stroke-width", 0.8);
    });

    // X axis
    xAxisG
      .call(
        d3.axisBottom(xScale)
          .tickSize(0)
          .tickFormat((d, i) => {
            const lab = TIER_LABELS[TIER_KEYS.indexOf(d)];
            return lab.replace("\n", " ");
          })
      )
      .call(ax => ax.select(".domain").attr("stroke", BORDER))
      .call(ax => ax.selectAll(".tick line").remove())
      .call(ax =>
        ax.selectAll(".tick text")
          .attr("fill", TEXT)
          .attr("font-size", 11)
          .attr("font-family", "IBM Plex Sans, sans-serif")
          .attr("dy", "1.2em")
      );

    // X sub-label (team count per tier)
    data.forEach(d => {
      const xPos = xScale(d.tier) + xScale.bandwidth() / 2;
      g.selectAll(`.tier-n-${d.tier.replace(" ", "")}`).remove();
      g.append("text")
        .attr("class", `tier-n-${d.tier.replace(" ", "")}`)
        .attr("x", xPos)
        .attr("y", IH + 44)
        .attr("text-anchor", "middle")
        .attr("fill", MUTED)
        .attr("font-size", 10)
        .attr("font-family", "IBM Plex Sans, sans-serif")
        .text(`n=${d._total}`);
    });

    // Y axis
    yAxisG
      .call(
        d3.axisLeft(yScale)
          .tickValues([0, 20, 40, 60, 80, 100])
          .tickFormat(d => d + "%")
          .tickSize(-IW)
      )
      .call(ax => ax.select(".domain").attr("stroke", BORDER))
      .call(ax =>
        ax.selectAll(".tick line")
          .attr("stroke", BORDER)
          .attr("stroke-dasharray", "4,4")
          .attr("stroke-width", 0.6)
      )
      .call(ax =>
        ax.selectAll(".tick text")
          .attr("fill", MUTED)
          .attr("font-size", 10)
          .attr("font-family", "IBM Plex Sans, sans-serif")
          .attr("dx", "-4")
      );

    // x-axis label
    const metricLabel = METRICS.find(m => m.value === metricCol)?.label || metricCol;
    xLabel.text(`Efficiency Tier — ${metricLabel}`);

    // Stacked bars
    const tierGroups = barsG
      .selectAll(".tier-series")
      .data(series, d => d.key)
      .join("g")
      .attr("class", "tier-series")
      .attr("fill", d => ROUND_COLORS[d.key.replace("_pct", "")] || "#2d3f55");

    tierGroups
      .selectAll("rect")
      .data(d => d.map(pt => ({ ...pt, roundKey: d.key.replace("_pct", "") })))
      .join(
        enter =>
          enter
            .append("rect")
            .attr("x",      d => xScale(d.data.tier))
            .attr("y",      d => yScale(d[1]))
            .attr("height", d => Math.max(0, yScale(d[0]) - yScale(d[1])))
            .attr("width",  xScale.bandwidth())
            .attr("rx", 2)
            .attr("opacity", d => getOpacity(d.roundKey)),
        update =>
          update
            .transition()
            .duration(450)
            .ease(d3.easeCubicOut)
            .attr("x",      d => xScale(d.data.tier))
            .attr("y",      d => yScale(d[1]))
            .attr("height", d => Math.max(0, yScale(d[0]) - yScale(d[1])))
            .attr("width",  xScale.bandwidth())
            .attr("opacity", d => getOpacity(d.roundKey)),
        exit => exit.remove()
      )
      .on("mouseover", function (event, d) {
        const pct   = d.data[d.roundKey + "_pct"];
        const count = d.data[d.roundKey];
        tooltip
          .style("opacity", 1)
          .html(
            `<div style="font-weight:700;color:${ACCENT};margin-bottom:5px">
               ${d.data.tier}
             </div>
             <div><span style="color:${MUTED}">Round:</span> <b>${d.roundKey}</b></div>
             <div><span style="color:${MUTED}">Teams:</span> <b>${count}</b></div>
             <div><span style="color:${MUTED}">Share:</span> <b>${pct.toFixed(1)}%</b></div>
             <div style="color:${MUTED};font-size:10px;margin-top:4px">
               Tier total: ${d.data._total} teams
             </div>`
          );
        d3.select(this).attr("opacity", 1).attr("stroke", "#ffffff44").attr("stroke-width", 1);
      })
      .on("mousemove", function (event) {
        tooltip
          .style("left",  event.pageX + 16 + "px")
          .style("top",   event.pageY - 28 + "px");
      })
      .on("mouseout", function (event, d) {
        tooltip.style("opacity", 0);
        d3.select(this)
          .attr("opacity", getOpacity(d.roundKey))
          .attr("stroke", "none");
      })
      .on("click", function (event, d) {
        // Toggle highlight
        selectedRound = selectedRound === d.roundKey ? null : d.roundKey;
        refreshOpacity();
        refreshLegendHighlight();
      });
  }

  /* ── Opacity helpers (for click-to-highlight) ───────────────────────────── */
  function getOpacity(roundKey) {
    if (!selectedRound) return 1;
    return roundKey === selectedRound ? 1 : 0.18;
  }

  function refreshOpacity() {
    barsG.selectAll("rect")
      .attr("opacity", d => getOpacity(d.roundKey));
  }

  function refreshLegendHighlight() {
    legendG.selectAll("rect")
      .attr("opacity", function () {
        const round = this.getAttribute("class")
          ?.replace("legend-rect-", "")
          ?.replace(/-/g, "/");
        if (!selectedRound) return 1;
        return round === selectedRound ? 1 : 0.25;
      });
  }

  function handleLegendClick(round) {
    selectedRound = selectedRound === round ? null : round;
    refreshOpacity();
    refreshLegendHighlight();
  }

  /* ── Load data and initialise ───────────────────────────────────────────── */
  d3.csv("data/cbb_clean.csv").then(raw => {
    // Normalise POSTSEASON: fill blanks
    raw.forEach(d => {
      if (!d.POSTSEASON || d.POSTSEASON === "NA" || d.POSTSEASON === "N/A" || d.POSTSEASON === "") {
        d.POSTSEASON = "No Tournament";
      }
      // Cast tier columns to strings for safe comparison
      ["BARTHAG_TIER", "ADJOE_TIER", "ADJDE_TIER"].forEach(col => {
        d[col] = (d[col] || "").trim();
      });
    });

    allData = raw;

    // Initial render
    render("BARTHAG_TIER");

    // Dropdown change
    select.on("change", function () {
      selectedRound = null;
      refreshLegendHighlight();
      render(this.value);
    });
  });
})();
