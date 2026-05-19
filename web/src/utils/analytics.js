const VISITOR_KEY = "pldz.analytics.visitor";
const CTA_SELECTOR = "[data-analytics-cta]";
let initialized = false;
let observer = null;
let lastTrackedPath = "";
const seenImpressions = new Set();

function ensureVisitorId() {
  const existing = window.localStorage.getItem(VISITOR_KEY);
  if (existing) return existing;
  const created = `v_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
  window.localStorage.setItem(VISITOR_KEY, created);
  return created;
}

function buildBasePayload() {
  return {
    path: window.location.pathname,
    referrer: document.referrer || "",
    client_user_agent: navigator.userAgent || "",
    extra: {
      visitor_id: ensureVisitorId(),
      viewport: `${window.innerWidth}x${window.innerHeight}`,
      language: navigator.language || "",
    },
  };
}

function sendTrack(payload) {
  const body = JSON.stringify(payload);
  if (navigator.sendBeacon) {
    const blob = new Blob([body], { type: "application/json" });
    navigator.sendBeacon("/api/v1/analytics/track", blob);
    return;
  }

  fetch("/api/v1/analytics/track", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    keepalive: true,
  }).catch(() => null);
}

export function trackPageView(pathOverride = "") {
  const path = pathOverride || window.location.pathname;
  if (!path || path.startsWith("/admin")) return;
  if (lastTrackedPath === path) return;
  lastTrackedPath = path;
  sendTrack({
    ...buildBasePayload(),
    event_name: "page_view",
    path,
  });
}

export function trackArticleView({ articleId = "", articleTitle = "" } = {}) {
  if (!articleId) return;
  sendTrack({
    ...buildBasePayload(),
    event_name: "article_view",
    article_id: articleId,
    article_title: articleTitle,
  });
}

export function trackCtaClick({ eventKey = "", eventSource = "", extra = {} } = {}) {
  if (!eventKey) return;
  sendTrack({
    ...buildBasePayload(),
    event_name: "cta_click",
    event_key: eventKey,
    event_source: eventSource,
    extra,
  });
}

function handleDocumentClick(event) {
  const target = event.target?.closest?.(CTA_SELECTOR);
  if (!target) return;

  trackCtaClick({
    eventKey: target.dataset.analyticsCta || "",
    eventSource: target.dataset.analyticsSource || window.location.pathname,
    extra: {
      label: target.dataset.analyticsLabel || target.textContent?.trim?.() || "",
      href: target.getAttribute("href") || "",
    },
  });
}

function observeCtaImpressions() {
  if (observer) {
    observer.disconnect();
  }

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        const element = entry.target;
        const impressionKey = `${window.location.pathname}|${element.dataset.analyticsCta || ""}|${element.dataset.analyticsSource || ""}`;
        if (seenImpressions.has(impressionKey)) return;
        seenImpressions.add(impressionKey);

        sendTrack({
          ...buildBasePayload(),
          event_name: "cta_impression",
          event_key: element.dataset.analyticsCta || "",
          event_source: element.dataset.analyticsSource || window.location.pathname,
          extra: {
            label: element.dataset.analyticsLabel || element.textContent?.trim?.() || "",
            href: element.getAttribute("href") || "",
          },
        });
      });
    },
    { threshold: 0.55 }
  );

  document.querySelectorAll(CTA_SELECTOR).forEach((element) => observer.observe(element));
}

export function refreshAnalyticsBindings() {
  if (!initialized) return;
  observeCtaImpressions();
}

export function initAnalytics(router) {
  if (initialized) {
    return;
  }

  initialized = true;
  ensureVisitorId();
  document.addEventListener("click", handleDocumentClick, true);

  router.afterEach((to) => {
    window.requestAnimationFrame(() => {
      lastTrackedPath = "";
      trackPageView(to.path);
      refreshAnalyticsBindings();
    });
  });

  window.requestAnimationFrame(() => {
    trackPageView(window.location.pathname);
    refreshAnalyticsBindings();
  });
}
