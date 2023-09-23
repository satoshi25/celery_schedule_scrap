from typing import List
from datetime import date
from sqlalchemy.orm import Session

from celery import chain

from src.celery_config import celery_task
from src.service.article import ScrapArticle
from src.repository.connection import SessionFactory
from src.repository.article_repository import ArticleModel, Article


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
    article_session: Session = SessionFactory()

    def save_articles(session: Session, articles: List[dict]) -> None:
        data_list: List[dict] = []
        for article in articles:
            row = {
                "title": article.get("title"),
                "image": article.get("image"),
                "journal": article.get("journal"),
                "url": article.get("url"),
                "view": article.get("view"),
                "publish_date": article.get("publish_date")
            }
            data_list.append(row)
        session.bulk_insert_mappings(Article, data_list)
        session.commit()

    try:
        save_articles(session=article_session, articles=data)
    finally:
        article_session.close()

    return data


@celery_task.task
def scrap_and_save_pipeline_task():
    pipeline = chain(scrap_article_task.s(), save_article_db_task.s())
    pipeline.apply_async()
