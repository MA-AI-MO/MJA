(function () {
  const datasets = {
    copart: window.COPART_REVIEWS_DATA,
    iaa: window.IAA_REVIEWS_DATA,
  };
  const tiersPayload = window.COPART_TIERS_DATA;
  const businessConfig = {
    copart: {
      title: "Copart External Review Analysis Tool",
      logoSrc: "assets/copart-logo.svg",
      logoAlt: "Copart logo",
      csvPrefix: "copart",
    },
    iaa: {
      title: "IAA External Review Analysis Tool",
      logoSrc: "assets/iaa-logo.png",
      logoAlt: "IAA logo",
      csvPrefix: "iaa",
    },
  };

  let activeBusiness = "copart";
  let reviewsPayload = datasets[activeBusiness];

  if (!datasets.copart || !datasets.iaa || !tiersPayload) {
    throw new Error("Missing data bundles.");
  }

  function getAllReviews() {
    return reviewsPayload?.reviews || [];
  }
  const allowedPaths = new Set(
    (tiersPayload.allowed_paths || []).map((row) => `${row.tier1}|||${row.tier2}|||${row.tier3}`)
  );

  function warnInvalidAssignments(datasetKey, payload) {
    const rows = payload?.reviews || [];
    const invalidReviews = rows.filter(
      (r) => !allowedPaths.has(`${r.tier1}|||${r.tier2}|||${r.tier3}`)
    );
    if (invalidReviews.length) {
      console.warn(`Invalid tier assignments found for ${datasetKey}:`, invalidReviews);
    }
  }
  warnInvalidAssignments("copart", datasets.copart);
  warnInvalidAssignments("iaa", datasets.iaa);

  function applyBusinessTheme() {
    const cfg = businessConfig[activeBusiness];
    document.body.dataset.business = activeBusiness;

    const logo = document.getElementById("brand-logo");
    const title = document.getElementById("app-title");
    if (logo) {
      logo.src = cfg.logoSrc;
      logo.alt = cfg.logoAlt;
    }
    if (title) title.textContent = cfg.title;
    document.title = cfg.title;

    document.querySelectorAll(".business-option").forEach((btn) => {
      const isActive = btn.dataset.business === activeBusiness;
      btn.classList.toggle("is-active", isActive);
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  }

  function renderSources() {
    const sourceList = document.getElementById("source-list");
    if (!sourceList) return;

    const urls = reviewsPayload.meta?.source_urls || [];
    sourceList.innerHTML = "";
    urls.forEach((url) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = url;
      li.appendChild(a);
      sourceList.appendChild(li);
    });
  }

  function sortEntries(entries) {
    return entries.sort((a, b) => {
      if (b[1] !== a[1]) return b[1] - a[1];
      return a[0].localeCompare(b[0]);
    });
  }

  function countBy(rows, field) {
    const map = new Map();
    rows.forEach((row) => {
      const key = row[field] || "Unspecified";
      map.set(key, (map.get(key) || 0) + 1);
    });
    return sortEntries(Array.from(map.entries()));
  }

  function formatDate(value) {
    if (!value) return "Unknown date";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toISOString().slice(0, 10);
  }

  function slugify(text) {
    return String(text || "all")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 60);
  }

  const MONTH_NAMES = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
  };

  function csvEscape(value) {
    if (value === null || value === undefined) return "";
    const str = String(value);
    return /[",\n]/.test(str) ? `"${str.replace(/"/g, '""')}"` : str;
  }

  function downloadCsv(rows, filename) {
    const headers = [
      "id",
      "review_date",
      "source_website",
      "source_label",
      "author",
      "rating",
      "sentiment",
      "tier1",
      "tier2",
      "tier3",
      "review_text",
      "source_url",
    ];

    const lines = [headers.join(",")];
    rows.forEach((row) => {
      lines.push(headers.map((h) => csvEscape(row[h])).join(","));
    });

    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  const SELECT_ALL_VALUE = "__all__";

  function toSummaryText(values, emptyText) {
    if (!values || !values.length) return emptyText;
    if (values.length <= 3) return values.join(", ");
    return `${values.slice(0, 3).join(", ")} (+${values.length - 3} more)`;
  }

  function renderBars(container, entries, selectedLabel, onClick) {
    container.innerHTML = "";

    if (!entries.length) {
      const p = document.createElement("p");
      p.className = "empty-state";
      p.textContent = "No reviews for this selection.";
      container.appendChild(p);
      return;
    }

    const max = entries[0][1] || 1;
    entries.forEach(([label, count]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "bar-row";
      if (selectedLabel === label) button.classList.add("is-selected");

      const labelNode = document.createElement("div");
      labelNode.className = "bar-label";
      labelNode.textContent = label;

      const track = document.createElement("div");
      track.className = "bar-track";

      const fill = document.createElement("div");
      fill.className = "bar-fill";
      fill.style.width = `${(count / max) * 100}%`;
      track.appendChild(fill);

      const valueNode = document.createElement("div");
      valueNode.className = "bar-count";
      valueNode.textContent = String(count);

      button.appendChild(labelNode);
      button.appendChild(track);
      button.appendChild(valueNode);

      button.addEventListener("click", () => onClick(label));
      container.appendChild(button);
    });
  }

  class SentimentPanel {
    constructor(root, sentiment) {
      this.root = root;
      this.sentiment = sentiment;
      this.state = {
        websites: [],
        years: [],
        months: [],
        tier1: null,
        tier2: null,
        tier3: null,
      };

      this.bindElements();
      this.bindEvents();
      this.populateWebsiteOptions();
      this.populateYearOptions();
      this.populateMonthOptions();
      this.render();
    }

    onDatasetChanged() {
      this.state = {
        websites: [],
        years: [],
        months: [],
        tier1: null,
        tier2: null,
        tier3: null,
      };
      this.populateWebsiteOptions();
      this.populateYearOptions();
      this.populateMonthOptions();
      this.render();
    }

    bindElements() {
      this.websiteFilter = this.root.querySelector(".website-filter");
      this.yearFilter = this.root.querySelector(".year-filter");
      this.monthFilter = this.root.querySelector(".month-filter");
      this.downloadBtn = this.root.querySelector(".download-btn");
      this.tier1Chart = this.root.querySelector(".tier1-chart");
      this.tier2Card = this.root.querySelector(".tier2-card");
      this.tier2Chart = this.root.querySelector(".tier2-chart");
      this.tier3Card = this.root.querySelector(".tier3-card");
      this.tier3Chart = this.root.querySelector(".tier3-chart");
      this.clearTier1Btn = this.root.querySelector(".clear-tier1");
      this.clearTier2Btn = this.root.querySelector(".clear-tier2");
      this.selTier1Label = this.root.querySelector(".selected-tier1-label");
      this.selTier2Label = this.root.querySelector(".selected-tier2-label");
      this.topTopics = this.root.querySelector(".top-topics");
      this.websiteTierTable = this.root.querySelector(".website-tier-table");
      this.selectionPath = this.root.querySelector(".selection-path");
      this.selectionMetrics = this.root.querySelector(".selection-metrics");
      this.topReviews = this.root.querySelector(".top-reviews");
    }

    bindEvents() {
      this.websiteFilter.addEventListener("change", () => {
        const sites = this.getWebsiteValues();
        if (!this.applyDropdownSelection("websites", this.websiteFilter.value, sites)) return;
        this.populateWebsiteOptions();
        this.populateYearOptions();
        this.populateMonthOptions();
        this.render();
      });

      this.yearFilter.addEventListener("change", () => {
        const years = this.getYearValues();
        if (!this.applyDropdownSelection("years", this.yearFilter.value, years)) return;
        this.populateYearOptions();
        this.populateMonthOptions();
        this.render();
      });

      this.monthFilter.addEventListener("change", () => {
        const months = this.getMonthValues();
        if (!this.applyDropdownSelection("months", this.monthFilter.value, months)) return;
        this.populateMonthOptions();
        this.render();
      });

      this.clearTier1Btn.addEventListener("click", () => {
        this.state.tier1 = null;
        this.state.tier2 = null;
        this.state.tier3 = null;
        this.render();
      });

      this.clearTier2Btn.addEventListener("click", () => {
        this.state.tier2 = null;
        this.state.tier3 = null;
        this.render();
      });

      this.downloadBtn.addEventListener("click", () => {
        const rows = this.getSelectionRows();
        const part = this.state.tier3 || this.state.tier2 || this.state.tier1 || "all";
        const websites = this.state.websites.length ? this.state.websites.join("-") : "all-sites";
        const years = this.state.years.length ? this.state.years.join("-") : "all-years";
        const months = this.state.months.length ? this.state.months.join("-") : "all-months";
        const prefix = businessConfig[activeBusiness].csvPrefix;
        const file = `${prefix}-${this.sentiment}-${slugify(websites)}-${slugify(years)}-${slugify(months)}-${slugify(part)}.csv`;
        downloadCsv(rows, file);
      });
    }

    getSentimentRows() {
      return getAllReviews().filter((r) => r.sentiment === this.sentiment);
    }

    getFilteredRows() {
      let rows = this.getSentimentRows();

      if (this.state.websites.length) {
        const siteSet = new Set(this.state.websites);
        rows = rows.filter((r) => siteSet.has(r.source_website));
      }

      if (this.state.years.length) {
        const yearSet = new Set(this.state.years);
        rows = rows.filter((r) => yearSet.has(String(r.review_date || "").slice(0, 4)));
      }

      if (this.state.months.length) {
        const monthSet = new Set(this.state.months);
        rows = rows.filter((r) => monthSet.has(String(r.review_date || "").slice(5, 7)));
      }

      return rows;
    }

    getSelectionRows() {
      let rows = this.getFilteredRows();
      if (this.state.tier1) rows = rows.filter((r) => r.tier1 === this.state.tier1);
      if (this.state.tier2) rows = rows.filter((r) => r.tier2 === this.state.tier2);
      if (this.state.tier3) rows = rows.filter((r) => r.tier3 === this.state.tier3);
      return rows;
    }

    retainValidValues(values, allowedValues) {
      const allowed = new Set(allowedValues);
      return (values || []).filter((value) => allowed.has(value));
    }

    applyDropdownSelection(stateKey, selectedValue, availableValues) {
      if (!selectedValue) return false;

      if (selectedValue === SELECT_ALL_VALUE) {
        this.state[stateKey] =
          this.state[stateKey].length === availableValues.length ? [] : [...availableValues];
        return true;
      }

      if (!availableValues.includes(selectedValue)) return false;

      const next = new Set(this.state[stateKey]);
      if (next.has(selectedValue)) {
        next.delete(selectedValue);
      } else {
        next.add(selectedValue);
      }
      this.state[stateKey] = availableValues.filter((value) => next.has(value));
      return true;
    }

    populateSingleDropdown(selectEl, selectedValues, allValues, emptyText, selectAllText, toLabel) {
      const labelFor = toLabel || ((v) => v);
      const selectedSet = new Set(selectedValues);
      const allSelected = allValues.length > 0 && selectedValues.length === allValues.length;

      selectEl.innerHTML = "";

      const summaryOption = document.createElement("option");
      summaryOption.value = "";
      summaryOption.textContent = toSummaryText(selectedValues.map((v) => labelFor(v)), emptyText);
      summaryOption.selected = true;
      selectEl.appendChild(summaryOption);

      const selectAllOption = document.createElement("option");
      selectAllOption.value = SELECT_ALL_VALUE;
      selectAllOption.textContent = allSelected ? `Clear all (${allValues.length})` : selectAllText;
      selectEl.appendChild(selectAllOption);

      allValues.forEach((value) => {
        const opt = document.createElement("option");
        opt.value = value;
        opt.textContent = `${selectedSet.has(value) ? "[x] " : ""}${labelFor(value)}`;
        selectEl.appendChild(opt);
      });

      selectEl.value = "";
    }

    getWebsiteValues() {
      return Array.from(new Set(this.getSentimentRows().map((r) => r.source_website))).sort();
    }

    populateWebsiteOptions() {
      const sites = this.getWebsiteValues();
      this.state.websites = this.retainValidValues(this.state.websites, sites);
      this.populateSingleDropdown(
        this.websiteFilter,
        this.state.websites,
        sites,
        "All websites",
        "Select all websites"
      );
    }

    getDateOptionRows() {
      let rows = this.getSentimentRows();
      if (this.state.websites.length) {
        const websiteSet = new Set(this.state.websites);
        rows = rows.filter((r) => websiteSet.has(r.source_website));
      }
      return rows;
    }

    getYearValues() {
      return Array.from(
        new Set(
          this.getDateOptionRows()
            .map((r) => String(r.review_date || "").slice(0, 4))
            .filter((y) => /^\d{4}$/.test(y) && y !== "1970")
        )
      ).sort((a, b) => b.localeCompare(a));
    }

    populateYearOptions() {
      const years = this.getYearValues();
      this.state.years = this.retainValidValues(this.state.years, years);
      this.populateSingleDropdown(this.yearFilter, this.state.years, years, "All years", "Select all years");
    }

    getMonthValues() {
      let rows = this.getDateOptionRows();
      if (this.state.years.length) {
        const yearSet = new Set(this.state.years);
        rows = rows.filter((r) => yearSet.has(String(r.review_date || "").slice(0, 4)));
      }

      return Array.from(
        new Set(
          rows
            .map((r) => String(r.review_date || "").slice(5, 7))
            .filter((m) => /^\d{2}$/.test(m) && m >= "01" && m <= "12")
        )
      ).sort((a, b) => a.localeCompare(b));
    }

    populateMonthOptions() {
      const months = this.getMonthValues();
      this.state.months = this.retainValidValues(this.state.months, months);
      this.populateSingleDropdown(
        this.monthFilter,
        this.state.months,
        months,
        "All months",
        "Select all months",
        (month) => MONTH_NAMES[month] || month
      );
    }

    ensureValidSelection() {
      const filtered = this.getFilteredRows();
      const hasTier1 = this.state.tier1 && filtered.some((r) => r.tier1 === this.state.tier1);
      if (!hasTier1) {
        this.state.tier1 = null;
        this.state.tier2 = null;
        this.state.tier3 = null;
        return;
      }

      const tier1Rows = filtered.filter((r) => r.tier1 === this.state.tier1);
      const hasTier2 = this.state.tier2 && tier1Rows.some((r) => r.tier2 === this.state.tier2);
      if (!hasTier2) {
        this.state.tier2 = null;
        this.state.tier3 = null;
        return;
      }

      const tier2Rows = tier1Rows.filter((r) => r.tier2 === this.state.tier2);
      const hasTier3 = this.state.tier3 && tier2Rows.some((r) => r.tier3 === this.state.tier3);
      if (!hasTier3) {
        this.state.tier3 = null;
      }
    }

    render() {
      this.ensureValidSelection();
      const filtered = this.getFilteredRows();

      this.renderTier1(filtered);
      this.renderTier2(filtered);
      this.renderTier3(filtered);
      this.renderTopTopics(filtered);
      this.renderWebsiteByTier(filtered);
      this.renderSelectionSummary();
    }

    renderTier1(filtered) {
      const entries = countBy(filtered, "tier1");
      renderBars(this.tier1Chart, entries, this.state.tier1, (label) => {
        if (this.state.tier1 === label) {
          this.state.tier1 = null;
          this.state.tier2 = null;
          this.state.tier3 = null;
        } else {
          this.state.tier1 = label;
          this.state.tier2 = null;
          this.state.tier3 = null;
        }
        this.render();
      });
    }

    renderTier2(filtered) {
      if (!this.state.tier1) {
        this.tier2Card.classList.add("is-hidden");
        return;
      }

      this.tier2Card.classList.remove("is-hidden");
      this.selTier1Label.textContent = this.state.tier1;

      const tier1Rows = filtered.filter((r) => r.tier1 === this.state.tier1);
      const entries = countBy(tier1Rows, "tier2");
      renderBars(this.tier2Chart, entries, this.state.tier2, (label) => {
        if (this.state.tier2 === label) {
          this.state.tier2 = null;
          this.state.tier3 = null;
        } else {
          this.state.tier2 = label;
          this.state.tier3 = null;
        }
        this.render();
      });
    }

    renderTier3(filtered) {
      if (!this.state.tier1 || !this.state.tier2) {
        this.tier3Card.classList.add("is-hidden");
        return;
      }

      this.tier3Card.classList.remove("is-hidden");
      this.selTier2Label.textContent = `${this.state.tier1} -> ${this.state.tier2}`;

      const tier2Rows = filtered.filter(
        (r) => r.tier1 === this.state.tier1 && r.tier2 === this.state.tier2
      );
      const entries = countBy(tier2Rows, "tier3");
      renderBars(this.tier3Chart, entries, this.state.tier3, (label) => {
        this.state.tier3 = this.state.tier3 === label ? null : label;
        this.render();
      });
    }

    renderTopTopics(filtered) {
      const entries = countBy(filtered, "tier3").slice(0, 10);
      this.topTopics.innerHTML = "";

      if (!entries.length) {
        const li = document.createElement("li");
        li.textContent = "No topic data.";
        this.topTopics.appendChild(li);
        return;
      }

      entries.forEach(([topic, count]) => {
        const li = document.createElement("li");
        li.textContent = `${topic} (${count})`;
        this.topTopics.appendChild(li);
      });
    }

    renderWebsiteByTier(filtered) {
      this.websiteTierTable.innerHTML = "";

      let levelField = "tier1";
      let scoped = filtered;
      if (this.state.tier1 && this.state.tier2) {
        levelField = "tier3";
        scoped = filtered.filter((r) => r.tier1 === this.state.tier1 && r.tier2 === this.state.tier2);
      } else if (this.state.tier1) {
        levelField = "tier2";
        scoped = filtered.filter((r) => r.tier1 === this.state.tier1);
      }

      const byTier = new Map();
      scoped.forEach((row) => {
        const tierKey = row[levelField];
        if (!byTier.has(tierKey)) byTier.set(tierKey, []);
        byTier.get(tierKey).push(row);
      });

      const rows = Array.from(byTier.entries())
        .map(([tierName, items]) => {
          const siteCounts = countBy(items, "source_website");
          const [topSite, topCount] = siteCounts[0] || ["-", 0];
          return {
            tierName,
            topSite,
            topCount,
            total: items.length,
          };
        })
        .sort((a, b) => b.total - a.total)
        .slice(0, 10);

      if (!rows.length) {
        this.websiteTierTable.textContent = "No website data for this selection.";
        return;
      }

      const table = document.createElement("table");
      const thead = document.createElement("thead");
      thead.innerHTML = `<tr><th>${levelField.toUpperCase()}</th><th>Top Website</th><th>Count</th></tr>`;
      table.appendChild(thead);

      const tbody = document.createElement("tbody");
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.tierName}</td><td>${row.topSite}</td><td>${row.topCount}/${row.total}</td>`;
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);

      this.websiteTierTable.appendChild(table);
    }

    renderSelectionSummary() {
      const filteredRows = this.getFilteredRows();
      let rows = this.getSelectionRows();
      let scope = this.state.tier3 || this.state.tier2 || this.state.tier1 || "All tiers";

      // If nothing is selected, show examples from the top chart category (top Tier 1).
      if (!this.state.tier1 && !this.state.tier2 && !this.state.tier3) {
        const topTier1 = countBy(filteredRows, "tier1")[0];
        if (topTier1) {
          rows = filteredRows.filter((r) => r.tier1 === topTier1[0]);
          scope = `Top Tier 1: ${topTier1[0]}`;
        }
      }

      const siteText = toSummaryText(this.state.websites, "All websites");
      const yearText = toSummaryText(this.state.years, "All years");
      const monthText = this.state.months.length
        ? toSummaryText(this.state.months.map((m) => MONTH_NAMES[m] || m), "All months")
        : "All months";
      this.selectionPath.textContent = `Scope: ${scope} | Website: ${siteText} | Year: ${yearText} | Month: ${monthText}`;

      const rated = rows.filter((r) => typeof r.rating === "number");
      const avgRating = rated.length
        ? (rated.reduce((sum, r) => sum + r.rating, 0) / rated.length).toFixed(2)
        : "n/a";
      const websiteCount = new Set(rows.map((r) => r.source_website)).size;

      this.selectionMetrics.innerHTML = "";
      [
        `Reviews: ${rows.length}`,
        `Websites: ${websiteCount}`,
        `Avg rating: ${avgRating}`,
      ].forEach((text) => {
        const span = document.createElement("span");
        span.className = "metric-pill";
        span.textContent = text;
        this.selectionMetrics.appendChild(span);
      });

      const sortedReviews = [...rows].sort((a, b) => formatDate(b.review_date).localeCompare(formatDate(a.review_date)));
      this.topReviews.innerHTML = "";

      if (!sortedReviews.length) {
        const li = document.createElement("li");
        li.textContent = "No reviews in current selection.";
        this.topReviews.appendChild(li);
        return;
      }

      sortedReviews.slice(0, 5).forEach((row) => {
        const li = document.createElement("li");
        li.textContent = `${row.review_text} (${row.source_label}, ${row.author}, ${formatDate(row.review_date)})`;
        this.topReviews.appendChild(li);
      });
    }
  }

  const panels = [
    new SentimentPanel(document.getElementById("negative-panel"), "negative"),
    new SentimentPanel(document.getElementById("positive-panel"), "positive"),
  ];

  function switchBusiness(nextBusiness) {
    if (!datasets[nextBusiness] || nextBusiness === activeBusiness) return;
    activeBusiness = nextBusiness;
    reviewsPayload = datasets[activeBusiness];
    applyBusinessTheme();
    renderSources();
    panels.forEach((panel) => panel.onDatasetChanged());
  }

  document.querySelectorAll(".business-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      switchBusiness(btn.dataset.business);
    });
  });

  applyBusinessTheme();
  renderSources();
})();

