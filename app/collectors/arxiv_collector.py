from dataclasses import dataclass

import arxiv

from ..config import settings


@dataclass
class Paper:
    title: str
    summary: str
    url: str
    authors: list[str]


def fetch(keyword: str, max_results: int | None = None) -> list[Paper]:
    limit = max_results or settings.arxiv_max_results
    search = arxiv.Search(
        query=keyword,
        max_results=limit,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    papers: list[Paper] = []
    for result in search.results():
        papers.append(
            Paper(
                title=result.title.strip(),
                summary=result.summary.strip(),
                url=result.entry_id,
                authors=[a.name for a in result.authors],
            )
        )
    return papers
