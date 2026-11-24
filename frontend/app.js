(() => {
  // DOM element selectors
  const unifiedInput = document.querySelector("#unified-input");
  const hiddenMessage = document.querySelector("#message");
  const hiddenUrl = document.querySelector("#url");
  const incidentStatus = document.querySelector("#incident-status");
  const analyzeButton = document.querySelector("#analyze");
  const analyzeBtnText = document.querySelector("#analyzeBtnText");
  const loadingIndicator = document.querySelector("#loadingIndicator");
  const formError = document.querySelector("#form-error");
  const formErrorText = document.querySelector("#form-error-text");
  const formErrorClose = document.querySelector("#form-error-close");
  const clearBtn = document.querySelector("#clearBtn");
  const pasteSampleBtn = document.querySelector("#pasteSampleBtn");
  const resetHeaderBtn = document.querySelector("#resetHeaderBtn");
  const brandLogo = document.querySelector("#brandLogo");
  const scenarioGrid = document.querySelector("#scenarioGrid");

  // Results containers
  const results = document.querySelector("#results");
  const layer1Decision = document.querySelector("#layer1-decision");
  const evidenceList = document.querySelector("#evidenceList");
  const evidenceCountBadge = document.querySelector("#evidenceCountBadge");
  const analyzeAnotherBtn = document.querySelector("#analyzeAnotherBtn");

  // Layer 3 (Technical Details) elements
  const engineStatusTag = document.querySelector("#engineStatusTag");
  const engineLimitationText = document.querySelector("#engineLimitationText");
  const technicalUrlContainer = document.querySelector("#technicalUrlContainer");
  const technicalUrlList = document.querySelector("#technicalUrlList");
  const technicalLimitationsList = document.querySelector("#technicalLimitationsList");

  // User-facing friendly verdict dictionary
  const VERDICT_MAP = {
    critical: {
      label: "Very high risk of scam",
      badgeClass: "bg-[#BA1A1A] text-white",
      icon: "warning",
      colorClass: "text-[#BA1A1A]"
    },
    high: {
      label: "Potential scam detected",
      badgeClass: "bg-[#B45309] text-white",
      icon: "crisis_alert",
      colorClass: "text-[#B45309]"
    },
    moderate: {
      label: "Suspicious signs found",
      badgeClass: "bg-[#546500] text-white",
      icon: "info",
      colorClass: "text-[#546500]"
    },
    low_indicators: {
      label: "No strong warning signs detected",
      badgeClass: "bg-[#174C38] text-white",
      icon: "verified_user",
      colorClass: "text-[#174C38]"
    }
  };

  // Safe DOM element creator (zero raw innerHTML injection)
  function createEl(tagName, className, textContent) {
    const el = document.createElement(tagName);
    if (className) el.className = className;
    if (textContent !== undefined && textContent !== null) el.textContent = textContent;
    return el;
  }

  function showError(msg) {
    if (formErrorText) formErrorText.textContent = msg;
    if (formError) formError.classList.remove("hidden");
  }

  function hideError() {
    if (formError) formError.classList.add("hidden");
  }

  if (formErrorClose) {
    formErrorClose.addEventListener("click", hideError);
  }

  // Clear workspace
  function resetWorkspace() {
    if (unifiedInput) unifiedInput.value = "";
    if (hiddenMessage) hiddenMessage.value = "";
    if (hiddenUrl) hiddenUrl.value = "";
    if (incidentStatus) incidentStatus.value = "received_only";
    hideError();
    if (results) results.hidden = true;
    if (unifiedInput) unifiedInput.focus();
  }

  if (clearBtn) clearBtn.addEventListener("click", resetWorkspace);
  if (resetHeaderBtn) resetHeaderBtn.addEventListener("click", resetWorkspace);
  if (brandLogo) brandLogo.addEventListener("click", (e) => {
    e.preventDefault();
    resetWorkspace();
  });
  if (analyzeAnotherBtn) analyzeAnotherBtn.addEventListener("click", () => {
    resetWorkspace();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // Paste clipboard
  if (pasteSampleBtn) {
    pasteSampleBtn.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (text && unifiedInput) {
          unifiedInput.value = text;
          hideError();
          unifiedInput.focus();
        }
      } catch {
        showError("Clipboard permission not granted. Please paste text directly into the box.");
      }
    });
  }

  // Quick Scenarios from demo fixtures
  const scenarios = {
    internship: {
      text: "Congratulations, you are shortlisted for an internship. Pay ₹799 as a registration fee today to confirm your seat.",
      incident: "received_only"
    },
    upipin: {
      text: "Your refund is pending. Scan the QR code and enter your UPI PIN immediately to receive the amount.",
      incident: "received_only"
    },
    shorturl: {
      text: "Please review the offer at https://bit.ly/offer.",
      incident: "received_only"
    },
    legitotp: {
      text: "Security reminder: Never share your OTP, password, or UPI PIN with anyone.",
      incident: "received_only"
    }
  };

  if (scenarioGrid) {
    scenarioGrid.querySelectorAll(".scenario-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-scenario");
        const sc = scenarios[key];
        if (sc && unifiedInput) {
          unifiedInput.value = sc.text;
          if (incidentStatus) incidentStatus.value = sc.incident;
          hideError();
          runAnalysis();
        }
      });
    });
  }

  // Keyboard shortcut Ctrl/Cmd+Enter
  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      runAnalysis();
    }
  });

  // Render Layer 1: Immediate Decision
  function renderLayer1(data) {
    layer1Decision.replaceChildren();
    const levelKey = data.assessment.level;
    const verdictInfo = VERDICT_MAP[levelKey] || VERDICT_MAP.low_indicators;

    layer1Decision.className = `rounded-2xl p-6 sm:p-7 shadow-sm transition-all duration-300 verdict-${levelKey}`;

    // Top Header: Badge + Title
    const headerRow = createEl("div", "flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#202622]/10");
    const badgeWrapper = createEl("div", "flex items-center gap-2");
    const badge = createEl("span", `inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold tracking-wide verdict-badge`);
    const icon = createEl("span", "material-symbols-outlined text-[15px]", verdictInfo.icon);
    const badgeLabel = createEl("span", "", verdictInfo.label.toUpperCase());
    badge.append(icon, badgeLabel);
    badgeWrapper.append(badge);

    const safeAuditNote = createEl("span", "text-xs text-[#404944] font-medium", "Scan completed locally");
    headerRow.append(badgeWrapper, safeAuditNote);

    // One-sentence summary explanation
    const summaryRow = createEl("div", "mt-4 flex flex-col gap-2");
    const summaryHeading = createEl("h3", "font-headline text-2xl sm:text-3xl font-semibold text-[#003523] leading-snug", data.assessment.summary);
    summaryRow.append(summaryHeading);

    if (data.assessment.uncertain) {
      const cautionText = createEl("p", "text-xs text-[#546500] font-medium flex items-center gap-1 mt-1");
      const cautionIcon = createEl("span", "material-symbols-outlined text-[15px]", "info");
      const cautionMsg = createEl("span", "", "Note: SIFT highlights patterns based on rules. A clear result never guarantees a message is completely safe. Always verify independently.");
      cautionText.append(cautionIcon, cautionMsg);
      summaryRow.append(cautionText);
    }

    // Recommended Actions section right in Layer 1
    const actionsSection = createEl("div", "mt-5 pt-4 border-t border-[#202622]/10 flex flex-col gap-2.5");
    const actionsTitle = createEl("h4", "font-bold text-sm text-[#003523] flex items-center gap-1.5");
    const actIcon = createEl("span", "material-symbols-outlined text-[18px] text-[#174C38]", "check_circle");
    const actTitleText = createEl("span", "", "What you should do:");
    actionsTitle.append(actIcon, actTitleText);
    actionsSection.append(actionsTitle);

    if (data.next_steps && data.next_steps.length > 0) {
      const actionsList = createEl("ul", "space-y-2 mt-1");
      data.next_steps.forEach((step, idx) => {
        const item = createEl("li", "flex items-start gap-2.5 text-sm text-[#202622] leading-relaxed bg-white/70 p-2.5 rounded-xl border border-[#202622]/5");
        const num = createEl("span", "w-5 h-5 rounded-full bg-[#174C38] text-white text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5", String(idx + 1));
        const textSpan = createEl("span", "font-medium", step);
        item.append(num, textSpan);
        actionsList.append(item);
      });
      actionsSection.append(actionsList);
    }

    layer1Decision.append(headerRow, summaryRow, actionsSection);
  }

  // Render Layer 2: Evidence Trail ("Why we flagged this")
  function renderLayer2(signals) {
    evidenceList.replaceChildren();
    const count = signals ? signals.length : 0;
    if (evidenceCountBadge) {
      evidenceCountBadge.textContent = `${count} ${count === 1 ? "warning sign" : "warning signs"} found`;
    }

    if (count === 0) {
      const emptyCard = createEl("div", "p-5 rounded-xl bg-white border border-[#DDD7C5] text-center flex flex-col items-center gap-1.5");
      const icon = createEl("span", "material-symbols-outlined text-2xl text-[#174C38]", "check");
      const title = createEl("h4", "font-bold text-sm text-[#003523]", "No specific scam patterns detected");
      const msg = createEl("p", "text-xs text-[#404944] max-w-md", "SIFT did not find common fraud keywords, payment traps, or known deceptive link patterns in this text.");
      emptyCard.append(icon, title, msg);
      evidenceList.append(emptyCard);
      return;
    }

    signals.forEach((sig) => {
      // Clean, vertical one-per-row card
      const card = createEl("div", "p-4 sm:p-5 rounded-xl bg-white border border-[#DDD7C5] shadow-xs flex flex-col gap-2.5");

      // What was noticed (Title)
      const topRow = createEl("div", "flex items-start justify-between gap-2");
      const titleWrap = createEl("div", "flex items-center gap-2");
      const flagIcon = createEl("span", "material-symbols-outlined text-[18px] text-[#B45309] shrink-0", "flag");
      const title = createEl("h4", "text-sm font-bold text-[#003523]", sig.reason || sig.signal_id.replace(/_/g, " "));
      titleWrap.append(flagIcon, title);
      topRow.append(titleWrap);
      card.append(topRow);

      // What part triggered it (Exact snippet)
      if (sig.evidence) {
        const snippetBox = createEl("div", "p-2.5 rounded-lg bg-[#FAF8F2] border border-[#EAEDE6] flex flex-col gap-1");
        const snippetLabel = createEl("span", "text-[10px] font-bold uppercase tracking-wider text-[#707973]", "Flagged text in message:");
        const snippetText = createEl("p", "text-xs font-semibold text-[#BA1A1A] break-words font-mono", `"${sig.evidence}"`);
        snippetBox.append(snippetLabel, snippetText);
        card.append(snippetBox);
      }

      // Actionable safety takeaway
      if (sig.recommended_action) {
        const actionRow = createEl("div", "text-xs text-[#404944] flex items-start gap-1.5");
        const checkIcon = createEl("span", "material-symbols-outlined text-[15px] text-[#174C38] shrink-0 mt-0.5", "arrow_right");
        const actionText = createEl("span", "font-medium text-[#202622]", sig.recommended_action);
        actionRow.append(checkIcon, actionText);
        card.append(actionRow);
      }

      evidenceList.append(card);
    });
  }

  // Render Layer 3: Technical Details (collapsed)
  function renderLayer3(data) {
    if (engineStatusTag) {
      engineStatusTag.textContent = data.model && data.model.status ? data.model.status.toUpperCase() : "RULES-ONLY FALLBACK";
    }
    if (engineLimitationText) {
      engineLimitationText.textContent = data.model?.limitation || "The local rule engine evaluated this content without remote ML model dependencies.";
    }

    // URL parsing breakdown
    if (technicalUrlList) {
      technicalUrlList.replaceChildren();
      if (!data.urls || data.urls.length === 0) {
        const noUrls = createEl("p", "text-xs text-[#707973] italic", "No HTTP/HTTPS web addresses were detected in the text.");
        technicalUrlList.append(noUrls);
      } else {
        data.urls.forEach((u) => {
          const item = createEl("div", "p-2.5 rounded bg-white border border-[#DDD7C5] flex flex-col gap-1");
          const urlLink = createEl("span", "font-mono text-xs font-bold text-[#003523] break-all", u.submitted_url);
          const meta = createEl("span", "text-[11px] text-[#404944]", `Host: ${u.host || 'N/A'} · Scheme: ${(u.scheme || '').toUpperCase()} · Valid: ${u.valid ? 'Yes' : 'No'}`);
          item.append(urlLink, meta);
          if (u.error) {
            const err = createEl("span", "text-[11px] text-[#BA1A1A]", u.error);
            item.append(err);
          }
          technicalUrlList.append(item);
        });
      }
    }

    // Limitations list
    if (technicalLimitationsList) {
      technicalLimitationsList.replaceChildren();
      if (data.limitations && data.limitations.length > 0) {
        data.limitations.forEach((lim) => {
          const li = createEl("li", "", lim);
          technicalLimitationsList.append(li);
        });
      }
    }
  }

  // Primary Result Handler
  function renderResult(data) {
    renderLayer1(data);
    renderLayer2(data.signals || []);
    renderLayer3(data);

    if (results) {
      results.hidden = false;
      results.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  // Main Analysis Trigger
  async function runAnalysis() {
    hideError();
    const rawInput = unifiedInput ? unifiedInput.value.trim() : "";

    if (!rawInput) {
      showError("Please paste a message or web address to check.");
      if (unifiedInput) unifiedInput.focus();
      return;
    }

    if (rawInput.length > 10000) {
      showError("Your message is too long (limit is 10,000 characters). Please paste a shorter excerpt.");
      return;
    }

    // Sync hidden fields to satisfy test suites / backend contract
    const isUrlOnly = /^https?:\/\/[^\s]+$/i.test(rawInput);
    if (isUrlOnly) {
      if (hiddenUrl) hiddenUrl.value = rawInput;
      if (hiddenMessage) hiddenMessage.value = "";
    } else {
      if (hiddenMessage) hiddenMessage.value = rawInput;
      if (hiddenUrl) hiddenUrl.value = "";
    }

    // Prepare JSON payload according to API contract
    const payload = {
      message: isUrlOnly ? null : rawInput,
      url: isUrlOnly ? rawInput : null,
      include_url_inspection: true,
      incident_status: incidentStatus ? incidentStatus.value : "received_only"
    };

    // UI Loading state
    if (analyzeButton) analyzeButton.disabled = true;
    if (analyzeBtnText) analyzeBtnText.textContent = "Checking...";
    if (loadingIndicator) loadingIndicator.classList.remove("hidden");

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        if (response.status === 422) {
          const errData = await response.json().catch(() => null);
          const detailMsg = errData && errData.detail && errData.detail[0] ? errData.detail[0].msg : "Please verify your input.";
          showError(`Could not analyze input: ${detailMsg}`);
        } else {
          showError(`The check could not be completed (Server returned error ${response.status}). Please try again.`);
        }
        return;
      }

      const data = await response.json();
      renderResult(data);
    } catch {
      showError("Cannot connect to the SIFT analysis service. Please check your network or ensure the server is running.");
    } finally {
      if (analyzeButton) analyzeButton.disabled = false;
      if (analyzeBtnText) analyzeBtnText.textContent = "Check for Scam Signs";
      if (loadingIndicator) loadingIndicator.classList.add("hidden");
    }
  }

  if (analyzeButton) {
    analyzeButton.addEventListener("click", runAnalysis);
  }
})();
