"""Module for provisioning a RemoteTTS Client/Server"""

from aiohttp import ClientSession, web
from typing import Callable, Awaitable, Tuple


class RemoteTTSClient:
	"""RemoteTTS Client class"""

	def __init__(self, host: str):
		"""
		:param host: API url
		"""
		self._host = host
		self._session = ClientSession(host)

	async def synthesize(self, text: str) -> str:
		"""Synthesize the inputted text into audio by calling the API located at host

		:param text: text to turn into spoken audio
		"""
		headers = {}

		async with self._session.post('/synthesize', json={'text': text}) as resp:
			data: dict = await resp.json()
			audio = data.get('audio')
			format = data.get('format')
			if audio is None or type(audio) is not bytes:
				pass
			if format is None or type(format) is not str:
				pass

			return format, audio


# https://docs.aiohttp.org/en/stable/web_quickstart.html#file-uploads
class RemoteTTSServer:
	"""RemoteTTS Server class"""

	def __init__(self, callback: Callable[[str], Tuple[bytes, str]]):
		"""Initialization method.
		Configures the routing table with the synthesize route.

		:param callback: Callback function for generating the tts audio
		"""
		self._app = web.Application()
		self._app.add_routes([web.post('/synthesize', self.synthesize)])
		self._callback = callback

	async def synthesize(self, request: web.Request) -> Awaitable[web.StreamResponse]:
		"""Synthesization POST route

		:param request: aiohttp request
		"""

		data = await request.post()
		text = data.get('text')
		if text is None:
			# TODO handle errors
			raise web.HTTPBadRequest(body="POST parameter 'text' is not defined")
		if type(text) is not str:
			raise web.HTTPUnsupportedMediaType(body="POST parameter 'text' is not a string")

		audio, format = self._callback(text)
		return web.json_response({'format': format, 'audio': audio})
