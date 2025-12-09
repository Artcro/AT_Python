from pathlib import Path
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import RequestException


def download_html_to_file(url: str, destination: Path) -> None:
    destination_dir: Path = destination.parent
    destination_dir.mkdir(parents=True, exist_ok=True)

    headers: Dict[str, str] = {}
    headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
    headers["Accept-Language"] = "en-US,en;q=0.9"

    try:
        response: Response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text_value: str = response.text
    except RequestException as error:
        raise RuntimeError(str(error)) from error

    with open(destination, "w", encoding="utf-8") as file:
        file.write(text_value)


def load_html_from_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as file:
        content: str = file.read()
    return content


def extract_chart_items_from_html(html: str, limit: int) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")

    items: List[Dict[str, Any]] = []
    count: int = 0

    li_elements = soup.find_all("li")
    for li in li_elements:
        class_attr = li.get("class")
        has_summary_class = False
        if class_attr is not None:
            for class_name in class_attr:
                if class_name == "ipc-metadata-list-summary-item":
                    has_summary_class = True
                    break

        if not has_summary_class:
            continue

        title_tag = li.find("h3")
        if title_tag is None:
            continue
        title_text_value = title_tag.get_text(strip=True)

        year_value = None
        span_elements = li.find_all("span")
        for span in span_elements:
            span_classes = span.get("class")
            if span_classes is None:
                continue

            contains_metadata_class = False
            for span_class in span_classes:
                if "cli-title-metadata-item" in span_class:
                    contains_metadata_class = True
                    break

            if not contains_metadata_class:
                continue

            year_text = span.get_text(strip=True)
            if len(year_text) >= 4:
                year_slice = year_text[:4]
            else:
                year_slice = year_text

            try:
                year_candidate = int(year_slice)
            except ValueError:
                year_candidate = None

            if year_candidate is not None:
                year_value = year_candidate
                break

        if year_value is None:
            continue

        rating_span = li.find("span", class_="ipc-rating-star--rating")
        if rating_span is None:
            continue
        rating_text = rating_span.get_text(strip=True)
        rating_text_normalized = rating_text.replace(",", ".")
        try:
            rating_value = float(rating_text_normalized)
        except ValueError:
            continue

        item_info: Dict[str, Any] = {}
        item_info["title"] = title_text_value
        item_info["year"] = year_value
        item_info["rating"] = rating_value

        items.append(item_info)

        count = count + 1
        if count >= limit:
            break

    return items
