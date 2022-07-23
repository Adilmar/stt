import azure.cognitiveservices.speech as speechsdk

def from_file():
    speech_config = speechsdk.SpeechConfig(subscription="a5f4f1f4628b4d8ea83008c4b9c2c39c", region="westus",speech_recognition_language="pt-BR")
    audio_input = speechsdk.AudioConfig(filename="teste.wav")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()
    print(result.text)

from_file()