from flask import Flask, render_template, request, jsonify, send_file, make_response
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from pyngrok import ngrok
import requests  # Thư viện để gửi HTTP request
import io
import os

app = Flask(__name__)
FASTAPI_URL = "http://localhost:8000"  # Đường dẫn tới server FastAPI đang chạy

app.config['UPLOAD_FOLDER'] = 'static/uploads/' # Thư mục lưu trữ ảnh chụp từ camera

IMAGE_PATH = "static/uploads/captured_image.png" # Đường dẫn tới ảnh chụp từ camera

@app.route('/')
def index():
    return render_template('index.html')

# Biến toàn cục để lưu âm thanh phản hồi dưới dạng byte string
last_audio_response = None

@app.route('/listen', methods=['POST'])
def listen():
    recognizer = sr.Recognizer()
    
    # Chuyển đổi dữ liệu âm thanh thành WAV nếu không phải định dạng hỗ trợ
    audio_file = request.files['audio']
    audio_segment = AudioSegment.from_file(audio_file, format="webm")
    audio_wav = io.BytesIO()
    audio_segment.export(audio_wav, format="wav")
    audio_wav.seek(0)
    
    # Sử dụng audio_wav cho SpeechRecognition
    with sr.AudioFile(audio_wav) as source:
        audio_data = recognizer.record(source)
    
    try:
        # Nhận diện giọng nói
        text = recognizer.recognize_google(audio_data, language='vi-VN')
        print("Client nói:", text)
        
        response_text = get_answer(IMAGE_PATH, text)
        
        # Tạo file âm thanh phản hồi
        tts = gTTS(response_text, lang='en')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        # Lưu âm thanh vào biến toàn cục dưới dạng byte string
        global last_audio_response
        last_audio_response = audio_bytes.read()  # Lưu dưới dạng byte string

        # Trả về JSON chứa text và respond_text
        return jsonify({"text": text, "respond_text": response_text})
        
    except Exception as e:
        print("Lỗi nhận diện:", str(e))
        return jsonify({"text": "Lỗi nhận diện giọng nói.", "respond_text": ""})

# Endpoint mới để trả về âm thanh
@app.route('/get_audio_response', methods=['GET'])
def get_audio_response():
    if last_audio_response:
        # Tạo một io.BytesIO mới từ byte string
        audio_io = io.BytesIO(last_audio_response)
        return send_file(audio_io, mimetype="audio/mpeg")
    return jsonify({"error": "No audio response available"}), 404
    
def get_answer(image_url, question):
    with open(image_url, "rb") as image_file:
        image_data = image_file.read()  # Đọc dữ liệu nhị phân của ảnh

    # Định nghĩa dữ liệu để gửi đến API FastAPI
    files = {"img": image_data}  # Gửi ảnh dưới dạng dữ liệu nhị phân
    data = {"question": question}  # Định nghĩa câu hỏi dưới dạng dữ liệu form

    try:
        # Gửi yêu cầu POST tới API FastAPI với ảnh và câu hỏi
        response = requests.post(f"{FASTAPI_URL}/submit", files=files, data=data)

        # Kiểm tra phản hồi từ API
        if response.status_code == 200:
            # Nếu thành công, lấy câu trả lời từ phản hồi JSON
            answer = response.json().get("answer", "No answer received")
            return answer  # Trả về chuỗi câu trả lời
        else:
            # Trả về chuỗi lỗi nếu không lấy được câu trả lời
            return "Error: Could not retrieve answer"
    except Exception as e:
        print("Lỗi khi gọi API FastAPI:", str(e))
        return "Error: Exception occurred while retrieving answer"

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully', 'filename': filename})

if __name__ == '__main__':
    # Tạo đường hầm ngrok cho server trên cổng 5000
    # ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")
    # public_url = ngrok.connect(5000)
    # print("Public URL:", public_url)

    # Chạy server Flask
    app.run(host="0.0.0.0", port=5000)
