import speech_recognition as sr
#import azure.cognitiveservices.speech as speechsdk

import os,sys
import requests
import json
from pydub import AudioSegment


def wav(url):
  url = str(url)

  r = requests.get(url, allow_redirects=True)
  open('/tmp/wpp.ogg', 'wb').write(r.content)
  
  orig_song = "wpp.ogg"
  dest_song = "/tmp/testez.wav"

  song = AudioSegment.from_ogg(orig_song)
  song.export(dest_song, format="wav")

  response = transcreve_audio(dest_song)

  return response



def transcreve_audio(nome_audio):
    # Selecione o audio para reconhecimento
    r = sr.Recognizer()
    with sr.AudioFile(nome_audio) as source:
      audio = r.record(source)  # leitura do arquivo de audio

    # Reconhecimento usando o Google Speech Recognition
    try:
      #print('Google Speech Recognition: ' + r.recognize_google(audio,language='pt-BR'))
      texto = r.recognize_google(audio,language='pt-BR')
    except sr.UnknownValueError:
      #print('Google Speech Recognition NÃO ENTENDEU o audio')
      texto = ''
    except sr.RequestError as e:
      #print('Erro ao solicitar resultados do serviço Google Speech Recognition; {0}'.format(e))
      texto = ''
    
    response = {"statusCode":200,"text":texto}

    return response




saida = wav("https://push-ilha-sp-push-media-prod.s3.sa-east-1.amazonaws.com/media/7400/df12/b56a/df12b56a-eb59-4ca3-84ca-91e913f17898.ogg")

print(saida)