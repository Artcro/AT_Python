from pathlib import Path
from typing import Tuple

import pandas as pd
from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError


def load_dataframes(engine) -> Tuple[pd.DataFrame, pd.DataFrame]:
    movies_df = pd.DataFrame()
    series_df = pd.DataFrame()
    console = Console()

    try:
        movies_df = pd.read_sql_table("movies", con=engine)
    except SQLAlchemyError as error:
        console.print("Erro ao ler tabela movies:", str(error), style="bold red")
    except ValueError as error:
        console.print("Erro ao ler tabela movies:", str(error), style="bold red")

    try:
        series_df = pd.read_sql_table("series", con=engine)
    except SQLAlchemyError as error:
        console.print("Erro ao ler tabela series:", str(error), style="bold red")
    except ValueError as error:
        console.print("Erro ao ler tabela series:", str(error), style="bold red")

    return movies_df, series_df


def classify_rating(rating: float) -> str:
    if rating >= 9.0:
        return "Obra-prima"
    if rating >= 8.0:
        return "Excelente"
    if rating >= 7.0:
        return "Bom"
    return "Mediano"


def add_category_column(movies_df: pd.DataFrame) -> pd.DataFrame:
    if movies_df.empty:
        return movies_df

    result_df = movies_df.copy()
    result_df["categoria"] = result_df["rating"].apply(classify_rating)
    return result_df


def show_top_movies(movies_df: pd.DataFrame) -> None:
    console = Console()

    if movies_df.empty:
        console.print("Nenhum filme carregado para análise.", style="bold yellow")
        return

    sorted_df = movies_df.sort_values(by="rating", ascending=False)
    filtered_df = sorted_df[sorted_df["rating"] > 9.0]
    head_df = filtered_df.head(5)

    console.rule("[bold cyan]Top 5 filmes com nota maior que 9.0[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Título")
    table.add_column("Ano", justify="right")
    table.add_column("Nota", justify="right")

    for index in head_df.index:
        row = head_df.loc[index]
        title_value = str(row["title"])
        year_value = int(row["year"])
        rating_value = float(row["rating"])
        formatted_rating = f"{rating_value:.1f}"
        table.add_row(title_value, str(year_value), formatted_rating)

    console.print(table)


def show_title_rating_category(movies_df: pd.DataFrame, limit: int) -> None:
    console = Console()

    if movies_df.empty:
        console.print("Nenhum filme disponível para exibir categoria.", style="bold yellow")
        return

    head_df = movies_df.head(limit)
    console.rule("[bold cyan]Title, rating e categoria dos primeiros filmes[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Título")
    table.add_column("Nota", justify="right")
    table.add_column("Categoria")

    for index in head_df.index:
        row = head_df.loc[index]
        title_value = str(row["title"])
        rating_value = float(row["rating"])
        category_value = str(row["categoria"])
        formatted_rating = f"{rating_value:.1f}"
        table.add_row(title_value, formatted_rating, category_value)

    console.print(table)


def build_category_summary(movies_df: pd.DataFrame) -> pd.DataFrame:
    if movies_df.empty:
        return pd.DataFrame()

    if "categoria" not in movies_df.columns:
        return pd.DataFrame()

    grouped = movies_df.groupby(["categoria", "year"])
    counts = grouped["id"].count().reset_index(name="quantidade")
    pivot_table = counts.pivot(
        index="categoria",
        columns="year",
        values="quantidade",
    )
    pivot_table = pivot_table.fillna(0)
    pivot_table = pivot_table.astype(int)

    return pivot_table


def export_dataframes(
        movies_df: pd.DataFrame,
        series_df: pd.DataFrame,
        output_dir: Path,
) -> None:
    console = Console()
    output_dir.mkdir(parents=True, exist_ok=True)

    movies_csv_path = output_dir / "movies.csv"
    series_csv_path = output_dir / "series.csv"
    movies_json_path = output_dir / "movies.json"
    series_json_path = output_dir / "series.json"

    try:
        movies_df.to_csv(movies_csv_path, index=False)
        console.print(f"Arquivo salvo: {movies_csv_path}", style="green")
    except OSError as error:
        console.print("Erro ao salvar movies.csv:", str(error), style="bold red")

    try:
        series_df.to_csv(series_csv_path, index=False)
        console.print(f"Arquivo salvo: {series_csv_path}", style="green")
    except OSError as error:
        console.print("Erro ao salvar series.csv:", str(error), style="bold red")

    try:
        movies_df.to_json(movies_json_path, orient="records", force_ascii=False)
        console.print(f"Arquivo salvo: {movies_json_path}", style="green")
    except OSError as error:
        console.print("Erro ao salvar movies.json:", str(error), style="bold red")

    try:
        series_df.to_json(series_json_path, orient="records", force_ascii=False)
        console.print(f"Arquivo salvo: {series_json_path}", style="green")
    except OSError as error:
        console.print("Erro ao salvar series.json:", str(error), style="bold red")
