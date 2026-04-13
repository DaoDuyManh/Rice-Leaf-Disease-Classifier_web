# Rice Leaf Disease Classifier - Web Version

## Mô tả
Ứng dụng web dự đoán bệnh lá lúa sử dụng Streamlit và mô hình machine learning.

## Yêu cầu hệ thống
- Python 3.8+
- pip

## Cài đặt

### 1. Tạo Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình Firebase
- Đảm bảo file `rice-leaf-disease-classifier-firebase-adminsdk-fbsvc-15b0ed0c79.json` có trong thư mục
- File `.env` đã được cấu hình (nếu cần)

### 4. Chạy ứng dụng
```bash
streamlit run streamlit_app_v2.py
```

Ứng dụng sẽ chạy trên: http://localhost:8501

## Cấu trúc thư mục
```
Rice Leaf Disease Classifier_web/
├── streamlit_app_v2.py          # Ứng dụng Streamlit chính
├── firebase_service.py          # Service kết nối Firebase
├── firebase_config.py           # Config Firebase
├── best_MobileNetV2_model.keras # Mô hình ML
├── requirements.txt             # Dependencies
├── local_data/                  # Dữ liệu cục bộ
├── .env.example                 # Template biến môi trường
└── README_web.md               # Hướng dẫn gốc
```

## Tính năng
- 🖼️ Tải lên ảnh lá lúa để phân tích
- 🔍 Dự đoán bệnh với độ tin cậy cao
- 📊 Xem lịch sử phân tích được đồng bộ với Firebase
- 💾 Lưu trữ các phân tích trên Firebase Firestore

## Ghi chú
- Mô hình được huấn luyện trên dữ liệu lá lúa Việt Nam
- Dữ liệu được đồng bộ giữa web và ứng dụng mobile qua Firebase
