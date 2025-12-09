from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import json


@dataclass
class Config:
    imdb_top_250_url: str
    imdb_top_250_series_url: str
    n_filmes: int
    html_source_path: Path
    series_html_source_path: Path
    database_path: Path
    output_directory: Path


def load_config(config_path: Path) -> Config:
    with open(config_path, "r", encoding="utf-8") as file:
        raw_data: Dict[str, Any] = json.load(file)

    base_dir: Path = config_path.parent

    url_movies_value: str = ""
    if "imdb_top_250_url" in raw_data:
        url_movies_value = str(raw_data["imdb_top_250_url"])

    url_series_value: str = ""
    if "imdb_top_250_series_url" in raw_data:
        url_series_value = str(raw_data["imdb_top_250_series_url"])

    n_filmes_value: int = 250
    if "n_filmes" in raw_data:
        n_filmes_value = int(raw_data["n_filmes"])

    html_movies_rel_path_value: str = "data/imdb_top_250_movies.html"
    if "html_source_path" in raw_data:
        html_movies_rel_path_value = str(raw_data["html_source_path"])
    html_movies_path: Path = (base_dir / html_movies_rel_path_value).resolve()

    html_series_rel_path_value: str = "data/imdb_top_250_tv.html"
    if "series_html_source_path" in raw_data:
        html_series_rel_path_value = str(raw_data["series_html_source_path"])
    html_series_path: Path = (base_dir / html_series_rel_path_value).resolve()

    db_rel_path_value: str = "data/imdb.db"
    if "database_path" in raw_data:
        db_rel_path_value = str(raw_data["database_path"])
    db_path: Path = (base_dir / db_rel_path_value).resolve()

    output_rel_path_value: str = "data"
    if "output_directory" in raw_data:
        output_rel_path_value = str(raw_data["output_directory"])
    output_dir: Path = (base_dir / output_rel_path_value).resolve()

    config = Config(
        imdb_top_250_url=url_movies_value,
        imdb_top_250_series_url=url_series_value,
        n_filmes=n_filmes_value,
        html_source_path=html_movies_path,
        series_html_source_path=html_series_path,
        database_path=db_path,
        output_directory=output_dir,
    )
    return config
