from datetime import datetime

from pydantic import BaseModel, Field


class KeywordCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    enabled: bool = True


class KeywordUpdate(BaseModel):
    enabled: bool


class KeywordOut(BaseModel):
    id: int
    name: str
    enabled: bool
    created_at: datetime


class RunRequest(BaseModel):
    keyword: str = Field(min_length=1, max_length=100)


class SourcePaper(BaseModel):
    title: str
    url: str | None = None
    authors: list[str] = []


class SourceNews(BaseModel):
    title: str
    url: str | None = None


class Sources(BaseModel):
    papers: list[SourcePaper] = []
    news: list[SourceNews] = []


class AnalysisOut(BaseModel):
    id: int
    keyword: str
    result: str
    run_type: str
    sources: Sources | None = None
    tags: list[str] = []
    created_at: datetime


class AnalysisPage(BaseModel):
    items: list[AnalysisOut]
    total: int
    has_more: bool
    next_before_id: int | None = None
