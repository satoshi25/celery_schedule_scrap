from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from datetime import date


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