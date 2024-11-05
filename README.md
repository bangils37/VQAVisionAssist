# VQA Vision Assist

Ứng dụng hỗ trợ người khiếm thị nhận diện môi trường và các vật thể xung quanh thông qua công nghệ nhận diện giọng nói và hình ảnh tiên tiến. Với sự kết hợp của text-to-speech, speech-to-text và VQA AI Model (Visual Question Answering - sử dụng PNP-VQA), ứng dụng cho phép người dùng khiếm thị hỏi các câu hỏi về những gì đang diễn ra xung quanh họ và nhận câu trả lời qua giọng nói. Ứng dụng sử dụng camera và micrô của thiết bị để ghi nhận hình ảnh và câu hỏi của người dùng, sau đó đưa ra phản hồi bằng âm thanh, giúp họ có được thông tin chính xác và tức thì về môi trường xung quanh.

## Workflow

1. **Kích hoạt thiết bị**: Khi ứng dụng khởi chạy, người dùng cấp quyền truy cập vào camera và micro của thiết bị. Camera đóng vai trò như "con mắt" của ứng dụng để quan sát môi trường xung quanh, trong khi micro cho phép ứng dụng lắng nghe câu hỏi của người dùng.
2. **Ghi nhận câu hỏi và hình ảnh**: Khi người dùng bắt đầu nói, ứng dụng ngay lập tức ghi lại hình ảnh tại thời điểm đó từ camera cùng với câu hỏi được chuyển đổi từ giọng nói thành văn bản (speech-to-text).
3. **Phân tích câu hỏi và hình ảnh**: Hình ảnh và câu hỏi sau đó được chuyển vào VQA AI Model (Visual Question Answering - sử dụng PNP-VQA) để phân tích và suy luận. Mô hình này sẽ xử lý thông tin và đưa ra câu trả lời phù hợp dựa trên ngữ cảnh trong hình ảnh và nội dung câu hỏi.
4. **Trả lời qua giọng nói**: Câu trả lời từ mô hình VQA được chuyển đổi thành giọng nói (text-to-speech) và phát qua loa của thiết bị, giúp người dùng nghe được thông tin cần thiết về môi trường hoặc vật thể mà họ muốn tìm hiểu.
5. **Phản hồi theo thời gian thực**: Toàn bộ quy trình này diễn ra nhanh để đảm bảo tính liên tục và phản hồi nhanh chóng cho người dùng khiếm thị, giúp họ có thông tin về thế giới xung quanh theo thời gian thực.

VD:

![image.png](image.png)

- **Hỏi:** What is going on here?
T**rả lời:** A couple of people playing a game
- **Hỏi:** What is this game?
T**rả lời:** Card game

## Model

Được tham khảo từ bài báo: [Plug-and-Play VQA: Zero-shot VQA by Conjoining Large Pretrained Models with Zero Training", by Anthony T.M.H. et al](https://arxiv.org/pdf/2210.08773)

![image.png](image%201.png)

Cách hoạt động của Model nằm trong 3 modules:

1. **Image-Question Matching Module (Mô-đun ghép nối hình ảnh-câu hỏi)**: Mô-đun này sử dụng câu hỏi của người dùng để xác định các vùng ảnh (patches) liên quan trong hình ảnh. Nó áp dụng kỹ thuật Grad-CAM để làm nổi bật các khu vực có khả năng liên quan đến câu hỏi, giúp mô hình tập trung vào các chi tiết quan trọng.
2. **Image Captioning Module (Mô-đun tạo chú thích hình ảnh)**: Sau khi xác định các vùng ảnh liên quan, mô-đun này sẽ lấy mẫu các vùng đó và tạo ra nhiều chú thích khác nhau mô tả nội dung của hình ảnh. Nhờ phương pháp giải mã ngẫu nhiên, các chú thích này có thể đa dạng và phong phú, cung cấp nhiều thông tin bổ sung cho bước phân tích sau.
3. **Question Answering Module (Mô-đun trả lời câu hỏi)**: Cuối cùng, mô-đun này kết hợp câu hỏi và các chú thích được tạo ra để đưa ra câu trả lời chính xác nhất. Bằng cách sử dụng các chú thích làm ngữ cảnh, mô hình có thể hiểu rõ hơn về đối tượng và các thuộc tính có liên quan trong hình ảnh để phản hồi phù hợp với câu hỏi.

## **Dependencies and Installation**

```bash
git clone https://github.com/bangils37/VQAVisionAssist.git
cd VQAVisionAssist
```

### 1. Cài đặt Python

Đảm bảo rằng bạn đã cài đặt **Python 3.8** trở lên (Đề xuất [Anaconda](https://www.anaconda.com/download/#linux) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)). Bạn có thể kiểm tra phiên bản hiện tại bằng lệnh:

```bash
python --version
```

### 2. Thiết lập môi trường ảo (khuyến nghị)

Tạo môi trường ảo để quản lý các gói cài đặt:

```bash
python -m venv venv
source venv/bin/activate  # Trên macOS/Linux
venv\Scripts\activate     # Trên Windows
```

### 3. Cài đặt các thư viện

Chạy lệnh sau để cài đặt tất cả các thư viện cần thiết:

```bash
.\install_packages.bat
```

### 4. Cài đặt thêm một số thư viện phụ thuộc

Một số thư viện yêu cầu cài đặt thêm:

- **ffmpeg**: Được sử dụng bởi `pydub` để xử lý âm thanh. Bạn có thể cài đặt ffmpeg như sau:
    
    **Trên Ubuntu/Debian:**
    
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```
    
    **Trên macOS (sử dụng Homebrew):**
    
    ```bash
    brew install ffmpeg
    ```
    
    **Trên Windows**:
    
    - Tải ffmpeg từ [tại đây](https://ffmpeg.org/download.html) và làm theo hướng dẫn để thêm vào PATH.

## Run

```bash
python vqaserver.py
python app.py
```