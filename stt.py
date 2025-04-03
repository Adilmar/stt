import requests
import json
import time
import os
from datetime import date
from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS, cross_origin
from random import randrange
from time import sleep
import base64
import tempfile
import os
import re

import speech_recognition as sr
from pydub import AudioSegment

cabecario = f'''
______   _________  _________             _________  _________  ______     
███████╗████████╗████████╗    ██╗ █████╗ 
██╔════╝╚══██╔══╝╚══██╔══╝    ██║██╔══██╗
███████╗   ██║      ██║       ██║███████║
╚════██║   ██║      ██║       ██║██╔══██║
███████║   ██║      ██║       ██║██║  ██║
╚══════╝   ╚═╝      ╚═╝       ╚═╝╚═╝  ╚═╝
                                         

      Módulo:    STT - TTS
      Developer: Dr Adilmar Coelho Dantas 
      Web:       www.adilmar.com.br                                      
'''

print(cabecario)

TOKEN_BOT_HUB = "Token 2274b1aec12962f7980aa374485f0c0479710692"
BASE_URL = f"https://api.telegram.org/bot1626167634:AAFX_qyIXbeSB6Ciq481ZUBZOUtr8QaY0Ww"
FILE_BASE_URL = f"https://api.telegram.org/file/bot1626167634:AAFX_qyIXbeSB6Ciq481ZUBZOUtr8QaY0Ww"

CHATWOOT_URL = "https://chatwoot-evolution-api.9grgnc.easypanel.host/chat/getBase64FromMediaMessage"

WIT_AI_URL = "https://api.wit.ai/speech?v=20221114"
WIT_AI_TOKEN = "SZYPKFBBSKLLAPYGMRR5QEAFQIWRKBH7"

def extract_last_text(response):
    """
    Extrai o último valor do campo 'text' de um JSON retornado pela API.
    """
    response_text = response.strip()  # Remove espaços extras
    json_blocks = re.findall(r'\{.*?\}', response_text, re.DOTALL)  # Encontra todos os blocos JSON

    texts = []

    for block in json_blocks:
        try:
            data = json.loads(block)  # Converte cada JSON para dicionário
            if "text" in data:
                texts.append(data["text"])  # Armazena os valores de 'text'
        except json.JSONDecodeError:
            continue  # Ignora erros de parsing

    return texts[-1] if texts else ""  # Retorna o último texto encontrado ou string vazia

def fetch_media_base64(message_id, api_key, instance):
    URL = F"{CHATWOOT_URL}/{instance}"
    payload = {
        "message": {"key": {"id": message_id}},
        "convertToMp4": False
    }
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(URL, json=payload, headers=headers).json()
    return response 

def convert_ogg_to_wav(base64_audio):
    ogg_bytes = base64.b64decode(base64_audio)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as ogg_file:
        ogg_file.write(ogg_bytes)
        ogg_path = ogg_file.name
    
    wav_path = ogg_path.replace(".ogg", ".wav")
    audio = AudioSegment.from_file(ogg_path, format="ogg")
    audio.export(wav_path, format="wav")
    os.remove(ogg_path)
    return wav_path

def transcribe_audio(file_path):
    headers = {
        "Authorization": f"Bearer {WIT_AI_TOKEN}",
        "Content-Type": "audio/wav"
    }
    with open(file_path, "rb") as audio_file:
        response = requests.post(WIT_AI_URL, headers=headers, data=audio_file).text
    os.remove(file_path)
    response = extract_last_text(response)
    print("xx",response)
    
    return response

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

@app.route("/process_message", methods=["POST"])
def process_message():
    content = request.json
    try:
        message_id = content["message_id"]
        api_key = content["api_key"]
        instance = str(content["instance"])

        media_data = fetch_media_base64(message_id, api_key, instance)
        if not media_data:
            return jsonify({"error": "Failed to fetch media"}), 500

        mimetype = media_data.get("mimetype", "")
        base64_audio = media_data.get("base64", "")
        if not base64_audio:
            return jsonify({"error": "No base64 audio found"}), 500

        if "ogg" in mimetype:
            audio_path = convert_ogg_to_wav(base64_audio)
        else:
            return jsonify({"error": "Unsupported audio format"}), 400

        text = transcribe_audio(audio_path)
        response = jsonify({"transcription":text, "statusCode":200}), 200
    
    except Exception:
        response = jsonify({"message":"bad request param"}), 401
    
    return response


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
