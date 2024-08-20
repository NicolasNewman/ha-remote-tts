"""Module for provisioning a RemoteTTS Client/Server"""

from aiohttp import ClientSession, web
from asyncio import sleep
from typing import Callable, Awaitable, Tuple
import base64


class RemoteTTSClient:
	"""RemoteTTS Client class"""

	def __init__(self, host: str):
		"""
		:param host: API url
		"""
		self._host = host

	async def synthesize(self, text: str) -> tuple[str, bytes]:
		"""Synthesize the inputted text into audio by calling the API located at host

		:param text: text to turn into spoken audio
		"""
		async with ClientSession(self._host) as session:
			async with session.post('/synthesize', data={'text': text}) as resp:
				data: dict = await resp.json(content_type='application/json; charset=utf-8')
				audio_b64 = data.get('audio')
				format = data.get('format')
				if audio_b64 is None or type(audio_b64) is not str:
					pass
				if format is None or type(format) is not str:
					pass

				audio = base64.b64decode(audio_b64)

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
		self._runner = web.AppRunner(self._app)

	async def synthesize(self, request: web.Request) -> Awaitable[web.StreamResponse]:
		"""Synthesization POST route

		:param request: aiohttp request
		"""
		data = await request.post()
		text = data.get('text')
		if text is None:
			return web.HTTPBadRequest(body="POST parameter 'text' is not defined")
		if type(text) is not str:
			return web.HTTPUnsupportedMediaType(body="POST parameter 'text' is not a string")

		audio, format = self._callback(text)
		audio_str = base64.b64encode(audio)
		return web.json_response({'format': format, 'audio': audio_str.decode('ascii')})

	async def start(self, ip: str = 'localhost', port: str = '8080'):
		await self._runner.setup()
		site = web.TCPSite(self._runner, ip, port)
		await site.start()

		while True:
			await sleep(3600)

	async def stop(self):
		await self._runner.cleanup()
