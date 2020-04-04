from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import sounddevice

client = speech_v1.SpeechClient()

encoding = enums.RecognitionConfig.AudioEncoding.FLAC
sample_rate_hertz = 44100
language_code = 'en-US'
config = {'encoding': encoding, 'sample_rate_hertz': sample_rate_hertz, 'language_code': language_code}
uri = 'gs://bucket_name/file_name.flac'
audio = {'uri': uri}

response = client.recognize(config, audio)