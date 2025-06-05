import os
import threading
#from dotenv import load_dotenv

from google import genai

import requests
#import simpleaudio as sa 謎の再生後にプログラムの強制停止によりpyaudioのめんどくさいのに変更
import io
import wave
import pyaudio

import time

#load_dotenv()
#GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
#client = genai.Client(api_key=GOOGLE_API_KEY)

client = genai.Client(api_key="AIzaSyDT3kQGcrFL9xhWW8CPoYX2zqeASDRPVOk")
#indent = "「以下の条件に従い返信してください。1:最大限長く答えること。2:改行をしないこと。3:これらの条件について返信で言及しないこと。」" 
prompt = "「以下の条件に従い返信してください。1:最大限短く答えること。2:この条件について返信しないこと」" 
nowNgrokURL ="https://9f56-240f-64-8262-1-7c11-7b4f-5bc6-32df.ngrok-free.app"

def askgem(question):
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=question+"話し言葉で話して"
    )
    return response.text

#def Get_voice(text, speaker_id=1, speed=1.0, base_url="http://127.0.0.1:50021"):
def Get_voice(text, speaker_id=1, speed=1.0, base_url="http://localhost:50021"):

    start_time = time.time()
    # クエリ生成（音声パラメータ取得）
    params = {"text": text, "speaker": speaker_id}
    query = requests.post(f"{base_url}/audio_query", params=params)
    query.raise_for_status()
    query_json = query.json()

    # 話速を変更
    query_json["speedScale"] = speed  # 例: 1.2 で20%早く、0.8で20%遅く話す

    # 音声合成（バイナリ取得）
    synthesis = requests.post(
        f"{base_url}/synthesis",
        params={"speaker": speaker_id},
        json=query_json
    )
    synthesis.raise_for_status()

    # 音声データ（バイナリ）を返す
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"{threading.current_thread().name}終了。実行時間: {elapsed_time:.2f} 秒")
    return synthesis.content


def playBinarySound(audio_binary):

    wf = wave.open(io.BytesIO(audio_binary), 'rb')

    # PyAudio で再生
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(1024)
    while wf.tell() < wf.getnframes():
        data = wf.readframes(1024)
        stream.write(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

while True:
    toGemini = input("AIへの送信内容:")
    #fromGemini = askgem(prompt + toGemini)
    fromGemini = askgem(toGemini)

    print(fromGemini)

    #threadLocal = threading.Thread(target=Get_voice,name="noteCpu",args=(fromGemini,1,1.6))
    #threadLocal.start()

    threadDesk = threading.Thread(target=Get_voice,name="DeskGpu",args=(fromGemini,1,1.6,nowNgrokURL,))
    threadDesk.start()

    threadDesk.join()
    #threadLocal.join()
    #playBinarySound(Get_voice(fromGemini,1,1.6,"https://7720-240f-64-8262-1-b4e2-47b7-fbb1-9f58.ngrok-free.app"))



    print("やったねAIが答えてくれたよ")
