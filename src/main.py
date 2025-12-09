from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

from analysis import (
    load_dataframes,
    add_category_column,
    show_top_movies,
    show_title_rating_category,
    build_category_summary,
    export_dataframes,
)
from config_loader import Config, load_config
from database import (
    create_sqlite_engine,
    create_database_schema,
    insert_movies_and_series,
)
from models import Movie, Series, TV
from scraping import (
    load_html_from_file,
    extract_chart_items_from_html,
    download_html_to_file,
)

console = Console()


def create_movie_objects(raw_movies: List[Dict[str, Any]]) -> List[Movie]:
    movies: List[Movie] = []
    for movie_data in raw_movies:
        title_value = str(movie_data["title"])
        year_value = int(movie_data["year"])
        rating_value = float(movie_data["rating"])
        movie = Movie(title=title_value, year=year_value, rating=rating_value)
        movies.append(movie)
    return movies


def create_series_from_scraping(raw_series: List[Dict[str, Any]]) -> List[Series]:
    series_list: List[Series] = []
    for series_data in raw_series:
        title_value = str(series_data["title"])
        year_value = int(series_data["year"])
        seasons_value = 1
        episodes_value = 1
        series = Series(
            title=title_value,
            year=year_value,
            seasons=seasons_value,
            episodes=episodes_value,
        )
        series_list.append(series)
    return series_list


def show_basic_movies_info(raw_movies: List[Dict[str, Any]]) -> None:
    console.rule("[bold cyan]Primeiros 10 títulos de filmes (Exercício 1)[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Posição", justify="right")
    table.add_column("Título")

    limit = 10
    index_value = 0
    while index_value < limit and index_value < len(raw_movies):
        movie_data = raw_movies[index_value]
        title_value = str(movie_data["title"])
        position_text = str(index_value + 1)
        table.add_row(position_text, title_value)
        index_value = index_value + 1

    console.print(table)
    console.print()

    console.rule("[bold cyan]Primeiros 5 filmes com título, ano e nota (Exercício 2)[/bold cyan]")

    table_detailed = Table(show_header=True, header_style="bold magenta")
    table_detailed.add_column("Posição", justify="right")
    table_detailed.add_column("Título")
    table_detailed.add_column("Ano", justify="right")
    table_detailed.add_column("Nota", justify="right")

    second_limit = 5
    index_value = 0
    while index_value < second_limit and index_value < len(raw_movies):
        movie_data = raw_movies[index_value]
        title_value = str(movie_data["title"])
        year_value = int(movie_data["year"])
        rating_value = float(movie_data["rating"])
        formatted_rating = f"{rating_value:.1f}"
        position_text = str(index_value + 1)
        table_detailed.add_row(position_text, title_value, str(year_value), formatted_rating)
        index_value = index_value + 1

    console.print(table_detailed)
    console.print()


def show_basic_series_info(raw_series: List[Dict[str, Any]]) -> None:
    if len(raw_series) == 0:
        console.print("Nenhuma série carregada do IMDb Top 250.", style="bold yellow")
        console.print()
        return

    console.rule("[bold cyan]Primeiros 10 títulos de séries (Top 250 séries)[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Posição", justify="right")
    table.add_column("Título")

    limit = 10
    index_value = 0
    while index_value < limit and index_value < len(raw_series):
        series_data = raw_series[index_value]
        title_value = str(series_data["title"])
        position_text = str(index_value + 1)
        table.add_row(position_text, title_value)
        index_value = index_value + 1

    console.print(table)
    console.print()

    console.rule("[bold cyan]Primeiras 5 séries com título, ano e nota[/bold cyan]")

    table_detailed = Table(show_header=True, header_style="bold magenta")
    table_detailed.add_column("Posição", justify="right")
    table_detailed.add_column("Título")
    table_detailed.add_column("Ano", justify="right")
    table_detailed.add_column("Nota", justify="right")

    second_limit = 5
    index_value = 0
    while index_value < second_limit and index_value < len(raw_series):
        series_data = raw_series[index_value]
        title_value = str(series_data["title"])
        year_value = int(series_data["year"])
        rating_value = float(series_data["rating"])
        formatted_rating = f"{rating_value:.1f}"
        position_text = str(index_value + 1)
        table_detailed.add_row(position_text, title_value, str(year_value), formatted_rating)
        index_value = index_value + 1

    console.print(table_detailed)
    console.print()


def show_catalog(catalog: List[TV]) -> None:
    console.rule("[bold cyan]Catálogo completo de filmes e séries (Exercício 5)[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tipo")
    table.add_column("Título")
    table.add_column("Ano", justify="right")
    table.add_column("Detalhes")

    for item in catalog:
        item_type = "Outro"
        if isinstance(item, Movie):
            item_type = "Filme"
        elif isinstance(item, Series):
            item_type = "Série"

        title_value = item.title
        year_value = item.year
        details_text = str(item)

        table.add_row(item_type, title_value, str(year_value), details_text)

    console.print(table)
    console.print()


def ensure_movies_html(config: Config) -> bool:
    try:
        download_html_to_file(config.imdb_top_250_url, config.html_source_path)
        console.print("HTML de filmes atualizado a partir da web.", style="green")
        return True
    except RuntimeError as error:
        console.print("Não foi possível atualizar o HTML de filmes a partir da web.", style="bold red")
        console.print(str(error), style="red")
        if not config.html_source_path.exists():
            console.print("Arquivo HTML local de filmes não encontrado. Encerrando execução.", style="bold red")
            return False
        return True


def ensure_series_html(config: Config) -> bool:
    try:
        download_html_to_file(
            config.imdb_top_250_series_url,
            config.series_html_source_path,
        )
        console.print("HTML de séries atualizado a partir da web.", style="green")
        return True
    except RuntimeError as error:
        console.print("Não foi possível atualizar o HTML de séries a partir da web.", style="bold yellow")
        console.print(str(error), style="yellow")
        if not config.series_html_source_path.exists():
            console.print(
                "Arquivo HTML local de séries não encontrado. Continuando apenas com filmes.",
                style="bold yellow",
            )
            return False
        return True


def load_raw_items_from_html(path: Path, limit: int) -> List[Dict[str, Any]]:
    html_content: str = load_html_from_file(path)
    raw_items: List[Dict[str, Any]] = extract_chart_items_from_html(
        html=html_content,
        limit=limit,
    )
    return raw_items


def build_series_list(scraped_series: List[Series]) -> List[Series]:
    series_list: List[Series] = []
    for series in scraped_series:
        series_list.append(series)
    return series_list


def build_catalog(movies: List[Movie], series_list: List[Series]) -> List[TV]:
    catalog: List[TV] = []
    for movie in movies:
        catalog.append(movie)
    for series in series_list:
        catalog.append(series)
    return catalog


def show_dataframe_preview(dataframe, name: str, exercise_label: str) -> None:
    if dataframe is None:
        console.print("DataFrame de " + name + " não foi carregado.", style="bold yellow")
        console.print()
        return

    if dataframe.empty:
        console.print("DataFrame de " + name + " está vazio.", style="bold yellow")
        console.print()
        return

    title_text = "[bold cyan]Primeiras 5 linhas de " + name + " (" + exercise_label + ")[/bold cyan]"
    console.rule(title_text)

    table = Table(show_header=True, header_style="bold magenta")

    for column_name in dataframe.columns:
        table.add_column(str(column_name))

    head_df = dataframe.head(5)
    for index in head_df.index:
        row = head_df.loc[index]
        row_values: List[str] = []
        for column_name in dataframe.columns:
            value = row[column_name]
            row_values.append(str(value))
        table.add_row(*row_values)

    console.print(table)
    console.print()


def show_summary_table(summary_table) -> None:
    if summary_table is None:
        console.print("Não foi possível construir o resumo por categoria.", style="bold yellow")
        console.print()
        return

    if summary_table.empty:
        console.print("Não foi possível construir o resumo por categoria.", style="bold yellow")
        console.print()
        return

    console.rule("[bold cyan]Resumo de filmes por categoria e ano (Exercício 10)[/bold cyan]")

    years: List[int] = []
    for column_year in summary_table.columns:
        years.append(column_year)

    max_columns_per_table = 8
    start_index = 0

    while start_index < len(years):
        end_index = start_index + max_columns_per_table
        if end_index > len(years):
            end_index = len(years)

        subset_years: List[int] = []
        index_value = start_index
        while index_value < end_index:
            subset_years.append(years[index_value])
            index_value = index_value + 1

        table_summary = Table(show_header=True, header_style="bold magenta")
        table_summary.add_column("Categoria")

        for year in subset_years:
            table_summary.add_column(str(year), justify="right")

        for category in summary_table.index:
            row_values: List[str] = []
            row_values.append(str(category))
            for year in subset_years:
                value = summary_table.loc[category, year]
                row_values.append(str(value))
            table_summary.add_row(*row_values)

        console.print(table_summary)
        console.print()

        start_index = end_index


def main() -> None:
    base_dir: Path = Path(__file__).resolve().parent.parent
    config_path: Path = base_dir / "config.json"
    config: Config = load_config(config_path)

    movies_html_ok = ensure_movies_html(config)
    if not movies_html_ok:
        return

    series_html_ok = ensure_series_html(config)

    raw_movies: List[Dict[str, Any]] = load_raw_items_from_html(
        path=config.html_source_path,
        limit=config.n_filmes,
    )

    raw_series: List[Dict[str, Any]] = []
    if series_html_ok and config.series_html_source_path.exists():
        raw_series = load_raw_items_from_html(
            path=config.series_html_source_path,
            limit=config.n_filmes,
        )

    show_basic_movies_info(raw_movies)
    show_basic_series_info(raw_series)

    movies: List[Movie] = create_movie_objects(raw_movies)
    scraped_series: List[Series] = create_series_from_scraping(raw_series)
    series_list: List[Series] = build_series_list(scraped_series)

    catalog: List[TV] = build_catalog(movies, series_list)
    show_catalog(catalog)

    engine = create_sqlite_engine(config.database_path)
    create_database_schema(engine)
    insert_movies_and_series(engine, movies, series_list)

    movies_df, series_df = load_dataframes(engine)

    show_dataframe_preview(movies_df, name="movies", exercise_label="Exercício 7")
    show_dataframe_preview(series_df, name="series", exercise_label="Exercício 7")

    show_top_movies(movies_df)

    movies_with_category = add_category_column(movies_df)
    show_title_rating_category(movies_with_category, limit=10)

    summary_table = build_category_summary(movies_with_category)
    show_summary_table(summary_table)

    export_dataframes(
        movies_df=movies_with_category,
        series_df=series_df,
        output_dir=config.output_directory,
    )
    console.print("Processo concluído.", style="bold green")


if __name__ == "__main__":
    main()
