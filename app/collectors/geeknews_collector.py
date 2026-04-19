from dataclasses import dataclass

import feedparser

from ..config import settings


@dataclass
class NewsItem:
    title: str
    summary: str
    url: str


def fetch(keyword: str | None = None, max_results: int | None = None) -> list[NewsItem]:
    limit = max_results or settings.geeknews_max_results
    feed = feedparser.parse(settings.geeknews_rss_url)

    items: list[NewsItem] = []
    for entry in feed.entries:
        title = getattr(entry, "title", "").strip()
        summary = getattr(entry, "summary", "").strip()
        url = getattr(entry, "link", "")

        if keyword:
            haystack = f"{title} {summary}".lower()
            if keyword.lower() not in haystack:
                continue

        items.append(NewsItem(title=title, summary=summary, url=url))
        if len(items) >= limit:
            break

    if keyword and not items:
        for entry in feed.entries[:limit]:
            items.append(
                NewsItem(
                    title=getattr(entry, "title", "").strip(),
                    summary=getattr(entry, "summary", "").strip(),
                    url=getattr(entry, "link", ""),
                )
            )

    return items
