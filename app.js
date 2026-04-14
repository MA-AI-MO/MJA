(function () {
  const datasets = {
    copart: window.COPART_REVIEWS_DATA,
    iaa: window.IAA_REVIEWS_DATA,
  };
  const tiersPayload = window.COPART_TIERS_DATA;
  const businessConfig = {
    copart: {
      title: "Copart Web Sentiment Analysis Tool",
      logoSrc: "assets/copart-logo.svg",
      logoAlt: "Copart logo",
      csvPrefix: "copart",
    },
    iaa: {
      title: "IAA Web Sentiment Analysis Tool",
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

  function countByMap(rows, field) {
    const map = new Map();
    rows.forEach((row) => {
      const key = row[field] || "Unspecified";
      map.set(key, (map.get(key) || 0) + 1);
    });
    return map;
  }

  function countBy(rows, field) {
    return sortEntries(Array.from(countByMap(rows, field).entries()));
  }

  function formatDate(value) {
    if (!value) return "Unknown date";
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value;
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toISOString().slice(0, 10);
  }

  function getReviewYear(row) {
    return String(row.review_date || "").slice(0, 4);
  }

  function getReviewMonth(row) {
    return String(row.review_date || "").slice(5, 7);
  }

  function wordCount(text) {
    return (String(text || "").match(/[a-z0-9']+/gi) || []).length;
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

  const SUMMARY_STOPWORDS = new Set([
    "about", "after", "again", "against", "almost", "also", "although", "always", "among",
    "another", "anyone", "anything", "around", "because", "before", "being", "between",
    "both", "buyer", "buyers", "cannot", "car", "cars", "case", "cases", "company",
    "could", "customer", "customers", "details", "does", "doesnt", "dont", "during",
    "each", "even", "every", "everything", "from", "have", "having", "help", "helped",
    "here", "into", "issue", "issues", "just", "kind", "know", "made", "make", "many",
    "maybe", "more", "most", "much", "need", "never", "nothing", "only", "other",
    "people", "pickup", "please", "problem", "problems", "really", "review", "reviews",
    "same", "seller", "sellers", "should", "since", "some", "something", "still", "such",
    "than", "that", "their", "them", "then", "there", "these", "they", "thing", "think",
    "this", "those", "through", "time", "times", "title", "vehicle", "vehicles", "very",
    "want", "went", "were", "what", "when", "where", "which", "while", "with", "within",
    "would", "your", "yard", "auction", "auctions", "copart", "iaa", "iaai", "insurance",
    "auto",
  ]);

  const SIGNAL_THEMES = [
    {
      key: "support_followup",
      minHits: 2,
      words: ["callback", "call back", "called", "phone", "email", "response", "respond", "follow up", "follow-up", "contact"],
      negativeText: "slow follow-up, missed callbacks, and repeated contact attempts before anyone responds",
      positiveText: "follow-up timing, who responds, and which contact channel actually works",
    },
    {
      key: "support_quality",
      minHits: 2,
      words: ["support", "customer service", "staff", "agent", "representative", "manager", "rude", "helpful", "unhelpful"],
      negativeText: "rude, dismissive, or inconsistent support interactions that leave the case unresolved",
      positiveText: "support quality, agent helpfulness, and whether staff resolve the issue clearly",
    },
    {
      key: "fees_billing",
      minHits: 2,
      words: ["fee", "fees", "charge", "charged", "billing", "deposit", "refund", "payment", "storage", "tow"],
      negativeText: "unexpected charges, deposit holds, refund delays, and billing disputes",
      positiveText: "fee structure, deposits, refunds, and how charges are explained",
    },
    {
      key: "access_verification",
      minHits: 2,
      words: ["login", "log in", "account", "password", "verify", "verification", "upload", "license", "id", "driver"],
      negativeText: "login failures, account blocks, and ID or document upload problems that stop people from bidding",
      positiveText: "account setup, verification, and document upload steps needed to use the platform",
    },
    {
      key: "vehicle_disclosure",
      minHits: 2,
      words: ["damage", "damaged", "photo", "photos", "picture", "pictures", "engine", "airbag", "odometer", "disclose", "disclosed", "condition"],
      negativeText: "damage, condition, and disclosure issues that buyers feel were missed or not shown clearly",
      positiveText: "how people inspect listings, read photos, and judge vehicle condition before bidding",
    },
    {
      key: "pickup_release",
      minHits: 2,
      words: ["pickup", "pick up", "release", "yard", "appointment", "delivery", "transport", "storage", "schedule", "scheduling"],
      negativeText: "pickup delays, release problems, and yard scheduling issues after the sale",
      positiveText: "pickup timing, storage rules, release steps, and transport scheduling",
    },
    {
      key: "documents_title",
      minHits: 2,
      words: ["title", "poa", "paperwork", "document", "documents", "registration", "ownership", "bill of sale"],
      negativeText: "title, POA, and paperwork delays that slow down transfer or release",
      positiveText: "title transfer, POA requirements, and the paperwork needed after purchase",
    },
    {
      key: "bidding_rules",
      minHits: 2,
      words: ["bid", "bidding", "member", "membership", "dealer", "license", "auction"],
      negativeText: "membership, dealer-license, and bidding-rule confusion that blocks participation",
      positiveText: "how bidding works, membership requirements, and whether a dealer license is needed",
    },
  ];

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

  function toSummaryText(values, emptyText) {
    if (!values || !values.length) return emptyText;
    if (values.length <= 3) return values.join(", ");
    return `${values.slice(0, 3).join(", ")} (+${values.length - 3} more)`;
  }

  function naturalJoin(items) {
    if (!items.length) return "";
    if (items.length === 1) return items[0];
    if (items.length === 2) return `${items[0]} and ${items[1]}`;
    return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
  }

  function formatChangeText(currentCount, previousCount) {
    if (!previousCount) {
      return currentCount > 0 ? "new" : "0.0%";
    }
    const pct = ((currentCount - previousCount) / previousCount) * 100;
    const sign = pct > 0 ? "+" : "";
    return `${sign}${pct.toFixed(1)}%`;
  }

  function formatShare(count, total) {
    if (!total) return "0%";
    const pct = (count / total) * 100;
    return `${pct >= 10 ? pct.toFixed(0) : pct.toFixed(1)}%`;
  }

  function formatBreakdown(entries, total, limit) {
    return naturalJoin(
      entries.slice(0, limit).map(([label, count]) => `${label} (${count}, ${formatShare(count, total)})`)
    );
  }

  function tokenizeSummaryWords(text) {
    return String(text || "")
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((word) => word.length >= 4 && !SUMMARY_STOPWORDS.has(word));
  }

  function findSignalThemes(rows, sentiment) {
    return SIGNAL_THEMES.map((theme) => {
      let count = 0;
      rows.forEach((row) => {
        const haystack = [
          row.review_text,
          row.tier1,
          row.tier2,
          row.tier3,
          row.source_label,
        ]
          .join(" ")
          .toLowerCase();
        const hitCount = theme.words.reduce(
          (total, word) => total + (haystack.includes(word) ? 1 : 0),
          0
        );
        if (hitCount >= theme.minHits) count += 1;
      });

      return {
        count,
        text: sentiment === "negative" ? theme.negativeText : theme.positiveText,
      };
    })
      .filter((theme) => theme.count >= Math.max(2, Math.ceil(rows.length * 0.08)))
      .sort((a, b) => b.count - a.count);
  }

  function extractDetailedThemes(rows, limit) {
    const phraseCounts = new Map();

    rows.forEach((row) => {
      const words = tokenizeSummaryWords(row.review_text);
      const seen = new Set();

      for (let index = 0; index < words.length - 2; index += 1) {
        for (let size = 3; size <= 5 && index + size <= words.length; size += 1) {
          const phrase = words.slice(index, index + size).join(" ");
          if (phrase.length < 18 || seen.has(phrase)) continue;
          seen.add(phrase);
          phraseCounts.set(phrase, (phraseCounts.get(phrase) || 0) + 1);
        }
      }
    });

    return sortEntries(
      Array.from(phraseCounts.entries()).filter(([, count]) => count >= Math.max(2, Math.ceil(rows.length * 0.05)))
    )
      .map(([phrase]) => phrase)
      .slice(0, limit);
  }

  function pickRepresentativeReviews(rows, limit) {
    const sourceCounts = countByMap(rows, "source_website");
    const ranked = [...rows].sort((a, b) => {
      const scoreA = Math.min(wordCount(a.review_text), 90) + (sourceCounts.get(a.source_website) || 0);
      const scoreB = Math.min(wordCount(b.review_text), 90) + (sourceCounts.get(b.source_website) || 0);
      if (scoreB !== scoreA) return scoreB - scoreA;
      return formatDate(b.review_date).localeCompare(formatDate(a.review_date));
    });

    const picked = [];
    const seenSources = new Set();

    ranked.forEach((row) => {
      if (picked.length >= limit) return;
      if (seenSources.has(row.source_website)) return;
      picked.push(row);
      seenSources.add(row.source_website);
    });

    ranked.forEach((row) => {
      if (picked.length >= limit) return;
      if (picked.some((existing) => existing.id === row.id)) return;
      picked.push(row);
    });

    return picked.slice(0, limit);
  }

  function buildAiSummary(rows, scope, sentiment) {
    if (!rows.length) {
      return {
        intro: "No reviews are available for the current selection.",
        bullets: [],
      };
    }

    const scopeText = scope.replace(/^Top Tier 1:\s*/, "");
    const sourceText = naturalJoin(
      countBy(rows, "source_website")
        .slice(0, 3)
        .map(([site, count]) => `${site} (${count})`)
    );
    const sourceEntries = countBy(rows, "source_website").slice(0, 3);
    const tier2Entries = countBy(rows, "tier2");
    const tier3Entries = countBy(rows, "tier3");
    const signalThemes = findSignalThemes(rows, sentiment).slice(0, 3);
    const detailedThemes = extractDetailedThemes(rows, 3);
    const questionShare = rows.filter((row) => String(row.review_text || "").includes("?")).length / rows.length;
    const rated = rows.filter((row) => typeof row.rating === "number");
    const avgRating = rated.length
      ? (rated.reduce((sum, row) => sum + row.rating, 0) / rated.length).toFixed(2)
      : "n/a";
    const bullets = [];

    const intro = sentiment === "negative"
      ? `Across ${rows.length} reviews in ${scopeText}, the complaints are concentrated in a few repeat patterns rather than scattered one-off issues.`
      : `Across ${rows.length} reviews in ${scopeText}, most posts fall into a few repeat discussion themes, practical questions, or process-related experiences.`;

    if (tier3Entries.length > 1) {
      bullets.push(
        `${sentiment === "negative" ? "The biggest complaint clusters are" : "The biggest discussion clusters are"} ${formatBreakdown(tier3Entries, rows.length, 3)}.`
      );
    } else if (tier2Entries.length > 1) {
      bullets.push(`Most of the volume in this selection sits in ${formatBreakdown(tier2Entries, rows.length, 3)}.`);
    }

    if (signalThemes.length) {
      bullets.push(
        `${sentiment === "negative" ? "Across the review text, people most often describe" : "Across the review text, people most often discuss"} ${naturalJoin(
          signalThemes.map((theme) => `${theme.text} (${theme.count} reviews)`)
        )}.`
      );
    } else if (detailedThemes.length) {
      bullets.push(
        `${sentiment === "negative" ? "Repeated review language points to" : "Repeated review language focuses on"} ${naturalJoin(detailedThemes)}.`
      );
    }

    if (sourceEntries.length) {
      bullets.push(
        `${sentiment === "negative" ? "Most of this complaint volume comes from" : "Most of this discussion volume comes from"} ${sourceText}.`
      );
    }

    if (questionShare >= 0.2) {
      bullets.push(
        `${Math.round(questionShare * 100)}% of these posts are written as questions or follow-up requests, so many users were still trying to resolve the issue when they posted.`
      );
    } else if (avgRating !== "n/a") {
      bullets.push(
        `${sentiment === "negative" ? "The average rating in this selection is" : "The average rating across this selection is"} ${avgRating}.`
      );
    }

    return {
      intro,
      bullets: bullets.slice(0, 4),
    };
  }

  class CheckboxMultiSelect {
    constructor(container, config) {
      this.container = container;
      this.config = config;
      this.options = [];
      this.selected = [];
      this.onChange = null;
      this.handleDocumentClick = (event) => {
        if (!this.container.contains(event.target)) this.close();
      };
      document.addEventListener("click", this.handleDocumentClick);
      this.build();
    }

    build() {
      this.container.innerHTML = "";
      this.container.classList.add("multi-select");

      this.trigger = document.createElement("button");
      this.trigger.type = "button";
      this.trigger.className = "multi-select-trigger";
      this.trigger.setAttribute("aria-expanded", "false");

      this.summaryNode = document.createElement("span");
      this.summaryNode.className = "multi-select-summary";

      this.chevronNode = document.createElement("span");
      this.chevronNode.className = "multi-select-chevron";
      this.chevronNode.textContent = "v";

      this.trigger.appendChild(this.summaryNode);
      this.trigger.appendChild(this.chevronNode);

      this.menu = document.createElement("div");
      this.menu.className = "multi-select-menu";

      this.actions = document.createElement("div");
      this.actions.className = "multi-select-actions";

      this.selectAllBtn = document.createElement("button");
      this.selectAllBtn.type = "button";
      this.selectAllBtn.className = "multi-select-action";
      this.selectAllBtn.textContent = "Select all";

      this.clearAllBtn = document.createElement("button");
      this.clearAllBtn.type = "button";
      this.clearAllBtn.className = "multi-select-action";
      this.clearAllBtn.textContent = "Unselect all";

      this.actions.appendChild(this.selectAllBtn);
      this.actions.appendChild(this.clearAllBtn);

      this.optionsWrap = document.createElement("div");
      this.optionsWrap.className = "multi-select-options";

      this.menu.appendChild(this.actions);
      this.menu.appendChild(this.optionsWrap);
      this.container.appendChild(this.trigger);
      this.container.appendChild(this.menu);

      this.trigger.addEventListener("click", (event) => {
        event.stopPropagation();
        this.toggle();
      });

      this.selectAllBtn.addEventListener("click", () => {
        this.selected = [...this.options];
        this.renderOptions();
        this.renderSummary();
        if (this.onChange) this.onChange([...this.selected]);
      });

      this.clearAllBtn.addEventListener("click", () => {
        this.selected = [];
        this.renderOptions();
        this.renderSummary();
        if (this.onChange) this.onChange([]);
      });
    }

    setOnChange(callback) {
      this.onChange = callback;
    }

    setOptions(options, selectedValues) {
      const validSelected = new Set(options);
      this.options = [...options];
      this.selected = (selectedValues || []).filter((value) => validSelected.has(value));
      this.renderOptions();
      this.renderSummary();
    }

    renderOptions() {
      this.optionsWrap.innerHTML = "";

      if (!this.options.length) {
        const empty = document.createElement("div");
        empty.className = "multi-select-empty";
        empty.textContent = "No options available";
        this.optionsWrap.appendChild(empty);
        return;
      }

      const selectedSet = new Set(this.selected);
      this.options.forEach((value) => {
        const option = document.createElement("label");
        option.className = "multi-select-option";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = selectedSet.has(value);

        const text = document.createElement("span");
        text.textContent = this.config.labelFor ? this.config.labelFor(value) : value;

        checkbox.addEventListener("change", () => {
          const next = new Set(this.selected);
          if (checkbox.checked) next.add(value);
          else next.delete(value);
          this.selected = this.options.filter((optionValue) => next.has(optionValue));
          this.renderSummary();
          if (this.onChange) this.onChange([...this.selected]);
        });

        option.appendChild(checkbox);
        option.appendChild(text);
        this.optionsWrap.appendChild(option);
      });
    }

    renderSummary() {
      const values = this.selected.map((value) => (this.config.labelFor ? this.config.labelFor(value) : value));
      this.summaryNode.textContent = toSummaryText(values, this.config.emptyText);
    }

    open() {
      this.container.classList.add("is-open");
      this.trigger.setAttribute("aria-expanded", "true");
    }

    close() {
      this.container.classList.remove("is-open");
      this.trigger.setAttribute("aria-expanded", "false");
    }

    toggle() {
      if (this.container.classList.contains("is-open")) this.close();
      else this.open();
    }
  }

  function renderBars(container, entries, options) {
    const { selectedLabel, onClick, compareMap, compareYear } = options;
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

      const main = document.createElement("div");
      main.className = "bar-main";

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

      main.appendChild(labelNode);
      main.appendChild(track);
      main.appendChild(valueNode);
      button.appendChild(main);

      if (compareMap && compareYear) {
        const previousCount = compareMap.get(label) || 0;
        const yoy = document.createElement("div");
        yoy.className = "bar-yoy";
        yoy.textContent = `YoY vs ${compareYear}: ${previousCount} last year | ${formatChangeText(count, previousCount)}`;
        button.appendChild(yoy);
      }

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
      this.initFilters();
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
      this.aiSummary = this.root.querySelector(".ai-summary");
    }

    initFilters() {
      this.websiteDropdown = new CheckboxMultiSelect(this.websiteFilter, {
        emptyText: "All websites",
      });
      this.yearDropdown = new CheckboxMultiSelect(this.yearFilter, {
        emptyText: "All years",
      });
      this.monthDropdown = new CheckboxMultiSelect(this.monthFilter, {
        emptyText: "All months",
        labelFor: (month) => MONTH_NAMES[month] || month,
      });

      this.websiteDropdown.setOnChange((values) => {
        this.state.websites = values;
        this.populateWebsiteOptions();
        this.populateYearOptions();
        this.populateMonthOptions();
        this.render();
      });

      this.yearDropdown.setOnChange((values) => {
        this.state.years = values;
        this.populateYearOptions();
        this.populateMonthOptions();
        this.render();
      });

      this.monthDropdown.setOnChange((values) => {
        this.state.months = values;
        this.populateMonthOptions();
        this.render();
      });
    }

    bindEvents() {
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
        rows = rows.filter((r) => yearSet.has(getReviewYear(r)));
      }

      if (this.state.months.length) {
        const monthSet = new Set(this.state.months);
        rows = rows.filter((r) => monthSet.has(getReviewMonth(r)));
      }

      return rows;
    }

    getPreviousYearRows() {
      if (this.state.years.length !== 1) return null;

      const selectedYear = Number(this.state.years[0]);
      if (!Number.isFinite(selectedYear) || selectedYear <= 0) return null;

      let rows = this.getSentimentRows();
      if (this.state.websites.length) {
        const websiteSet = new Set(this.state.websites);
        rows = rows.filter((row) => websiteSet.has(row.source_website));
      }

      const previousYear = String(selectedYear - 1);
      rows = rows.filter((row) => getReviewYear(row) === previousYear);

      if (this.state.months.length) {
        const monthSet = new Set(this.state.months);
        rows = rows.filter((row) => monthSet.has(getReviewMonth(row)));
      }

      return rows;
    }

    getComparisonYear() {
      if (this.state.years.length !== 1) return null;
      const selectedYear = Number(this.state.years[0]);
      if (!Number.isFinite(selectedYear) || selectedYear <= 0) return null;
      return String(selectedYear - 1);
    }

    getSelectionRows() {
      let rows = this.getFilteredRows();
      if (this.state.tier1) rows = rows.filter((r) => r.tier1 === this.state.tier1);
      if (this.state.tier2) rows = rows.filter((r) => r.tier2 === this.state.tier2);
      if (this.state.tier3) rows = rows.filter((r) => r.tier3 === this.state.tier3);
      return rows;
    }

    getScopedSummaryRows() {
      const filteredRows = this.getFilteredRows();
      let rows = this.getSelectionRows();
      let scope = this.state.tier3 || this.state.tier2 || this.state.tier1 || "All tiers";

      if (!this.state.tier1 && !this.state.tier2 && !this.state.tier3) {
        const topTier1 = countBy(filteredRows, "tier1")[0];
        if (topTier1) {
          rows = filteredRows.filter((row) => row.tier1 === topTier1[0]);
          scope = `Top Tier 1: ${topTier1[0]}`;
        }
      }

      return { filteredRows, rows, scope };
    }

    retainValidValues(values, allowedValues) {
      const allowed = new Set(allowedValues);
      return (values || []).filter((value) => allowed.has(value));
    }

    getWebsiteValues() {
      return Array.from(new Set(this.getSentimentRows().map((r) => r.source_website))).sort();
    }

    populateWebsiteOptions() {
      const sites = this.getWebsiteValues();
      this.state.websites = this.retainValidValues(this.state.websites, sites);
      this.websiteDropdown.setOptions(sites, this.state.websites);
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
            .map((r) => getReviewYear(r))
            .filter((y) => /^\d{4}$/.test(y) && y !== "1970")
        )
      ).sort((a, b) => b.localeCompare(a));
    }

    populateYearOptions() {
      const years = this.getYearValues();
      this.state.years = this.retainValidValues(this.state.years, years);
      this.yearDropdown.setOptions(years, this.state.years);
    }

    getMonthValues() {
      let rows = this.getDateOptionRows();
      if (this.state.years.length) {
        const yearSet = new Set(this.state.years);
        rows = rows.filter((r) => yearSet.has(getReviewYear(r)));
      }

      return Array.from(
        new Set(
          rows
            .map((r) => getReviewMonth(r))
            .filter((m) => /^\d{2}$/.test(m) && m >= "01" && m <= "12")
        )
      ).sort((a, b) => a.localeCompare(b));
    }

    populateMonthOptions() {
      const months = this.getMonthValues();
      this.state.months = this.retainValidValues(this.state.months, months);
      this.monthDropdown.setOptions(months, this.state.months);
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
      const previousYearRows = this.getPreviousYearRows();

      this.renderTier1(filtered, previousYearRows);
      this.renderTier2(filtered, previousYearRows);
      this.renderTier3(filtered, previousYearRows);
      this.renderTopTopics(filtered);
      this.renderWebsiteByTier(filtered);
      this.renderSelectionSummary();
    }

    renderTier1(filtered, previousYearRows) {
      const entries = countBy(filtered, "tier1");
      const compareMap = previousYearRows ? countByMap(previousYearRows, "tier1") : null;
      renderBars(this.tier1Chart, entries, {
        selectedLabel: this.state.tier1,
        compareMap,
        compareYear: this.getComparisonYear(),
        onClick: (label) => {
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
        },
      });
    }

    renderTier2(filtered, previousYearRows) {
      if (!this.state.tier1) {
        this.tier2Card.classList.add("is-hidden");
        return;
      }

      this.tier2Card.classList.remove("is-hidden");
      this.selTier1Label.textContent = this.state.tier1;

      const tier1Rows = filtered.filter((r) => r.tier1 === this.state.tier1);
      const entries = countBy(tier1Rows, "tier2");
      const previousTier1Rows = previousYearRows
        ? previousYearRows.filter((row) => row.tier1 === this.state.tier1)
        : null;
      const compareMap = previousTier1Rows ? countByMap(previousTier1Rows, "tier2") : null;
      renderBars(this.tier2Chart, entries, {
        selectedLabel: this.state.tier2,
        compareMap,
        compareYear: this.getComparisonYear(),
        onClick: (label) => {
          if (this.state.tier2 === label) {
            this.state.tier2 = null;
            this.state.tier3 = null;
          } else {
            this.state.tier2 = label;
            this.state.tier3 = null;
          }
          this.render();
        },
      });
    }

    renderTier3(filtered, previousYearRows) {
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
      const previousTier2Rows = previousYearRows
        ? previousYearRows.filter(
            (row) => row.tier1 === this.state.tier1 && row.tier2 === this.state.tier2
          )
        : null;
      const compareMap = previousTier2Rows ? countByMap(previousTier2Rows, "tier3") : null;
      renderBars(this.tier3Chart, entries, {
        selectedLabel: this.state.tier3,
        compareMap,
        compareYear: this.getComparisonYear(),
        onClick: (label) => {
          this.state.tier3 = this.state.tier3 === label ? null : label;
          this.render();
        },
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
      const { rows, scope } = this.getScopedSummaryRows();

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

      this.aiSummary.innerHTML = "";
      const aiSummary = buildAiSummary(rows, scope, this.sentiment);
      const aiParagraph = document.createElement("p");
      aiParagraph.textContent = aiSummary.intro;
      this.aiSummary.appendChild(aiParagraph);

      if (aiSummary.bullets.length) {
        const aiList = document.createElement("ul");
        aiList.className = "ai-summary-list";
        aiSummary.bullets.forEach((text) => {
          const li = document.createElement("li");
          li.textContent = text;
          aiList.appendChild(li);
        });
        this.aiSummary.appendChild(aiList);
      }

      this.topReviews.innerHTML = "";
      const representativeRows = pickRepresentativeReviews(rows, 3);
      if (!representativeRows.length) {
        const li = document.createElement("li");
        li.textContent = "No reviews in current selection.";
        this.topReviews.appendChild(li);
        return;
      }

      representativeRows.forEach((row) => {
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


