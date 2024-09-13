import json
from . import JSONUtils
from aiohttp import ClientSession
from Player.InvidiousAPI.Objects import *
from Core.Utils import clean_url

class InvidiousError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Invidious:
    _session: ClientSession

    def __init__(self, instance) -> None:
        self._session = ClientSession(instance)

    async def fetch_video(self, id: str, proxy: bool = True) -> InvFullVideo:
        video : InvFullVideo
        url = f"/api/v1/videos/{id}?local={proxy.__str__().lower()}"

        try:
            async with self._session.get(url) as response:
                response_data: bytes = await response.read()

                if not response.ok:
                    if "application/json" in response.content_type:
                        error = json.loads(response_data)["error"]
                        raise InvidiousError(error)
                    else:
                        response.raise_for_status()

                video = JSONUtils.json_deserialize(response_data, InvFullVideo)
        except Exception as ex:
            raise InvidiousError("Failed to perform the fetch request/parse the response") from ex

        try:
            if proxy:
                for format in video.adaptiveFormats:
                    format.url = clean_url(format.url)
        except Exception as ex:
            raise InvidiousError("Failed to clean the adaptive format URLs") from ex

        return video
    
    async def close(self):
        await self._session.close()