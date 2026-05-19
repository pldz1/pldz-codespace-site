import { apiGet, apiPost, hostPrefix } from "./request.js";

const analyticsPrefix = `${hostPrefix}/analytics`;

export function trackAnalyticsEvent(payload) {
  return apiPost(`${analyticsPrefix}/track`, payload);
}

export function getAnalyticsOverview(rangeValue = "30d", granularity = "day") {
  return apiGet(`${analyticsPrefix}/overview?range_value=${encodeURIComponent(rangeValue)}&granularity=${encodeURIComponent(granularity)}`);
}

export function getAnalyticsTopArticles(rangeValue = "30d", limit = 10) {
  return apiGet(`${analyticsPrefix}/articles/top?range_value=${encodeURIComponent(rangeValue)}&limit=${encodeURIComponent(limit)}`);
}

export function getAnalyticsCta(rangeValue = "30d", eventKey = "live_demo") {
  return apiGet(`${analyticsPrefix}/cta?range_value=${encodeURIComponent(rangeValue)}&event_key=${encodeURIComponent(eventKey)}`);
}
