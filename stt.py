import requests
import json
import time
import os
from datetime import date
from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS, cross_origin
from random import randrange
from time import sleep

from werkzeug.wrappers import response
import speech_recognition as sr
from pydub import AudioSegment


cabecario = f'''

 _____                _  ______            
/  ___|              | ||___  /            
\ `--.  ___ _ __   __| |   / /  __ _ _ __  
 `--. \/ _ \ '_ \ / _` |  / /  / _` | '_ \ 
/\__/ /  __/ | | | (_| |./ /__| (_| | |_) |
\____/ \___|_| |_|\__,_|\_____/\__,_| .__/ 
                                    | |    
                                    |_|   
      Módulo:    STT - TTS
      Developer: Dr Adilmar Coelho Dantas 
      Web:       www.adilmar.com.br                                      
'''

print(cabecario)

TOKEN_BOT_HUB = "Token 2274b1aec12962f7980aa374485f0c0479710692"
BASE_URL = f"https://api.telegram.org/bot1626167634:AAFX_qyIXbeSB6Ciq481ZUBZOUtr8QaY0Ww"
FILE_BASE_URL = f"https://api.telegram.org/file/bot1626167634:AAFX_qyIXbeSB6Ciq481ZUBZOUtr8QaY0Ww"


def send_message(message, chat_id):
    content = {"text": message.encode("utf-8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage"
    requests.post(url, content)

    response = {
        "statusCode": 200,
        "status": "enviada"
    }

    url = "https://hooks.slack.com/services/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"

    payload = json.dumps({
        "text": message
    })
    headers = {
        'Content-type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print("Mensagens enviadas", response.text)

    return response


def wav(url):
  url = str(url)

  r = requests.get(url, allow_redirects=True)
  open('/tmp/wpp.ogg', 'wb').write(r.content)
  
  orig_song = "/tmp/wpp.ogg"
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



app = Flask(__name__)
CORS(app)


@app.route('/stt', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        content = request.json

        ogg = content["url"]

        response = wav(ogg)

        return response


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
