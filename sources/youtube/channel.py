import re
from datetime import datetime

import httpx

from .. import SourceResult
from ..abc import Source
from ..exceptions import SourceInitException, SourceGatherException


async def check_username(username):
    pattern = r"@\w*"
    if not re.fullmatch(pattern, username):
        return False

    url = "https://www.youtube.com/" + username

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        return False

    return True


def highest_resolution_thumbnail(thumbnail_dict):
    keys = [
        "maxres",
        "standard",
        "high",
        "medium",
        "default"
    ]

    for key in keys:
        if key in thumbnail_dict:
            return thumbnail_dict[key]["url"]

    return None


class YoutubeChannelSource(Source):
    def __init__(self, api_key, uploads_playlist_id, name, gathering_period):
        super().__init__(name, gathering_period)
        # YoutubeApi возвращает время с временной зоной.
        # Для корректной работы, last_gathered всегда должен быть с временной зоной
        self.last_gathered = self.last_gathered.astimezone()
        self.api_key = api_key
        self.uploads_playlist_id = uploads_playlist_id

    @classmethod
    async def create(cls, api_key, username, name, gathering_period):
        if not await check_username(username):
            raise SourceInitException("Такого пользователя не существует")

        async with httpx.AsyncClient() as client:
            search_url = (
                f'https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={username}&type'
                f'=channel&key={api_key}')
            resp = await client.get(search_url)
            if resp.status_code != 200:
                raise SourceInitException(f"Ошибка youtube api при поиске канала: {resp.status_code}")
            resp = resp.json()
            total_results = resp["pageInfo"]["totalResults"]
            if total_results < 1:
                raise SourceInitException("Пользователь не найден")
            snippet = resp["items"][0]["snippet"]
            channel_id = snippet["channelId"]
            name = name or snippet["title"]

            channels_url = (f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&"
                            f"maxResults=1&key={api_key}")

            resp = await client.get(channels_url)
            if resp.status_code != 200:
                raise SourceInitException(f"Ошибка youtube api при получении информации о канале: {resp.status_code}")
            resp = resp.json()

            total_results = resp["pageInfo"]["totalResults"]
            if total_results < 1:
                raise SourceInitException("Канал не найден")

            uploads_playlist_id = resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            return cls(api_key, uploads_playlist_id, name, gathering_period)

    def gather_from_page(self, items, result: list[SourceResult]) -> tuple[bool, datetime]:
        last_time = None
        finished = False
        for item in items:
            snippet = item["snippet"]
            published_at = datetime.fromisoformat(snippet["publishedAt"])
            if self.last_gathered >= published_at:
                finished = True
                break

            # В плейлисте uploads видео по убыванию времени публикации. Первое - самое позднее
            if last_time is None:
                last_time = published_at

            result.append(
                SourceResult(
                    "Видео",
                    snippet["title"],
                    f"https://youtube.com/watch?v={snippet['resourceId']['videoId']}",
                    published_at,
                    snippet["description"],
                    highest_resolution_thumbnail(snippet["thumbnails"])
                )
            )

        return finished or last_time is None, last_time

    async def _gather_data(self) -> tuple[list[SourceResult], datetime]:
        playlist_items_url = (f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50"
                              f"&playlistId={self.uploads_playlist_id}&key={self.api_key}")

        async with httpx.AsyncClient() as client:
            resp = await client.get(playlist_items_url)
            if resp.status_code != 200:
                raise SourceGatherException(f"Ошибка youtube api при сборе из \"{self.name}\": {resp.status_code}")

            resp = resp.json()
            result = []

            # На одной странице ответа до 50 видео.
            # Если с момента предыдущего сбора было выпущено больше 50 видео, нужно смотреть следующие страницы
            # (если они есть)
            finished, last_time = self.gather_from_page(resp["items"], result)
            while not finished and "nextPageToken" in resp:
                new_page_url = playlist_items_url + f"&pageToken={resp['nextPageToken']}"
                resp = await client.get(new_page_url)
                if resp.status_code != 200:
                    raise SourceGatherException(f"Ошибка youtube api при сборе из \"{self.name}\": {resp.status_code}")

                resp = resp.json()
                finished, _ = self.gather_from_page(resp["items"], result)

            return result, last_time
