from pathlib import Path
from typing import List

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from models import Movie, Series


Base = declarative_base()


class MovieModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)


class SeriesModel(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    seasons = Column(Integer, nullable=False)
    episodes = Column(Integer, nullable=False)


def create_sqlite_engine(database_path: Path):
    database_url: str = f"sqlite:///{database_path}"
    engine = create_engine(database_url, echo=False, future=True)
    return engine


def create_database_schema(engine) -> None:
    Base.metadata.create_all(engine)


def insert_movies_and_series(
    engine,
    movies: List[Movie],
    series_list: List[Series],
) -> None:
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session: Session = session_factory()
    try:
        for movie in movies:
            movie_model = MovieModel(
                title=movie.title,
                year=movie.year,
                rating=movie.rating,
            )
            try:
                session.add(movie_model)
                session.commit()
            except IntegrityError:
                session.rollback()
            except SQLAlchemyError:
                session.rollback()

        for series in series_list:
            series_model = SeriesModel(
                title=series.title,
                year=series.year,
                seasons=series.seasons,
                episodes=series.episodes,
            )
            try:
                session.add(series_model)
                session.commit()
            except IntegrityError:
                session.rollback()
            except SQLAlchemyError:
                session.rollback()
    finally:
        session.close()
