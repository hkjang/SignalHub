import json
import logging

from ..collectors import arxiv_collector, geeknews_collector
from ..database import connect
from . import analyzer, mailer


logger = logging.getLogger(__name__)


def collect_and_analyze(keyword: str, run_type: str = "manual") -> dict:
    papers = arxiv_collector.fetch(keyword)
    news = geeknews_collector.fetch(keyword)
    result, tags = analyzer.analyze(papers, news)

    sources = {
        "papers": [
            {"title": p.title, "url": p.url, "authors": p.authors} for p in papers
        ],
        "news": [{"title": n.title, "url": n.url} for n in news],
    }

    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO analysis (keyword, result, run_type, sources, tags)
               VALUES (?, ?, ?, ?, ?)""",
            (
                keyword,
                result,
                run_type,
                json.dumps(sources, ensure_ascii=False),
                json.dumps(tags, ensure_ascii=False),
            ),
        )
        conn.commit()
        analysis_id = cur.lastrowid

    outcome = {
        "id": analysis_id,
        "keyword": keyword,
        "run_type": run_type,
        "result": result,
        "tags": tags,
        "papers": len(papers),
        "news": len(news),
    }

    try:
        mailer.send_async(outcome)
    except Exception:
        logger.exception("mailer dispatch failed")

    return outcome


def cleanup_old_analyses(retention_days: int) -> int:
    if retention_days is None or retention_days <= 0:
        return 0
    with connect() as conn:
        cur = conn.execute(
            "DELETE FROM analysis WHERE created_at < datetime('now', ?)",
            (f"-{int(retention_days)} days",),
        )
        conn.commit()
    removed = cur.rowcount or 0
    if removed:
        logger.info("retention cleanup removed %d analyses (older than %d days)",
                    removed, retention_days)
    return removed


def run_auto_jobs() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT name FROM keyword WHERE enabled = 1").fetchall()

    outcomes: list[dict] = []
    for row in rows:
        keyword = row["name"]
        try:
            outcome = collect_and_analyze(keyword, run_type="auto")
            outcomes.append({"keyword": keyword, "ok": True, "id": outcome["id"]})
        except Exception as exc:
            logger.exception("auto job failed for keyword=%s", keyword)
            outcomes.append({"keyword": keyword, "ok": False, "error": str(exc)})
    return outcomes
