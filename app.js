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
          signalThemes.map((theme) => `${theme.text} (${theme.count} reviews))`)
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
        `${Math.round(questionShare * 100)}%of these posts are written as questions or follow-up requests, so many users were still trying to resolve the issue when they posted.`
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
    entries.forEach(([