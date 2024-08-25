"""
Code adapted from @R2D2FISH/glados-tts
Repo: https://github.com/R2D2FISH/glados-tts
"""

import torch
from utils.tools import prepare_text
from scipy.io.wavfile import write
import time
import tempfile
import subprocess
from pydub import AudioSegment

kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'stdin': subprocess.PIPE}


class tts_runner:
	def __init__(self, use_p1: bool = False, log: bool = False):
		print('Initializing TTS Engine...')
		self.log = log
		if use_p1:
			self.emb = torch.load('models/emb/glados_p1.pt')
		else:
			self.emb = torch.load('models/emb/glados_p2.pt')
		# Select the device
		if torch.cuda.is_available():
			self.device = 'cuda'
		elif torch.is_vulkan_available():
			self.device = 'vulkan'
		else:
			self.device = 'cpu'

		# Load models
		self.glados = torch.jit.load('models/glados-new.pt')
		self.vocoder = torch.jit.load('models/vocoder-gpu.pt', map_location=self.device)
		for i in range(2):
			init = self.glados.generate_jit(prepare_text(str(i)), self.emb, 1.0)
			init_mel = init['mel_post'].to(self.device)
			init_vo = self.vocoder(init_mel)

	def run_tts(self, text, alpha: float = 1.0) -> AudioSegment:
		x = prepare_text(text)

		with torch.no_grad():
			# Generate generic TTS-output
			old_time = time.time()
			tts_output = self.glados.generate_jit(x, self.emb, alpha)
			if self.log:
				print('Forward Tacotron took ' + str((time.time() - old_time) * 1000) + 'ms')

			# Use HiFiGAN as vocoder to make output sound like GLaDOS
			old_time = time.time()
			mel = tts_output['mel_post'].to(self.device)
			audio = self.vocoder(mel)
			if self.log:
				print('HiFiGAN took ' + str((time.time() - old_time) * 1000) + 'ms')

			# Normalize audio to fit in wav-file
			audio = audio.squeeze()
			audio = audio * 32768.0
			audio = audio.cpu().numpy().astype('int16')
			output_file = tempfile.TemporaryFile()
			write(output_file, 22050, audio)
			sound = AudioSegment.from_wav(output_file)
			output_file.close()
			return sound
