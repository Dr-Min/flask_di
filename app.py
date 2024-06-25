from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from openai import OpenAI
from dotenv import load_dotenv
import base64
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

load_dotenv()
client = OpenAI(api_key="sk-proj-s6Ct9u7YF5JGUrBZIwX0T3BlbkFJ559Ed6UnCxCcdrxxrgei")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    audio_data = base64.b64decode(data.split(',')[1])
    
    # 음성을 텍스트로 변환
    with open('temp_audio.wav', 'wb') as f:
        f.write(audio_data)
    
    with open('temp_audio.wav', 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="ko")
    
    user_text = transcript.text
    
    # AI 응답 생성
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text}
        ]
    )
    
    ai_response = response.choices[0].message.content
    
    # 텍스트를 음성으로 변환
    audio_response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=ai_response
    )
    
    # 클라이언트에 응답 전송
    emit('ai_response', {
        'user_text': user_text,
        'text': ai_response, 
        'audio': base64.b64encode(audio_response.content).decode('utf-8')
    })

if __name__ == '__main__':
    socketio.run(app, debug=True)
