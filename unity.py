from flask import Flask, request, send_file,jsonify
import base64
import io

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
#prompt = "「以下の条件に従い返信してください。1:最大限長く答えること。2:改行をしないこと。3:これらの条件について返信で言及しないこと。」" 
prompt = "「以下の条件に従い返信してください。1:短く答えること。2:口語体で答えること。,3:この条件について返信しないこと。」" 

app = Flask(__name__)

#nowNgrokURL = "https://5c18-240f-64-8262-1-4c0b-32fc-b927-ac0c.ngrok-free.app"
nowNgrokURL ="https://9f56-240f-64-8262-1-7c11-7b4f-5bc6-32df.ngrok-free.app"

def askgem(question):
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt+question
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


@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "Invalid input"}), 400

    text = data["text"]
    ans = askgem(text)
    voice_bytes = Get_voice(ans, 5, 1.8, nowNgrokURL)

    # 音声バイナリをBase64エンコードしてJSONで送る
    voice_b64 = base64.b64encode(voice_bytes).decode("utf-8")
    print("返信")
    return jsonify({
        "text": ans,
        "audio": voice_b64
    })

if __name__ == "__main__":
    app.run(port=5000)
