# 🚀 Hướng Dẫn Chạy Toàn Bộ Hệ Thống

## **📋 Danh Sách File Đã Tạo**

```
Rice Leaf Disease Classifier/
├── streamlit_app_v2.py          ⭐ App Streamlit chính (với Firebase)
├── firebase_config.py            ⚙️ Cấu hình Firebase
├── firebase_service.py           🔧 Hàm xử lý Firebase
├── setup_firebase.py             📊 Script setup Firestore
├── setup_cli.py                  💻 CLI setup interactive
├── .env.example                  📝 Template .env
├── SETUP_FIREBASE.md             📖 Hướng dẫn chi tiết
├── README.md                     📚 File này
└── best_MobileNetV2_model.keras  🤖 Model AI
```

---

## **⚡ Quick Start (5 phút)**

### **1️⃣ Tạo .env File (Interactive CLI)**

```bash
cd "d:\DoAn\Rice Leaf Disease Classifier\Rice Leaf Disease Classifier"

d:\DoAn\venv_310\Scripts\python.exe setup_cli.py
```

Nhập thông tin khi được hỏi:
- API Key (từ Firebase Console)
- App ID (từ Firebase Console)
- Xác nhận các thông tin khác

---

### **2️⃣ Tải Service Account Key**

1. Vào https://console.firebase.google.com
2. Project: `rice-leaf-disease-classifier`
3. ⚙️ Project Settings → **Service Accounts**
4. Click **Generate new private key**
5. Di chuyển file `.json` vào folder dự án
6. Đặt tên: `firebase-service-account-key.json`

---

### **3️⃣ Setup Firestore**

```bash
d:\DoAn\venv_310\Scripts\python.exe setup_firebase.py
```

Script sẽ:
- ✅ Tạo Firestore collections
- ✅ Tạo file `firestore_rules.txt`

---

### **4️⃣ Cấu hình Security Rules**

1. Firebase Console → **Firestore Database** → **Rules**
2. Xóa code cũ
3. Copy nội dung từ `firestore_rules.txt` vào
4. Click **Publish**

---

### **5️⃣ Chạy Ứng dụng**

```bash
streamlit run streamlit_app_v2.py
```

Hoặc:

```bash
d:\DoAn\venv_310\Scripts\python.exe -m streamlit run streamlit_app_v2.py
```

✅ **Ứng dụng sẽ chạy tại:** http://localhost:8502

---

## **📝 Tính Năng Chính**

### **🔐 Xác Thực (Authentication)**
- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập
- ✅ Đăng xuất

### **📸 Phân Tích Ảnh**
- ✅ Tải lên ảnh lá lúa
- ✅ Phân loại bệnh tự động
- ✅ Hiển thị độ tin cậy
- ✅ Khuyến nghị điều trị & phòng ngừa

### **💾 Lưu Lịch Sử**
- ✅ Lưu tất cả kết quả phân tích
- ✅ Lưu chi tiết: thời gian, ảnh, độ tin cậy, khuyến nghị
- ✅ Thêm ghi chú cá nhân

### **🔍 Tìm Kiếm & Lọc**
- ✅ Tìm theo loại bệnh
- ✅ Lọc theo độ tin cậy
- ✅ Sắp xếp theo thời gian

### **📊 Thống Kê**
- ✅ Tổng số phân tích
- ✅ Phân bố bệnh
- ✅ Biểu đồ trực quan

---

## **🔧 Troubleshooting**

### **❌ "Service Account file not found"**
```
✅ Giải pháp:
- Tải file từ Firebase Console
- Đặt đúng path trong .env
- Tên file: firebase-service-account-key.json
```

### **❌ "Project ID không khớp"**
```
✅ Giải pháp:
- .env phải có: FIREBASE_PROJECT_ID=rice-leaf-disease-classifier
- Kiểm tra lại Firebase Console
```

### **❌ Lỗi import firebase_admin**
```
✅ Giải pháp:
- Chạy: pip install firebase-admin
- Hoặc: d:\DoAn\venv_310\Scripts\pip.exe install firebase-admin
```

### **❌ Port 8502 đã được sử dụng**
```
✅ Giải pháp:
- Chạy: streamlit run streamlit_app_v2.py --server.port=8503
```

### **❌ Firestore Rules lỗi**
```
✅ Giải pháp:
- Xóa toàn bộ Rules cũ
- Copy đúng nội dung từ firestore_rules.txt
- Click Publish
```

---

## **📊 Database Schema**

### **Collection: `users`**
```json
{
  "email": "user@example.com",
  "name": "Nguyen Van A",
  "createdAt": "2024-01-15T10:30:00Z",
  "totalAnalysis": 15,
  "lastAnalysis": "2024-01-20T14:45:00Z"
}
```

### **Collection: `analysis_history`**
```json
{
  "userId": "user_id_xyz",
  "timestamp": "2024-01-20T14:45:00Z",
  "imageFileName": "rice_leaf_001.jpg",
  "diseaseClass": "Bacterialblight",
  "diseaseNameVi": "Bệnh bạc lá",
  "confidence": 87.5,
  "allPredictions": {
    "Bacterialblight": 0.875,
    "Blast": 0.08,
    "Brownspot": 0.03,
    "Tungro": 0.015
  },
  "symptoms": "Các vệt dài màu vàng hoặc trắng...",
  "treatment": "Phun thuốc kháng sinh...",
  "prevention": "Sử dụng giống kháng...",
  "notes": "Ruộng phía bắc"
}
```

---

## **🎯 Các Bước Tiếp Theo**

- [ ] Tạo .env file (chạy setup_cli.py)
- [ ] Tải Service Account Key
- [ ] Chạy setup_firebase.py
- [ ] Cấu hình Firestore Rules
- [ ] Chạy streamlit_app_v2.py
- [ ] Đăng ký tài khoản test
- [ ] Tải ảnh lá lúa để test
- [ ] Xem lịch sử & thống kê

---

## **📚 Tài Liệu Tham Khảo**

- [Firebase Console](https://console.firebase.google.com)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Streamlit Documentation](https://docs.streamlit.io)

---

## **💡 Tips**

1. **Backup dữ liệu**: Firestore tự động backup hàng ngày
2. **Giới hạn chi phí**: 50,000 đọc/ngày miễn phí
3. **Cache model**: Sử dụng `@st.cache_resource` để tối ưu
4. **Bảo mật**: Luôn dùng Service Account cho backend

---

**✅ Hoàn tất tất cả bước và bạn sẽ có ứng dụng hoàn chỉnh!**

Nếu có vấn đề gì, xem file `SETUP_FIREBASE.md` để tìm giải pháp chi tiết.
