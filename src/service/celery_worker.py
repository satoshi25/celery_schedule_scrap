from typing import List
from datetime import date
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, String, Integer, Date
from celery import chain
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from src.celery_config import celery_task
from src.service.article import ScrapArticle


load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

engine = create_engine(DB_URL, echo=False)

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


class ArticleModel(BaseModel):
    title: str
    image: str
    journal: str
    url: str
    view: int
    publish_date: date


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    image = Column(String(2083), nullable=False)
    journal = Column(String(50), nullable=False)
    url = Column(String(2083), nullable=False)
    view = Column(Integer, nullable=False)
    publish_date = Column(Date, nullable=False)

    @classmethod
    def create_article(cls, article: dict) -> "Article":
        return cls(
            title=article.get("title"),
            image=article.get("image"),
            journal=article.get("journal"),
            url=article.get("url"),
            view=article.get("view"),
            publish_date=article.get("publish_date")
        )


@celery_task.task
def scrap_article_task() -> List[dict]:
    scrap_data = ScrapArticle().scrap_articles()

    data = []
    for articles in scrap_data:
        journal = list(articles.keys())[0]
        for article in articles[journal]:
            publish_date = date.fromisoformat(article.get("publish_date"))
            converted_article = ArticleModel(
                title=article.get("title"),
                image=article.get("image"),
                journal=article.get("journal"),
                url=article.get("url"),
                view=article.get("view"),
                publish_date=publish_date
            )
            data.append(converted_article.dict())

    return data


@celery_task.task
def save_article_db_task(data: list[dict]) -> List[dict]:
    session: Session = SessionFactory()

    def save_articles(session: Session, articles: List[dict]) -> None:
        data: List[dict] = []
        for article in articles:
            row = {
                "title": article.get("title"),
                "image": article.get("image"),
                "journal": article.get("journal"),
                "url": article.get("url"),
                "view": article.get("view"),
                "publish_date": article.get("publish_date")
            }
            data.append(row)
        session.bulk_insert_mappings(Article, data)
        session.commit()

    try:
        save_articles(session=session, articles=data)
    finally:
        session.close()

    return data


@celery_task.task
def scrap_and_save_pipeline_task():
    pipeline = chain(scrap_article_task.s(), save_article_db_task.s())
    pipeline.apply_async()
