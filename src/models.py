class TV:
    def __init__(self, title: str, year: int) -> None:
        self.title: str = title
        self.year: int = year

    def __str__(self) -> str:
        return f"{self.title} ({self.year})"


class Movie(TV):
    def __init__(self, title: str, year: int, rating: float) -> None:
        super().__init__(title, year)
        self.rating: float = rating

    def __str__(self) -> str:
        formatted_rating: str = f"{self.rating:.1f}"
        return f"{self.title} ({self.year}) - Nota: {formatted_rating}"


class Series(TV):
    def __init__(self, title: str, year: int, seasons: int, episodes: int) -> None:
        super().__init__(title, year)
        self.seasons: int = seasons
        self.episodes: int = episodes

    def __str__(self) -> str:
        return (
            f"{self.title} ({self.year}) - "
            f"Temporadas: {self.seasons}, Episódios: {self.episodes}"
        )
