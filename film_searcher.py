import re
from difflib import SequenceMatcher
import aiohttp

from get_token import get_poiskkino_token

class FilmSearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
            "Referer": "https://m3.frkp.site/"
        }
        self.EN_TO_RU = {
            "a": "а", "b": "б", "c": "к", "d": "д", "e": "е", "f": "ф",
            "g": "г", "h": "х", "i": "и", "j": "дж", "k": "к", "l": "л",
            "m": "м", "n": "н", "o": "о", "p": "п", "q": "к", "r": "р",
            "s": "с", "t": "т", "u": "у", "v": "в", "w": "в", "x": "кс",
            "y": "й", "z": "з",
        }
        self.RU_TO_EN = {v: k for k, v in self.EN_TO_RU.items()}

        self.BAD_WORDS_FOR_FILM = ['реакция']#, 'сериал', 'серия', 'трейлер', 'серии', 'serial']
        self.MIN_DURATION = 15 * 60  # минут

    def _get_movie_stub(self, query: str | None = None) -> dict:
        return {
            "id": 1,
            "title": query or "Фильм не найден",
            "original_title": None,
            "type": "unknown",
            "year": 1,
            "rating": {
                "kp": 1,
                "imdb": 1
            },
            "description": (
                "😔 К сожалению, по вашему запросу фильм не найден.\n\n"
                "Попробуйте:\n"
                "— уточнить название\n"
                "— написать название на английском\n"
                "— добавить год выпуска"
            ),
            "poster": "https://via.placeholder.com/600x900?text=No+Poster",
            "sources": {}
        }

    async def _search_rutube(self, query: str) -> dict | None:
        RUTUBE_SEARCH_URL = "https://rutube.ru/api/search/video/"


        params = {"query": query}

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(RUTUBE_SEARCH_URL, params=params, timeout=10) as response:
                response.raise_for_status()
                res = await response.json()

                for item in res.get("results", [])[:2]:
                    # print('------------- item')
                    # print(item)
                    # print('-------------')
                    title = item.get("title", "")
                    title_l = title.lower()
                    duration = item.get("duration", 0)

                    if any(bw.lower() in title_l for bw in self.BAD_WORDS_FOR_FILM):
                        continue
                    if duration < self.MIN_DURATION:
                        continue

                    video_url = item.get("video_url")
                    if not video_url:
                        continue

                    return {
                        "title": title,
                        "url": video_url,
                        "duration": duration
                    }

                return None


    async def _search_kkk_poisk(self, movie, id_or_name='id') -> str:
        if id_or_name == 'id':
            return f"https://m3.frkp.site/?id={movie}"
        if id_or_name == 'name':
            return f"https://m3.frkp.site/?name={movie}"

    def _translit_en_ru(self, word: str) -> str:
        result = ""
        for ch in word.lower():
            result += self.EN_TO_RU.get(ch, ch)
        return result

    def _translit_ru_en(self, word: str) -> str:
        result = ""
        i = 0
        while i < len(word):
            if word[i:i + 2].lower() in self.RU_TO_EN:
                result += self.RU_TO_EN[word[i:i + 2].lower()]
                i += 2
            else:
                result += self.RU_TO_EN.get(word[i].lower(), word[i])
                i += 1
        return result

    def _similar(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _is_valid_name(self, target: str, movie: dict) -> bool:
        names = [movie.get("name", "")]
        if movie.get("alternativeName"):
            names.append(movie["alternativeName"])
        if movie.get("enName"):
            names.append(movie["enName"])

        def split_words(s: str):
            return re.split(r"[\s\-]+", s.lower())

        target_words = split_words(target)

        ks = 0.7
        for name in names:
            name_words = split_words(name)
            for tw in target_words:
                for nw in name_words:
                    if (tw == nw
                        or tw == self._translit_ru_en(nw)
                        or self._translit_ru_en(tw) == nw
                        or self._similar(tw, nw) >= ks
                        or self._similar(tw, self._translit_ru_en(nw)) >= ks
                        or self._similar(self._translit_ru_en(tw), nw) >= ks):
                        return True
        return False

    async def _get_from_kinopoisk(self, query: str) -> dict | None:
        url = "https://api.poiskkino.dev/v1.4/movie/search"
        headers = {"X-API-KEY": get_poiskkino_token()}
        params = {
            "query": query,
            "limit": 5
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params, timeout=10) as resp:
                data = await resp.json()

        for movie in data.get("docs", []):
            # print('+=============  movie')
            # print(movie)
            # print('+============= ')
            if (not (movie is None)) and self._is_valid_name(query, movie):
                poster = movie.get("poster", {})
                poster_url = None if poster is None else poster.get("url")
                return {
                    "id": movie["id"],
                    "title": movie["name"],
                    'type': movie['type'],
                    "original_title": movie.get("enName"),
                    "year": movie.get("year"),
                    "description": movie.get("shortDescription") or movie.get("description"),
                    "poster": poster_url,
                    "rating": {
                        "kp": movie.get("rating", {}).get("kp"),
                        "imdb": movie.get("rating", {}).get("imdb"),
                    },
                    "external_ids": movie.get("externalId", {}),
                }

        return None

    async def _search_movie_descr(self, query: str) -> dict | None:
        movie = await self._get_from_kinopoisk(query)
        if not movie:
            return None

        movie["sources"] = {}
        return movie


    async def find_movie(self, name: str) -> dict | None:
        movie = await self._search_movie_descr(name)
        if not movie:
            return None

        movie_id = movie["id"]


        kkk_url = await self._search_kkk_poisk(movie_id)
        query = movie['type'] + ' ' + name + ' ' + str(movie['year'])
        # print(query)
        rutube_item = await self._search_rutube(query)

        movie["sources"]["m3.frkp.site"] = {
            "title": f"{movie['title']} ({movie['year']})",
            "url": kkk_url
        }

        if rutube_item:
            movie["sources"]["Rutube"] = {
                "title": rutube_item['title'],
                "url": rutube_item['url']
            }

        return movie
