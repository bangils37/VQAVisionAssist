let isListening = false;  // Biến để kiểm tra xem chương trình có đang ghi âm không
let mediaRecorder;        // Đối tượng MediaRecorder dùng để ghi âm
let audioChunks = [];     // Mảng chứa các đoạn ghi âm
let audioContext;         // Đối tượng AudioContext để xử lý âm thanh
let analyser;             // Đối tượng AnalyserNode để phân tích âm thanh
let volumeArray = [];     // Mảng để lưu giá trị âm lượng
let silenceTimeout;        // Biến để theo dõi thời gian im lặng
let isResponding = false; // Biến để kiểm tra trạng thái phản hồi

async function startListening() {
    if (isListening) return; // Nếu đang lắng nghe thì không làm gì cả
    isListening = true;


    // Yêu cầu quyền truy cập micro và bắt đầu ghi âm
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

    // Tạo AudioContext và AnalyserNode
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    analyser.fftSize = 2048; // Kích thước FFT cho phân tích âm thanh

    // Khi có dữ liệu âm thanh được ghi
    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data); // Thêm đoạn âm thanh vào mảng
    };

    mediaRecorder.onstop = async () => {
        document.getElementById('status').textContent = "Đang xử lý, xin chờ...";
        document.getElementById('status').style.backgroundColor = "orange"; // Màu cam khi đang xử lý
        document.getElementById('status').style.color = "white"; // Màu chữ trắng
    
        if (!isListening) return;

        // Nếu đang trong quá trình phản hồi, không làm gì cả
        if (isResponding) return;

        isResponding = true; // Đánh dấu là đang phản hồi
    
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');
    
        try {
            // Request đầu tiên để nhận text và respond_text
            const response = await fetch('/listen', {
                method: 'POST',
                body: formData
            });
            console.log(response);
    
            const result = await response.json();
            console.log(result);
            const text = result.text;
            const respond_text = result.respond_text;
            console.log(text);
            console.log(respond_text);

            // Kiểm tra nếu có lỗi nhận diện thì dừng lại
            if (text === "Lỗi nhận diện giọng nói.") {
                document.getElementById('status').textContent = "Không thể nhận diện giọng nói, hãy thử lại.";
                document.getElementById('status').style.backgroundColor = "red"; // Màu đỏ nếu có lỗi
                document.getElementById('status').style.color = "white"; // Màu chữ trắng
                return;  // Dừng hàm và không thực hiện request thứ hai
            }

            document.getElementById('question').textContent = `Câu hỏi: ${text}`;
            document.getElementById('answer').textContent = `Câu trả lời: ${respond_text}`;
    
            // Request thứ hai để lấy âm thanh
            const audioResponse = await fetch('/get_audio_response');
            if (audioResponse.ok) {
                const audioBlob = await audioResponse.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.play();
            } else {
                console.error("Không thể tải âm thanh phản hồi.");
            }
    
        } catch (error) {
            document.getElementById('response').textContent = "Lỗi kết nối đến server.";
        } finally {
            document.getElementById('status').textContent = "Tôi sẵn sàng lắng nghe.";
            document.getElementById('status').style.backgroundColor = "green"; // Màu xanh khi sẵn sàng
            document.getElementById('status').style.color = "white"; // Màu chữ trắng
            audioChunks = [];
            isResponding = false; // Đánh dấu đã hoàn thành phản hồi
            if (isListening) mediaRecorder.start();
        }
    };
        
    mediaRecorder.start(); // Bắt đầu ghi âm

    // Kiểm tra âm lượng liên tục
    checkVolume();
}

function checkVolume() {
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);
    const averageVolume = dataArray.reduce((sum, value) => sum + value) / dataArray.length;

    // document.getElementById('volume').textContent = averageVolume.toFixed(0);

    console.log(isResponding);
    if (averageVolume < 20) { // Nếu âm lượng nhỏ hơn 1
        // Thiết lập thời gian im lặng
        if (!silenceTimeout) {
            silenceTimeout = setTimeout(() => {
                if (mediaRecorder.state !== "inactive") 
                mediaRecorder.stop(); 
            }, 1500); // Thời gian im lặng 1 giây
        }
    } else {
        if(silenceTimeout !== null && !isResponding) {
            captureUpload(); // Chụp ảnh và tải lên ngay khi người dùng nói
        }
        // Nếu có âm thanh, đặt lại thời gian im lặng
        clearTimeout(silenceTimeout);
        silenceTimeout = null;
        if(!isResponding)
        {
            document.getElementById('status').textContent = "Tôi đang nghe thấy bạn nói gì đó...";
            document.getElementById('status').style.backgroundColor = "blue"; // Màu xanh dương khi đang nghe
            document.getElementById('status').style.color = "white"; // Màu chữ trắng
        }
    }

    // Gọi lại hàm kiểm tra âm lượng sau một khoảng thời gian
    if (isListening) {
        requestAnimationFrame(checkVolume);
    }
}

function stopListening() {
    isListening = false; // Đặt biến kiểm tra thành false
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop(); // Dừng ghi âm nếu đang ghi
    }
    clearTimeout(silenceTimeout); // Dọn dẹp thời gian im lặng
}

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const capturedImage = document.getElementById('capturedImage');

// Yêu cầu quyền truy cập vào camera
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing the camera: ", err);
    });

function captureUpload() {
    // Vẽ ảnh từ video lên canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Hiển thị ảnh vừa chụp lên thẻ img
    capturedImage.src = canvas.toDataURL('image/png');
    
    // Cập nhật thông báo trạng thái
    statusMessage.textContent = "Uploading...";

    // Chuyển ảnh trong canvas thành blob và tải lên server
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'captured_image.png');
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Cập nhật trạng thái sau khi tải lên thành công
            statusMessage.textContent = data.message;
        })
        .catch(error => {
            console.error('Error uploading image:', error);
            statusMessage.textContent = "Upload failed!";
        });
    });
}
