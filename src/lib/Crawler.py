import os
from typing import Self

import requests

from lib.Logger import Logger
from lib.Repository import Repository


class Crawler:
    # GitHub API credentials
    token = None

    # GitHub API routes
    repos_url = 'https://api.github.com/search/repositories'

    # Optional filters
    __min_stars = None
    __max_stars = None
    __lang = None

    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')

    @staticmethod
    def init():
        return Crawler()

    def max_stars(self, num: int) -> Self:
        self.__max_stars = num
        return self

    def min_stars(self, num: int) -> Self:
        self.__min_stars = num
        return self

    def lang(self, lang: str) -> Self:
        self.__lang = lang
        return self

    def __compose_filters(self) -> str:
        query_parts = []
        if self.__min_stars is not None and self.__max_stars is not None:
            query_parts.append(f"stars:{self.__min_stars}..{self.__max_stars}")
        else:
            if self.__min_stars is not None:
                query_parts.append(f"stars:>={self.__min_stars}")
            if self.__max_stars is not None:
                query_parts.append(f"stars:<={self.__max_stars}")
        if self.__lang is not None:
            query_parts.append(f"language:{self.__lang}")
        if not query_parts:
            query_parts.append("stars:>=0")
        return " ".join(query_parts)

    def __request_headers(self) -> dict:
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def __fetch_page(self, page: int, per_page: int) -> list:
        headers = self.__request_headers()
        params = {
            "q": self.__compose_filters(),
            "sort": "updated",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }

        response = requests.get(self.repos_url, params=params, headers=headers)
        if response.status_code != 200:
            Logger.error(f"Error fetching repositories on page {page}: {response.status_code}")
            return []
        return response.json().get("items", [])

    def crawl(self, num: int) -> tuple[dict, int]:
        repos = {}

        page = 1
        page_size = 200

        remaining_repos = num
        while remaining_repos > 0:
            items = self.__fetch_page(page, page_size)
            if not items:
                break

            for item in items:
                if remaining_repos <= 0:
                    break

                repo = Repository()
                repo.name = item.get("name")
                repo.url = item.get("html_url")
                repo.author = item.get("owner", {}).get("login")
                repo.stars = item.get("stargazers_count")
                repo.lang = item.get("language")
                repos[repo.key()] = repo
                remaining_repos -= 1

            page += 1

        Logger.info(f"{len(repos)} suitable repositories found.")
        return repos, len(repos)
