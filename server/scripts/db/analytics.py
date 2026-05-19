import hashlib
import json
import os
import threading
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from .connection import get_analytics_db_path

_lock = threading.Lock()
_MAX_RECENT_EVENTS = 200


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _default_payload() -> dict:
    return {
        "daily": {},
        "recent_events": [],
    }


def _read_db() -> dict:
    filepath = get_analytics_db_path()
    if not os.path.exists(filepath):
        return _default_payload()

    with open(filepath, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return _default_payload()

    data.setdefault("daily", {})
    data.setdefault("recent_events", [])
    return data


def _write_db(data: dict) -> None:
    filepath = get_analytics_db_path()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _to_iso_date(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def _normalize_group(granularity: str) -> str:
    return granularity if granularity in {"day", "week", "month"} else "day"


def _period_key(date_str: str, granularity: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if granularity == "month":
        return dt.strftime("%Y-%m")
    if granularity == "week":
        iso_year, iso_week, _ = dt.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    return date_str


def _sort_period_key(period_key: str, granularity: str) -> tuple:
    if granularity == "month":
        year, month = period_key.split("-")
        return int(year), int(month)
    if granularity == "week":
        year, week = period_key.split("-W")
        return int(year), int(week)
    return (period_key,)


def _parse_range_days(range_value: str) -> int:
    mapping = {"7d": 7, "30d": 30, "90d": 90, "180d": 180, "365d": 365}
    return mapping.get(range_value, 30)


def _make_visitor_hash(ip: str, user_agent: str) -> str:
    digest = hashlib.sha256(f"{ip}|{user_agent}".encode("utf-8")).hexdigest()
    return digest[:24]


def _ensure_day_bucket(data: dict, date_key: str) -> dict:
    bucket = data["daily"].setdefault(
        date_key,
        {
            "page_views": {"pv": 0, "visitors": [], "paths": {}},
            "articles": {},
            "cta": {},
        },
    )
    bucket.setdefault("page_views", {"pv": 0, "visitors": [], "paths": {}})
    bucket.setdefault("articles", {})
    bucket.setdefault("cta", {})
    bucket["page_views"].setdefault("pv", 0)
    bucket["page_views"].setdefault("visitors", [])
    bucket["page_views"].setdefault("paths", {})
    return bucket


def _append_unique(items: List[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


class AnalyticsHandler:
    @classmethod
    def track_event(
        cls,
        *,
        event_name: str,
        path: str,
        event_key: str,
        event_source: str,
        article_id: str,
        article_title: str,
        referrer: str,
        ip: str,
        user_agent: str,
        extra: Optional[dict] = None,
    ) -> dict:
        now = _utc_now()
        date_key = _to_iso_date(now)
        visitor_hash = _make_visitor_hash(ip, user_agent)

        with _lock:
            data = _read_db()
            bucket = _ensure_day_bucket(data, date_key)
            page_views = bucket["page_views"]

            if event_name == "page_view":
                page_views["pv"] += 1
                _append_unique(page_views["visitors"], visitor_hash)
                normalized_path = path or "/"
                page_views["paths"][normalized_path] = page_views["paths"].get(normalized_path, 0) + 1

            elif event_name == "article_view":
                if article_id:
                    article_bucket = bucket["articles"].setdefault(
                        article_id,
                        {
                            "title": article_title or article_id,
                            "clicks": 0,
                            "visitors": [],
                        },
                    )
                    article_bucket["title"] = article_title or article_bucket.get("title") or article_id
                    article_bucket["clicks"] += 1
                    _append_unique(article_bucket["visitors"], visitor_hash)

            elif event_name in {"cta_impression", "cta_click"}:
                cta_key = event_key or "unknown"
                cta_bucket = bucket["cta"].setdefault(
                    cta_key,
                    {
                        "label": event_key or "unknown",
                        "impressions": 0,
                        "clicks": 0,
                        "visitors": [],
                        "click_visitors": [],
                        "sources": {},
                    },
                )
                cta_bucket["label"] = event_key or cta_bucket.get("label") or "unknown"
                if event_name == "cta_impression":
                    cta_bucket["impressions"] += 1
                    _append_unique(cta_bucket["visitors"], visitor_hash)
                else:
                    cta_bucket["clicks"] += 1
                    _append_unique(cta_bucket["click_visitors"], visitor_hash)
                    source_key = event_source or path or "unknown"
                    cta_bucket["sources"][source_key] = cta_bucket["sources"].get(source_key, 0) + 1

            data["recent_events"].append(
                {
                    "event_name": event_name,
                    "event_key": event_key,
                    "event_source": event_source,
                    "article_id": article_id,
                    "article_title": article_title,
                    "path": path,
                    "referrer": referrer,
                    "visitor_hash": visitor_hash,
                    "ip": ip,
                    "user_agent": user_agent,
                    "created_at": now.isoformat(),
                    "extra": extra or {},
                }
            )
            data["recent_events"] = data["recent_events"][-_MAX_RECENT_EVENTS:]
            _write_db(data)

        return {"ok": True, "date": date_key}

    @classmethod
    def get_overview(cls, *, range_value: str = "30d", granularity: str = "day") -> dict:
        range_days = _parse_range_days(range_value)
        granularity = _normalize_group(granularity)
        cutoff = _utc_now().date() - timedelta(days=range_days - 1)

        with _lock:
            data = _read_db()

        grouped = defaultdict(lambda: {"pv": 0, "visitors": set()})

        for date_str, bucket in data["daily"].items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj < cutoff:
                continue
            page_views = bucket.get("page_views", {})
            period = _period_key(date_str, granularity)
            grouped[period]["pv"] += int(page_views.get("pv", 0))
            grouped[period]["visitors"].update(page_views.get("visitors", []))

        labels = []
        pv_series = []
        uv_series = []
        for period in sorted(grouped.keys(), key=lambda item: _sort_period_key(item, granularity)):
            labels.append(period)
            pv_series.append(grouped[period]["pv"])
            uv_series.append(len(grouped[period]["visitors"]))

        total_pv = sum(pv_series)
        total_uv = len({visitor for item in grouped.values() for visitor in item["visitors"]})
        return {
            "range": range_value,
            "granularity": granularity,
            "summary": {"pv": total_pv, "uv": total_uv},
            "series": {"labels": labels, "pv": pv_series, "uv": uv_series},
        }

    @classmethod
    def get_top_articles(cls, *, range_value: str = "30d", limit: int = 10) -> dict:
        range_days = _parse_range_days(range_value)
        cutoff = _utc_now().date() - timedelta(days=range_days - 1)

        with _lock:
            data = _read_db()

        article_totals: Dict[str, dict] = {}
        for date_str, bucket in data["daily"].items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj < cutoff:
                continue
            for article_id, item in bucket.get("articles", {}).items():
                target = article_totals.setdefault(
                    article_id,
                    {"article_id": article_id, "title": item.get("title") or article_id, "clicks": 0, "visitors": set()},
                )
                target["title"] = item.get("title") or target["title"]
                target["clicks"] += int(item.get("clicks", 0))
                target["visitors"].update(item.get("visitors", []))

        records = sorted(article_totals.values(), key=lambda item: item["clicks"], reverse=True)[:limit]
        return {
            "range": range_value,
            "items": [
                {
                    "article_id": item["article_id"],
                    "title": item["title"],
                    "clicks": item["clicks"],
                    "uv": len(item["visitors"]),
                }
                for item in records
            ],
        }

    @classmethod
    def get_cta_summary(cls, *, range_value: str = "30d", event_key: str = "live_demo") -> dict:
        range_days = _parse_range_days(range_value)
        cutoff = _utc_now().date() - timedelta(days=range_days - 1)

        with _lock:
            data = _read_db()

        impressions = 0
        clicks = 0
        visitors = set()
        click_visitors = set()
        sources: Dict[str, int] = defaultdict(int)

        for date_str, bucket in data["daily"].items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj < cutoff:
                continue

            cta_item = bucket.get("cta", {}).get(event_key)
            if not cta_item:
                continue

            impressions += int(cta_item.get("impressions", 0))
            clicks += int(cta_item.get("clicks", 0))
            visitors.update(cta_item.get("visitors", []))
            click_visitors.update(cta_item.get("click_visitors", []))
            for source_key, count in cta_item.get("sources", {}).items():
                sources[source_key] += int(count)

        ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0
        sorted_sources = sorted(sources.items(), key=lambda item: item[1], reverse=True)
        return {
            "range": range_value,
            "event_key": event_key,
            "impressions": impressions,
            "clicks": clicks,
            "uv": len(visitors),
            "click_uv": len(click_visitors),
            "ctr": ctr,
            "sources": [{"source": source, "clicks": count} for source, count in sorted_sources],
        }
