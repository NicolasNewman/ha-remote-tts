# ha-remote-tts

|         |   |
| ------- | - |
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/ha-remote-tts.svg)](https://pypi.org/project/ha-remote-tts/) [![PyPI Downloads](https://img.shields.io/pypi/dm/ha-remote-tts.svg?label=PyPI%20downloads)](https://pypi.org/project/ha-remote-tts/) |
| Meta    | [![License - MIT](https://img.shields.io/pypi/l/ha-remote-tts.svg)](https://github.com/NicolasNewman/ha-remote-tts/blob/main/LICENSE) |

## What is it?

API wrapper for the Remote TTS integration of Home Assistant

## Usage

### API

- POST: `/synthesize`
  - request:
    - `text`: The text to synthesize audio for
  - response (json):
    - `format`: The file format of the generated audio
    - `audio`: base64 encoded string of the raw audio

### Server

This is the class end-users should use to serve their own remote TTS engine.

```python
from ha_remote_tts import RemoteTTSServer
import asyncio

def synthesize(text):

    audio_bytes = get_tts_audio(text, key)

    return audio_bytes, 'wav'

server = RemoteTTSServer(synthesize)
asyncio.run(server.start())
```

### Client

```python
from ha_remote_tts import RemoteTTSClient
import asyncio

client = RemoteTTSClient('http://127.0.0.1:8080')
asyncio.run(client.synthesize('Hello, how are you?'))
```
