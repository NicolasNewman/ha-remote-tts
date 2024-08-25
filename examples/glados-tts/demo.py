from ha_remote_tts import RemoteTTSServer
import asyncio
import time


# see: https://github.com/R2D2FISH/glados-tts
from glados import tts_runner

glados = tts_runner(False, True)


def synthesize(line):
	if line == '':
		return b'', 'unknown'
	audio = glados.run_tts(line, 1.0).raw_data

	return audio, 'wav'


server = RemoteTTSServer(synthesize)
asyncio.run(server.start('localhost', '8080'))
