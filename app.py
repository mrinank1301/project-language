from flask import Flask, render_template, jsonify, request
import numpy as np
import speech_recognition as sr
import base64
import os
from PIL import Image
import io
import string

app = Flask(__name__)

# Initialize the speech recognizer
recognizer = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listen', methods=['POST'])
def listen():
    def listen_and_transcribe(language='en-US', timeout=1, energy_threshold=300, pause_threshold=0.5):
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            recognizer.energy_threshold = energy_threshold
            recognizer.pause_threshold = pause_threshold
            
            try:
                audio = recognizer.listen(source, timeout=timeout)
                text = recognizer.recognize_google(audio, language=language)
                return {'success': True, 'text': text}
            except sr.RequestError as e:
                return {'success': False, 'error': f"Could not request results; {e}"}
            except sr.UnknownValueError:
                return {'success': False, 'error': "Could not understand audio"}
            except sr.WaitTimeoutError:
                return {'success': False, 'error': "No speech detected within time limit"}

    result = listen_and_transcribe()
    return jsonify(result)

@app.route('/convert', methods=['POST'])
def convert_text():
    data = request.json
    text = data.get('text', '').strip()

    if not text:
        return jsonify(success=False, error="No text provided"), 400

    # Create a mapping of characters to paths at startup instead of processing each time
    LETTER_PATHS = {
        **{chr(i): f'/static/letters/{chr(i)}.jpg' for i in range(97, 123)},  # a-z
        **{str(i): f'/static/letters/{i}.jpg' for i in range(10)},  # 0-9
        ' ': 'space'
    }

    # Faster path generation using the mapping
    if text.isascii() and all(c in string.printable for c in text):
        paths = [LETTER_PATHS.get(c.lower(), f'/static/letters/symbol_{ord(c)}.jpg') for c in text]
        response_type = 'letters'
    else:
        paths = [f'/static/gifs/word_{i}.gif' for i in range(len(text.split()))]
        response_type = 'gifs'

    return jsonify(success=True, type=response_type, paths=paths)

if __name__ == '__main__':
    app.run(debug=True)

