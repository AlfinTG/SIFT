(() => {
  // DOM element selectors
  const messageInput = document.querySelector("#message");
  const urlInput = document.querySelector("#url");
  const incidentStatus = document.querySelector("#incident-status");
  const includeUrlInspection = document.querySelector("#includeUrlInspection");
  const analyzeButton = document.querySelector("#analyze");
  const analyzeBtnText = document.querySelector("#analyzeBtnText");
  const formError = document.querySelector("#form-error");
  const formErrorText = document.querySelector("#form-error-text");
  const formErrorClose = document.querySelector("#form-error-close");
  const analysisProgressState = document.querySelector("#analysisProgressState");
  const clearBtn = document.querySelector("#clearBtn");
  const pasteSampleBtn = document.querySelector("#pasteSampleBtn");
  const tokenCount = document.querySelector("#tokenCount");
  const quickResetBtn = document.querySelector("#quickResetBtn");
  const brandLogo = document.querySelector("#brandLogo");
  const scenarioGrid = document.querySelector("#scenarioGrid");
  const modeSelector = document.querySelector("#modeSelector");
  const copyReportBtn = document.querySelector("#copyReportBtn");
  const dossierToast = document.querySelector("#dossierToast");
  const toastMessage = document.querySelector("#toastMessage");

  // Posture widget elements
  const postureStatusBadge = document.querySelector("#postureStatusBadge");
  const threatScoreDisplay = document.querySelector("#threatScoreDisplay");
  const postureLabel = document.querySelector("#postureLabel");
  const postureSub = document.querySelector("#postureSub");
  const gaugeSvg = document.querySelector("#gaugeSvg");

  // Results containers
  const results = document.querySelector("#results");
  const assessment = document.querySelector("#assessment");
  const signals = document.querySelector("#signals");
  const signalCountBadge = document.querySelector("#signalCountBadge");
  const urlInspections = document.querySelector("#url-inspections");
  const nextSteps = document.querySelector("#next-steps");
  const limitations = document.querySelector("#limitations");

  // Nav buttons
  const navAnalyze = document.querySelector("#navAnalyze");
  const navReport = document.querySelector("#navReport");
  const navEvidence = document.querySelector("#navEvidence");

  let lastAnalysisData = null;

  // Safe DOM helpers (prevents innerHTML injection)
  function createEl(tagName, className, textContent) {
    const el = document.createElement(tagName);
    if (className) el.className = className;
    if (textContent !== undefined && textContent !== null) el.textContent = textContent;
    return el;
  }

  function showToast(text) {
    if (toastMessage) toastMessage.textContent = text;
    if (dossierToast) {
      dossierToast.classList.remove("translate-y-16", "opacity-0", "pointer-events-none");
      setTimeout(() => {
        dossierToast.classList.add("translate-y-16", "opacity-0", "pointer-events-none");
      }, 3000);
    }
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

  function updateMetadata() {
    const msg = messageInput ? messageInput.value : "";
    const u = urlInput ? urlInput.value : "";
    const chars = msg.length + u.length;
    const tokens = Math.ceil(chars / 4);
    if (tokenCount) {
      tokenCount.textContent = `${chars} chars | ~${tokens} tokens`;
    }

    if (!lastAnalysisData) {
      if (chars > 10) {
        if (postureLabel) postureLabel.textContent = "Payload Buffered";
        if (postureSub) postureSub.textContent = "Click 'Sift for Deceptive Patterns' to run local heuristics.";
        if (postureStatusBadge) {
          postureStatusBadge.textContent = "INGESTED";
          postureStatusBadge.className = "font-mono text-xs px-2 py-0.5 rounded-md bg-secondary-fixed text-on-secondary-fixed font-bold";
        }
      } else {
        if (postureLabel) postureLabel.textContent = "Awaiting Content";
        if (postureSub) postureSub.textContent = "Input payload to activate local inspection.";
        if (postureStatusBadge) {
          postureStatusBadge.textContent = "READY";
          postureStatusBadge.className = "font-mono text-xs px-2 py-0.5 rounded-md bg-secondary-container text-on-secondary-container font-bold";
        }
      }
    }
  }

  if (messageInput) messageInput.addEventListener("input", updateMetadata);
  if (urlInput) urlInput.addEventListener("input", updateMetadata);

  // Mode buttons
  if (modeSelector) {
    const modeButtons = modeSelector.querySelectorAll(".mode-btn");
    modeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        modeButtons.forEach((b) => {
          b.className = "mode-btn px-4 py-2 rounded-lg text-sm font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest transition-all flex items-center gap-2";
        });
        btn.className = "mode-btn px-4 py-2 rounded-lg text-sm font-semibold transition-all bg-primary-container text-on-primary shadow-sm flex items-center gap-2";
        const mode = btn.getAttribute("data-mode");
        const msgGrp = document.querySelector("#messageGroup");
        const urlGrp = document.querySelector("#urlGroup");
        if (mode === "message") {
          if (msgGrp) msgGrp.classList.remove("hidden");
          if (urlGrp) urlGrp.classList.remove("hidden");
          if (messageInput) messageInput.focus();
        } else if (mode === "url") {
          if (urlGrp) urlGrp.classList.remove("hidden");
          if (urlInput) urlInput.focus();
        } else {
          if (msgGrp) msgGrp.classList.remove("hidden");
          if (urlGrp) urlGrp.classList.remove("hidden");
        }
      });
    });
  }

  // Clear button
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (messageInput) messageInput.value = "";
      if (urlInput) urlInput.value = "";
      lastAnalysisData = null;
      hideError();
      if (results) results.hidden = true;
      updateMetadata();
      if (threatScoreDisplay) threatScoreDisplay.textContent = "--";
      if (gaugeSvg) gaugeSvg.setAttribute("stroke-dasharray", "15, 100");
      if (postureStatusBadge) {
        postureStatusBadge.textContent = "READY";
        postureStatusBadge.className = "font-mono text-xs px-2 py-0.5 rounded-md bg-secondary-container text-on-secondary-container font-bold";
      }
      if (messageInput) messageInput.focus();
    });
  }

  // Quick reset / brand logo reset
  const handleReset = () => {
    if (clearBtn) clearBtn.click();
    showToast("Workspace refreshed.");
  };
  if (quickResetBtn) quickResetBtn.addEventListener("click", handleReset);
  if (brandLogo) brandLogo.addEventListener("click", handleReset);

  // Paste clipboard
  if (pasteSampleBtn) {
    pasteSampleBtn.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          if (messageInput) messageInput.value = text;
          updateMetadata();
          showToast("Pasted from clipboard.");
        }
      } catch {
        showError("Clipboard access was blocked by browser. Please paste manually.");
      }
    });
  }

  // Scenarios
  const scenarios = {
    internship: {
      message: "Congratulations, you are shortlisted for an internship. Pay ₹799 as a registration fee today to confirm your seat.",
      url: "",
      incident: "received_only"
    },
    upipin: {
      message: "Your refund is pending. Scan the QR code and enter your UPI PIN immediately to receive the amount.",
      url: "",
      incident: "received_only"
    },
    legitotp: {
      message: "Security reminder: Never share your OTP, password, or UPI PIN with anyone.",
      url: "",
      incident: "received_only"
    }
  };

  if (scenarioGrid) {
    scenarioGrid.querySelectorAll(".scenario-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-scenario");
        const sc = scenarios[key];
        if (sc) {
          if (messageInput) messageInput.value = sc.message;
          if (urlInput) urlInput.value = sc.url;
          if (incidentStatus) incidentStatus.value = sc.incident;
          updateMetadata();
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

  // Render individual signal card
  function renderSignalCard(signal, index) {
    const card = createEl("article", "p-5 rounded-xl bg-surface-container-lowest flex flex-col justify-between shadow-sm border border-outline-variant");

    const topSection = createEl("div", "flex flex-col gap-3");

    // Header row
    const headerRow = createEl("div", "flex items-start justify-between gap-2");
    const numAndSource = createEl("div", "flex items-center gap-1.5");
    const numPill = createEl("span", "w-6 h-6 rounded-md bg-surface-container-high flex items-center justify-center text-primary font-mono text-xs font-bold", String(index + 1).padStart(2, "0"));
    const sourcePill = createEl("span", "inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-xs bg-surface-container-high text-on-surface-variant font-medium", signal.source === "url" ? "URL Inspection" : "Safety Rule");
    numAndSource.append(numPill, sourcePill);

    let sevClass = "bg-secondary-fixed text-on-secondary-fixed";
    if (signal.severity === "high" || signal.severity === "critical") {
      sevClass = "bg-error-container text-on-error-container";
    }
    const sevBadge = createEl("span", `px-2 py-0.5 rounded font-mono text-xs font-semibold uppercase ${sevClass}`, signal.severity);
    headerRow.append(numAndSource, sevBadge);

    // Title / Signal ID
    const titleBox = createEl("div");
    const signalTitle = createEl("h4", "font-body text-sm font-semibold text-on-surface", signal.signal_id.replace(/_/g, " ").toUpperCase());
    const signalSub = createEl("span", "font-mono text-[11px] text-on-surface-variant uppercase tracking-wide", `Source: ${signal.source}`);
    titleBox.append(signalTitle, signalSub);

    // Extracted Evidence Snippet Box
    const snippetBox = createEl("div", "p-2.5 rounded bg-surface-container text-on-surface font-mono text-xs border border-outline-variant");
    const snippetLabel = createEl("span", "text-on-surface-variant text-[10px] block uppercase font-medium mb-1", "Extracted Snippet:");
    const snippetCode = createEl("code", "text-error font-semibold break-all", signal.evidence);
    snippetBox.append(snippetLabel, snippetCode);

    // Reason
    const reasonPara = createEl("p", "text-xs text-on-surface-variant leading-relaxed", signal.reason);

    topSection.append(headerRow, titleBox, snippetBox, reasonPara);

    // Actionable Recommendation Footer
    const footer = createEl("div", "mt-4 pt-3 border-t border-outline-variant flex flex-col gap-1.5");
    const footerLabel = createEl("span", "text-[11px] font-mono text-on-surface-variant uppercase font-semibold flex items-center gap-1");
    const shieldIcon = createEl("span", "material-symbols-outlined text-[14px] text-primary", "verified_user");
    const footerLabelText = createEl("span", "", "Safety Recommendation");
    footerLabel.append(shieldIcon, footerLabelText);

    const actionBox = createEl("p", "text-xs text-on-surface bg-surface-container-low p-2 rounded leading-snug", signal.recommended_action);
    footer.append(footerLabel, actionBox);

    card.append(topSection, footer);
    return card;
  }

  // Render URL inspection item
  function renderUrlCard(inspection) {
    const card = createEl("div", `p-4 rounded-lg border ${inspection.valid ? "bg-surface-container-low border-outline-variant" : "bg-error-container/30 border-error-container"} flex flex-col gap-2`);

    const header = createEl("div", "flex items-center justify-between gap-2 flex-wrap");
    const submitted = createEl("code", "font-mono text-xs text-primary font-bold break-all", inspection.submitted_url);
    const validBadge = createEl("span", `font-mono text-[11px] px-2 py-0.5 rounded font-semibold ${inspection.valid ? "bg-primary-container text-on-primary" : "bg-error-container text-on-error-container"}`, inspection.valid ? "VALID SYNTAX" : "INVALID URL");
    header.append(submitted, validBadge);

    card.append(header);

    if (!inspection.valid) {
      const errPara = createEl("p", "text-xs text-error font-mono", inspection.error || "SIFT could not parse this URL safely.");
      card.append(errPara);
      return card;
    }

    const grid = createEl("div", "grid grid-cols-2 gap-2 text-xs font-mono text-on-surface-variant pt-1");
    const hostSpan = createEl("div", "", `Host: ${inspection.host}`);
    const schemeSpan = createEl("div", "", `Scheme: ${(inspection.scheme || "").toUpperCase()}`);
    grid.append(hostSpan, schemeSpan);
    card.append(grid);

    const sigCount = inspection.signals ? inspection.signals.length : 0;
    const countNote = createEl("p", "text-xs text-on-surface pt-1", sigCount === 0
      ? "No structural warning signals found on this URL. SIFT does not check live reputation."
      : `${sigCount} structural warning ${sigCount === 1 ? "signal" : "signals"} isolated on this URL.`);
    card.append(countNote);

    return card;
  }

  // Primary Result Renderer
  function renderResult(data) {
    lastAnalysisData = data;

    // Update Posture Widget
    const level = data.assessment.level;
    const levelDisplay = level.replace(/_/g, " ").toUpperCase();
    if (threatScoreDisplay) threatScoreDisplay.textContent = levelDisplay.split(" ")[0];

    let gaugeVal = "25, 100";
    let statusClass = "bg-secondary-container text-on-secondary-container";
    if (level === "critical") {
      gaugeVal = "95, 100";
      statusClass = "bg-error-container text-on-error-container";
    } else if (level === "high") {
      gaugeVal = "75, 100";
      statusClass = "bg-error-container text-on-error-container";
    } else if (level === "moderate") {
      gaugeVal = "50, 100";
      statusClass = "bg-secondary-fixed text-on-secondary-fixed";
    }

    if (gaugeSvg) gaugeSvg.setAttribute("stroke-dasharray", gaugeVal);
    if (postureStatusBadge) {
      postureStatusBadge.textContent = levelDisplay;
      postureStatusBadge.className = `font-mono text-xs px-2 py-0.5 rounded-md font-bold ${statusClass}`;
    }
    if (postureLabel) postureLabel.textContent = `Assessed: ${levelDisplay}`;
    if (postureSub) postureSub.textContent = data.assessment.summary;

    // 1. Primary Assessment Dossier Card
    assessment.replaceChildren();
    assessment.className = `rounded-xl p-6 md:p-8 shadow-sm text-on-primary assessment-${level}`;

    const dossierHeader = createEl("div", "flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/20");
    const badgeWrapper = createEl("div", "flex flex-wrap items-center gap-2.5");

    const levelBadge = createEl("span", `inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-mono text-xs font-semibold tracking-wide ${level === 'critical' || level === 'high' ? 'bg-error-container text-on-error-container' : 'bg-secondary-container text-on-secondary-container'}`);
    const pulseDot = createEl("span", `w-2 h-2 rounded-full ${level === 'critical' || level === 'high' ? 'bg-error animate-ping' : 'bg-secondary'}`);
    const levelText = createEl("span", "", `RISK LEVEL: ${levelDisplay}`);
    levelBadge.append(pulseDot, levelText);

    const modelStatusBadge = createEl("span", "px-3 py-1 rounded-full bg-black/30 text-white font-mono text-xs border border-white/20", "Classifier: Rules-Only Fallback");
    badgeWrapper.append(levelBadge, modelStatusBadge);

    const sessionInfo = createEl("div", "text-xs font-mono text-white/80", "Independent Heuristics Engine");
    dossierHeader.append(badgeWrapper, sessionInfo);

    // Summary Lead
    const contentGrid = createEl("div", "grid grid-cols-1 lg:grid-cols-12 gap-6 items-end mt-4");
    const leftSummary = createEl("div", "lg:col-span-8 flex flex-col gap-2");
    const summaryCategory = createEl("span", "font-mono text-xs uppercase tracking-wider text-secondary-fixed flex items-center gap-1.5");
    const alertIcon = createEl("span", "material-symbols-outlined text-[16px]", "crisis_alert");
    const categoryText = createEl("span", "", "Analytical Finding & Risk Disposition");
    summaryCategory.append(alertIcon, categoryText);

    const headline = createEl("h3", "font-display text-2xl md:text-3xl text-white font-normal leading-tight", data.assessment.summary);
    leftSummary.append(summaryCategory, headline);

    if (data.assessment.uncertain) {
      const uncertaintyNotice = createEl("p", "text-xs text-white/80 font-mono mt-1", "⚠️ Caution: SIFT does not verify absolute safety. Low-indicator results do not mean content is safe.");
      leftSummary.append(uncertaintyNotice);
    }

    const rightTelemetry = createEl("div", "lg:col-span-4 bg-black/25 p-4 rounded-lg flex flex-col gap-2 border border-white/20");
    const telemetryTitle = createEl("div", "flex items-center justify-between font-mono text-xs text-white/90");
    const tLabel = createEl("span", "", "Engine State");
    const tVal = createEl("span", "text-secondary-fixed font-semibold", data.model ? data.model.status.toUpperCase() : "ACTIVE");
    telemetryTitle.append(tLabel, tVal);

    const limitationNote = createEl("p", "text-xs text-white/70 leading-snug", data.model?.limitation || "The local rules-only fallback is active; results do not include an ML probability score.");
    rightTelemetry.append(telemetryTitle, limitationNote);

    contentGrid.append(leftSummary, rightTelemetry);
    assessment.append(dossierHeader, contentGrid);

    // 2. Signals
    signals.replaceChildren();
    const sigCount = data.signals ? data.signals.length : 0;
    if (signalCountBadge) signalCountBadge.textContent = `${sigCount} ${sigCount === 1 ? 'signal' : 'signals'} found`;

    if (sigCount === 0) {
      const emptyCard = createEl("div", "md:col-span-2 lg:col-span-3 p-6 rounded-xl bg-surface-container-lowest border border-outline-variant text-center flex flex-col items-center gap-2");
      const icon = createEl("span", "material-symbols-outlined text-3xl text-primary", "check_circle");
      const title = createEl("h4", "font-medium text-sm text-on-surface", "No Specific Warning Signals Found");
      const note = createEl("p", "text-xs text-on-surface-variant max-w-md", "SIFT's available local rules did not find immediate known warning indicators. This does NOT verify safety or confirm legitimacy.");
      emptyCard.append(icon, title, note);
      signals.append(emptyCard);
    } else {
      data.signals.forEach((sig, idx) => {
        signals.append(renderSignalCard(sig, idx));
      });
    }

    // 3. Safe Next Steps
    nextSteps.replaceChildren();
    if (data.next_steps && data.next_steps.length > 0) {
      data.next_steps.forEach((step, idx) => {
        const item = createEl("li", "flex items-start gap-2.5 p-3 rounded-lg bg-surface-container-lowest border border-outline-variant text-xs text-on-surface leading-relaxed");
        const numPill = createEl("span", "w-5 h-5 rounded-full bg-primary-container text-on-primary font-mono text-[11px] flex items-center justify-center font-bold shrink-0 mt-0.5", String(idx + 1));
        const textSpan = createEl("span", "", step);
        item.append(numPill, textSpan);
        nextSteps.append(item);
      });
    }

    // 4. URL Inspections
    urlInspections.replaceChildren();
    if (!data.urls || data.urls.length === 0) {
      const emptyUrl = createEl("p", "text-xs text-on-surface-variant italic p-4 bg-surface-container rounded-lg", "No HTTP or HTTPS URLs were provided or detected in the message.");
      urlInspections.append(emptyUrl);
    } else {
      data.urls.forEach((inspection) => {
        urlInspections.append(renderUrlCard(inspection));
      });
    }

    // 5. Limitations
    limitations.replaceChildren();
    if (data.limitations && data.limitations.length > 0) {
      data.limitations.forEach((lim) => {
        const li = createEl("li", "flex items-start gap-2 leading-relaxed");
        const dot = createEl("span", "w-1.5 h-1.5 rounded-full bg-outline shrink-0 mt-1.5");
        const t = createEl("span", "", lim);
        li.append(dot, t);
        limitations.append(li);
      });
    }

    // Reveal and scroll smoothly
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Copy Summary Action
  if (copyReportBtn) {
    copyReportBtn.addEventListener("click", () => {
      if (!lastAnalysisData) return;
      const text = `SIFT Scam Analysis Summary\nRisk Level: ${lastAnalysisData.assessment.level.toUpperCase()}\nSummary: ${lastAnalysisData.assessment.summary}\nSignals Found: ${lastAnalysisData.signals.length}\nUncertainty Notice: SIFT runs locally and does not guarantee safety.`;
      navigator.clipboard.writeText(text).then(() => {
        showToast("Summary copied to clipboard.");
      });
    });
  }

  // Analysis Dispatcher
  async function runAnalysis() {
    hideError();
    const msg = messageInput ? messageInput.value.trim() : "";
    const u = urlInput ? urlInput.value.trim() : "";

    if (!msg && !u) {
      showError("Please paste a message or enter a URL before running analysis.");
      if (messageInput) messageInput.focus();
      return;
    }

    if (msg.length > 10000) {
      showError("Message exceeds the maximum limit of 10,000 characters.");
      return;
    }

    if (u.length > 2048) {
      showError("URL exceeds the maximum limit of 2,048 characters.");
      return;
    }

    // UI Loading state
    if (analyzeButton) analyzeButton.disabled = true;
    if (analyzeBtnText) analyzeBtnText.textContent = "Analyzing Locally...";
    if (analysisProgressState) analysisProgressState.classList.remove("hidden");

    const payload = {
      message: msg || null,
      url: u || null,
      include_url_inspection: includeUrlInspection ? includeUrlInspection.checked : true,
      incident_status: incidentStatus ? incidentStatus.value : "received_only"
    };

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
          const detailMsg = errData && errData.detail && errData.detail[0] ? errData.detail[0].msg : "Validation error on submitted data.";
          showError(`Validation Error: ${detailMsg}`);
        } else {
          showError(`Service returned status code ${response.status}. Please retry.`);
        }
        return;
      }

      const data = await response.json();
      renderResult(data);
    } catch {
      showError("Could not connect to SIFT analysis service. Please ensure the backend is running.");
    } finally {
      if (analyzeButton) analyzeButton.disabled = false;
      if (analyzeBtnText) analyzeBtnText.textContent = "Sift for Deceptive Patterns";
      if (analysisProgressState) analysisProgressState.classList.add("hidden");
    }
  }

  if (analyzeButton) {
    analyzeButton.addEventListener("click", runAnalysis);
  }

  // Nav buttons jump
  if (navAnalyze) {
    navAnalyze.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
      if (messageInput) messageInput.focus();
    });
  }

  if (navReport) {
    navReport.addEventListener("click", () => {
      if (results && !results.hidden) {
        assessment.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        runAnalysis();
      }
    });
  }

  if (navEvidence) {
    navEvidence.addEventListener("click", () => {
      if (results && !results.hidden) {
        signals.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        runAnalysis();
      }
    });
  }

  // Initial metadata count
  updateMetadata();
})();
