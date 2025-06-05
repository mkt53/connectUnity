import threading
import queue
import requests
import wave
import io
import pyaudio
from google import genai
import os

# APIキー
# APIキーの設定（環境変数から取得）
client = genai.Client(api_key="AIzaSyDT3kQGcrFL9xhWW8CPoYX2zqeASDRPVOk")

# Voicevoxで音声合成
def get_voice(text, speaker_id=1, speed=1.8, base_url="http://127.0.0.1:50021"):
    params = {"text": text, "speaker": speaker_id}
    query = requests.post(f"{base_url}/audio_query", params=params)
    query.raise_for_status()
    query_json = query.json()
    query_json["speedScale"] = speed
    synthesis = requests.post(
        f"{base_url}/synthesis",
        params={"speaker": speaker_id},
        json=query_json
    )
    synthesis.raise_for_status()
    return synthesis.content

# 音声を再生
def play_binary_sound(audio_binary):
    wf = wave.open(io.BytesIO(audio_binary), 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()

# 音声合成＋再生の順次実行　それぞれ別で動作させて再生中にも音声を合成するようにした
# def synthesize_and_play_loop():
#     while askGemThread.is_alive() or not text_queue.empty():
#         text = text_queue.get()
#         try:
#             audio = get_voice(text,1,1.8,"https://5c18-240f-64-8262-1-4c0b-32fc-b927-ac0c.ngrok-free.app")
#             play_binary_sound(audio)
#         except Exception as e:
#             print(f"[エラー] {e}")
#         text_queue.task_done()
#     print("再生終了")

# 音声合成順次実行
def synthesizeVV():
    while askGemThread.is_alive() or not text_queue.empty():
        text = text_queue.get()
        try:
            audio = get_voice(text,1,1.8,"https://9f56-240f-64-8262-1-7c11-7b4f-5bc6-32df.ngrok-free.app")
            voice_queue.put(audio)
        except Exception as e:
            print(f"[エラー] {e}")
        text_queue.task_done()
    print("合成終了")

# 再生の順次実行
def play_voice_loop():
    while GenVoiceTh.is_alive() or not voice_queue.empty():
        play = voice_queue.get()
        try:
            play_binary_sound(play)
        except Exception as e:
            print(f"[エラー] {e}")
        voice_queue.task_done()
    print("再生終了")

def GetAns(question):#gemiiに送信しストリーミングでキューに順次追加する
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[question]
    )

    for chunk in response:
        if chunk.text:
            print(chunk.text, end="", flush=True)
            text_queue.put(chunk.text)  # ここで順番にキューへ

# テキスト → 音声合成 → 再生の順序を保証するためのテキストキュー
text_queue = queue.Queue()
voice_queue = queue.Queue()

# ユーザー入力とストリーミング処理
prompt = input("AIへの送信内容：")

askGemThread = threading.Thread(name="gem",target=GetAns,args=(prompt,))
askGemThread.start()


# 音声合成スレッドを1つだけ起動（順次処理を保証）
GenVoiceTh = threading.Thread(target=synthesizeVV, daemon=True)
GenVoiceTh.start()

# 音声再生スレッドを1つだけ起動（順次処理を保証）
PlayVoiceTh = threading.Thread(target=play_voice_loop,daemon=True)
PlayVoiceTh.start()

#askGemThread.join()
GenVoiceTh.join()
PlayVoiceTh.join()