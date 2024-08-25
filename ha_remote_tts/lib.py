"""Module for provisioning a RemoteTTS Client/Server"""

from aiohttp import ClientSession, web, ClientResponseError, ClientTimeout, ClientConnectionError
from asyncio import sleep
from typing import Callable, Awaitable, Tuple
import base64

from .exception import ApiError


class RemoteTTSClient:
	"""RemoteTTS Client class"""

	def __init__(self, host: str):
		"""
		:param host: API url
		"""
		self._host = host
		self._timeout = ClientTimeout(connect=5, total=30)
		self._session = ClientSession(host, timeout=self._timeout)

	async def close(self):
		await self._session.close()
		self._session = None

	async def verify_connection(self):
		try:
			async with self._session.get('/', timeout=self._timeout) as resp:
				resp.raise_for_status()
		except ClientConnectionError:
			await self.close()
			raise ApiError(status_code=404, body='Could not connect to server')
		except ClientResponseError as err:
			raise ApiError(status_code=err.status, body=err.message)

	async def synthesize(self, text: str) -> tuple[str, bytes]:
		"""Synthesize the inputted text into audio by calling the API located at host

		:param text: text to turn into spoken audio
		"""
		try:
			async with self._session.post(
				'/synthesize', data={'text': text}, timeout=self._timeout
			) as resp:
				data: dict = await resp.json(content_type='application/json; charset=utf-8')
				audio_b64 = data.get('audio')
				format = data.get('format')
				if audio_b64 is None or type(audio_b64) is not str:
					pass
				if format is None or type(format) is not str:
					pass

				audio = base64.b64decode(audio_b64)

				return format, audio
		except ClientConnectionError as err:
			await self.close()
			raise ApiError(status_code=404, body='Could not connect to server')
		except ClientResponseError as err:
			raise ApiError(status_code=err.status, body=err.message)


class RemoteTTSServer:
	"""RemoteTTS Server class"""

	def __init__(self, callback: Callable[[str], Tuple[bytes, str]]):
		"""Initialization method.
		Configures the routing table with the synthesize route.

		:param callback: Callback function for generating the tts audio
		"""
		self._app = web.Application()
		self._app.add_routes([web.post('/synthesize', self.synthesize), web.get('/', self.status)])
		self._callback = callback
		self._runner = web.AppRunner(self._app)

	async def status(self, request: web.Request) -> Awaitable[web.StreamResponse]:
		return web.json_response({'status': 'Ok'})

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
