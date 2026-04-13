import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
from datetime import datetime
import json
from firebase_service import FirebaseService
import base64
import io
import h5py

# Page config
st.set_page_config(
    page_title="Rice Leaf Disease Classifier",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0f1117;
        color: #e2e8f0;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9;
    }

    .custom-card {
        background: linear-gradient(135deg, #1f2937, #0f172a);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }

    .highlight {
        color: #60a5fa;
        font-weight: 700;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.95rem;
    }

    p, li, div {
        color: #cbd5e1;
    }

    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #2563eb;
    }

    .card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin: 1rem 0;
    }

    hr {
        border-color: #334155;
    }

    .stProgress > div > div > div {
        background-color: #3b82f6;
    }

    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }

    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white !important;
    }

    .stAlert {
        background-color: #1e293b;
        border: 1px solid #334155;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Constants
CLASSES = ['Bacterialblight', 'Blast', 'Brownspot', 'Tungro']
CLASS_NAMES_VI = {
    'Bacterialblight': 'Bệnh bạc lá',
    'Blast': 'Bệnh đạo ôn',
    'Brownspot': 'Bệnh đốm nâu',
    'Tungro': 'Bệnh vàng lùn'
}
IMG_SIZE = 224

# Initialize Firebase
firebase_service = FirebaseService()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

@st.cache_resource
def load_model():
    try:
        # Load model directly from saved_models folder
        saved_models_path = r"d:\DoAn\Rice Leaf Disease Classifier\Rice Leaf Disease Classifier\saved_models"
        
        model_files = [
            f"{saved_models_path}/best_MobileNetV2_model.keras",
            f"{saved_models_path}/best_MobileNetV2_model.h5",
            f"{saved_models_path}/best_CNN_model.h5",
            f"{saved_models_path}/rice_disease_CNN_best.h5"
        ]
        
        for model_file in model_files:
            if tf.io.gfile.exists(model_file):
                try:
                    return tf.keras.models.load_model(model_file, compile=False)
                except Exception:
                    continue
        
        # If .keras/.h5 failed, try .tflite as final fallback
        tflite_path = f"{saved_models_path}/best_MobileNetV2_model.tflite"
        if tf.io.gfile.exists(tflite_path):
            interpreter = tf.lite.Interpreter(model_path=tflite_path)
            interpreter.allocate_tensors()
            return interpreter
        
        st.error("❌ Cannot load any model from saved_models folder.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Model loading error: {str(e)[:200]}")
        st.stop()

model = load_model()

# Disease recommendations
RECOMMENDATIONS = {
    'Bacterialblight': {
        'name': 'Bệnh bạc lá',
        'symptoms': 'Các vệt dài màu vàng hoặc trắng trên lá, thường bắt đầu từ mép lá',
        'treatment': """
- Phun thuốc kháng sinh (Streptomycin 100-200 ppm, Tetracycline)
- Cải thiện thoát nước, tránh úng
- Loại bỏ và tiêu hủy cây bệnh
- Luân canh với cây họ đậu
- Sử dụng giống kháng bệnh
        """,
        'prevention': """
- Sử dụng giống kháng (ĐT8, OM4900, Jasmine 85)
- Bón phân cân đối, không thừa đạm
- Gieo cấy đúng mật độ
- Vệ sinh ruộng, xử lý rơm rạ
        """
    },
    'Blast': {
        'name': 'Bệnh đạo ôn',
        'symptoms': 'Đốm hình thoi, viền nâu, giữa xám trắng; cổ bông đổ gãy',
        'treatment': """
- Phun Tricyclazole, Isoprothiolane
- Giảm đạm, tăng kali và silic
- Tưới cạn-ướt xen kẽ
- Giữ ruộng thoáng
        """,
        'prevention': """
- Chọn giống kháng (IR64, Jasmine 85, ST25)
- Gieo đúng thời vụ
- Bón phân cân đối
- Không gieo quá dày
        """
    },
    'Brownspot': {
        'name': 'Bệnh đốm nâu',
        'symptoms': 'Đốm tròn màu nâu rải rác, thường do thiếu dinh dưỡng',
        'treatment': """
- Bổ sung kali (KCl 30-40 kg/ha)
- Cải thiện tưới tiêu
- Phun Mancozeb nếu cần
- Bón vi lượng (Zn, Fe, Mn)
        """,
        'prevention': """
- Bón phân đầy đủ NPK + vi lượng
- Cải tạo đất chua
- Ngâm hạt giống chọn lọc
- Đảm bảo đủ nước
        """
    },
    'Tungro': {
        'name': 'Bệnh vàng lùn',
        'symptoms': 'Lá vàng, cây lùn, ít nhánh, hạt lép; do virus qua rầy',
        'treatment': """
- Diệt rầy xanh (Imidacloprid, Buprofezin)
- Nhổ bỏ cây bệnh
- Sử dụng giống kháng
- Nghỉ ruộng 1-2 tuần
        """,
        'prevention': """
- Phòng rầy từ sớm
- Giống kháng (TN1, IR36, IR64)
- Gieo đồng loạt
- Vệ sinh ruộng
        """
    }
}

def show_auth_page():
    """Trang đăng nhập/đăng ký"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align:center; color:#60a5fa;'>🌾 Rice Leaf Disease</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Classifier</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký"])
        
        with tab1:
            st.subheader("Đăng Nhập")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Mật khẩu", type="password", key="login_password")
            
            if st.button("Đăng Nhập", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("❌ Vui lòng nhập đầy đủ thông tin")
                else:
                    result = firebase_service.sign_in(email, password)
                    if result['success']:
                        st.session_state.user_id = result['user_id']
                        st.session_state.user_email = email
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
        
        with tab2:
            st.subheader("Đăng Ký Tài Khoản Mới")
            name = st.text_input("Họ tên", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Mật khẩu (tối thiểu 6 ký tự)", type="password", key="signup_password")
            confirm_password = st.text_input("Xác nhận mật khẩu", type="password", key="confirm_password")
            
            if st.button("Đăng Ký", use_container_width=True, type="primary"):
                if not name or not email or not password:
                    st.error("❌ Vui lòng nhập đầy đủ thông tin")
                elif password != confirm_password:
                    st.error("❌ Mật khẩu không khớp")
                else:
                    result = firebase_service.sign_up(email, password, name)
                    if result['success']:
                        st.session_state.user_id = result['user_id']
                        st.session_state.user_email = email
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])

def show_main_app():
    """Trang chính ứng dụng"""
    
    # Hiển thị popup chi tiết nếu được chọn
    if st.session_state.get('selected_analysis'):
        detail = st.session_state['selected_analysis']
        
        # Tạo expander style popup
        with st.container():
            st.markdown("""
            <style>
                .popup-container {
                    background: linear-gradient(135deg, #1f2937, #0f172a);
                    border: 2px solid #3b82f6;
                    border-radius: 16px;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 20px 40px rgba(59, 130, 246, 0.3);
                }
            </style>
            <div class="popup-container">
            """, unsafe_allow_html=True)
            
            col_title, col_close = st.columns([10, 1])
            
            with col_title:
                st.markdown(f"<h2 style='color: #60a5fa; margin: 0;'>📋 Chi Tiết Phân Tích</h2>", unsafe_allow_html=True)
            
            with col_close:
                if st.button("✕", key="close_detail", help="Đóng popup"):
                    del st.session_state['selected_analysis']
                    st.rerun()
            
            st.markdown("---")
            
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                st.markdown("**🖼️ Ảnh Phân Tích:**")
                if 'imageBase64' in detail:
                    try:
                        img_data = base64.b64decode(detail['imageBase64'])
                        img = Image.open(io.BytesIO(img_data))
                        st.image(img, use_column_width=True)
                    except:
                        st.warning("⚠️ Không thể hiển thị ảnh")
                else:
                    st.info("ℹ️ Ảnh không được lưu")
            
            with col_info:
                st.markdown(f"<div style='background: #1e293b; padding: 1.5rem; border-radius: 12px;'>" +
                           f"<h3 style='color: #60a5fa; margin: 0;'>🦠 {detail['diseaseNameVi']}</h3>" +
                           f"<div style='font-size: 2rem; color: #10b981; margin: 0.5rem 0;'>{detail['confidence']:.1f}%</div>" +
                           f"<p style='color: #94a3b8; margin: 0;'>Độ tin cậy</p>" +
                           f"</div>", unsafe_allow_html=True)
                
                st.markdown("**📊 Chi tiết xác suất:**")
                for disease_name, prob in detail['allPredictions'].items():
                    percentage = prob * 100
                    st.progress(min(percentage/100, 1.0), f"{CLASS_NAMES_VI.get(disease_name, disease_name)}: {percentage:.1f}%")
            
            st.markdown("---")
            
            # Khuyến nghị chi tiết
            st.subheader(f"💊 Khuyến Nghị: {RECOMMENDATIONS[detail['diseaseClass']]['name']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🔍 Triệu Chứng Nhận Dạng:**")
                st.markdown(detail['symptoms'])
            
            with col2:
                st.markdown("**🩺 Cách Chữa Trị:**")
                st.markdown(detail['treatment'])
            
            with col3:
                st.markdown("**🛡️ Phòng Ngừa Bệnh:**")
                st.markdown(detail['prevention'])
            
            st.info("ℹ️ Luôn tham khảo chuyên gia nông nghiệp địa phương trước khi áp dụng")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"**👤 {st.session_state.user_email}**")
        if st.button("🚪 Đăng Xuất", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.title("Hướng dẫn sử dụng")
        st.markdown("""
- Bước 1: Chụp ảnh lá lúa rõ nét
- Bước 2: Tải ảnh JPG/PNG
- Bước 3: Chờ phân tích
- Bước 4: Xem kết quả & khuyến nghị

**Lưu ý**:
- Độ tin cậy < 70%: chụp lại
- Tham khảo chuyên gia nông nghiệp
        """)
        
        st.markdown("---")
        st.subheader("Các bệnh khả dĩ")
        for vi_name in CLASS_NAMES_VI.values():
            st.markdown(f"- {vi_name}")
        
        st.markdown("---")
        st.caption("© 2026 Rice Leaf Disease Classifier")
    
    # Main content - Chỉ hiển thị nếu không có popup
    if not st.session_state.get('selected_analysis'):
        tab1, tab2 = st.tabs(["📸 Phân Tích", "📊 Lịch Sử"])
        
        with tab1:
            st.markdown("<h1 style='text-align:center; color:#60a5fa;'>🌾 Phân loại bệnh lá lúa</h1>", 
                       unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;'>Tải ảnh lá lúa lên để nhận chẩn đoán</p>", 
                       unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Chọn ảnh (jpg, jpeg, png)",
                type=['jpg', 'jpeg', 'png'],
                label_visibility="visible"
            )
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Ảnh gốc", width=700)
            
            if st.button("🔬 Phân tích ảnh", type="primary", use_container_width=True):
                with st.spinner("Đang xử lý..."):
                    try:
                        img = np.array(image.convert('RGB'))
                        img_resized = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                        img_normalized = img_resized / 255.0
                        img_batch = np.expand_dims(img_normalized, axis=0).astype(np.float32)
                        
                        # Handle both Keras model and TFLite interpreter
                        if hasattr(model, 'predict'):
                            # Keras model
                            predictions = model.predict(img_batch, verbose=0)[0]
                        else:
                            # TFLite interpreter
                            input_details = model.get_input_details()
                            output_details = model.get_output_details()
                            model.set_tensor(input_details[0]['index'], img_batch)
                            model.invoke()
                            predictions = model.get_tensor(output_details[0]['index'])[0]
                        
                        predicted_idx = np.argmax(predictions)
                        predicted_class = CLASSES[predicted_idx]
                        confidence = predictions[predicted_idx] * 100
                        
                        # Chuyển ảnh thành base64 để lưu
                        buffered = Image.fromarray(np.uint8(img))
                        img_bytes = io.BytesIO()
                        buffered.save(img_bytes, format="PNG")
                        img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
                        
                        # Tự động lưu vào Firebase ngay khi phân tích xong
                        analysis_data = {
                            'imageFileName': uploaded_file.name,
                            'imageBase64': img_base64,  # Lưu ảnh dưới dạng base64
                            'diseaseClass': predicted_class,
                            'diseaseNameVi': CLASS_NAMES_VI[predicted_class],
                            'confidence': float(confidence),
                            'allPredictions': {
                                class_name: float(pred) 
                                for class_name, pred in zip(CLASSES, predictions)
                            },
                            'symptoms': RECOMMENDATIONS[predicted_class]['symptoms'],
                            'treatment': RECOMMENDATIONS[predicted_class]['treatment'],
                            'prevention': RECOMMENDATIONS[predicted_class]['prevention'],
                            'notes': '',
                        }
                        
                        result = firebase_service.save_analysis(
                            st.session_state.user_id,
                            analysis_data
                        )
                        
                        # Lưu vào session state
                        st.session_state.update({
                            'predictions': predictions,
                            'predicted_class': predicted_class,
                            'confidence': confidence,
                            'image_filename': uploaded_file.name,
                            'image_base64': img_base64,
                            'analysis_saved': result['success'],
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
            
            # Hiển thị kết quả nếu có
            if 'confidence' in st.session_state:
                predicted_class = st.session_state['predicted_class']
                confidence = st.session_state['confidence']
                predictions = st.session_state['predictions']
                
                # Thông báo lưu thành công
                if st.session_state.get('analysis_saved'):
                    st.success("✅ Kết quả đã được lưu vào lịch sử phân tích")
                
                st.markdown("<div class='custom-card'><h3 style='margin:0; color:#60a5fa;'>📋 Kết quả chẩn đoán</h3></div>", 
                           unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"""
                    <div class="card" style="text-align: center;">
                        <div style="font-size: 2.8rem; font-weight: 700; color: #60a5fa;">
                            {confidence:.1f}%
                        </div>
                        <div style="font-size: 1.4rem; margin: 0.8rem 0;">
                            {CLASS_NAMES_VI[predicted_class]}
                        </div>
                        <div style="color: #94a3b8; font-size: 0.95rem;">
                            Độ tin cậy
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Xác suất từng lớp**")
                    for disease, prob in zip(CLASSES, predictions):
                        percentage = prob * 100
                        is_max = (disease == predicted_class)
                        bar_color = "#60a5fa" if is_max else "#475569"
                        st.markdown(f"""
                        <div style="margin: 0.6rem 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 0.3rem;">
                                <span>{CLASS_NAMES_VI[disease]}</span>
                                <span>{percentage:.1f}%</span>
                            </div>
                            <div style="background: #1e293b; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background: {bar_color}; height: 100%; width: {percentage}%;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Khuyến nghị
                if predicted_class in RECOMMENDATIONS:
                    rec = RECOMMENDATIONS[predicted_class]
                    st.subheader(f"💊 Khuyến nghị: {rec['name']}")
                    st.markdown(f"**Triệu chứng:** {rec['symptoms']}")
                    
                    col_t, col_p = st.columns(2)
                    
                    with col_t:
                        st.markdown("**🩺 Điều trị**")
                        st.markdown(rec['treatment'])
                    
                    with col_p:
                        st.markdown("**🛡️ Phòng ngừa**")
                        st.markdown(rec['prevention'])
                    
                    st.info("ℹ️ Luôn tham khảo chuyên gia nông nghiệp địa phương trước khi áp dụng")
                
                # Nút xóa kết quả
                if st.button("🗑️ Xóa kết quả", use_container_width=True):
                    for key in ['confidence', 'predictions', 'predicted_class', 'image_filename']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        with tab2:
                st.subheader("📚 Lịch Sử Phân Tích")
                
                # Tìm kiếm
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    search_disease = st.selectbox(
                        "Lọc theo bệnh",
                        ['Tất cả'] + list(CLASS_NAMES_VI.values()),
                        key="filter_disease"
                    )
                
                with col2:
                    min_confidence = st.slider("Độ tin cậy tối thiểu", 0, 100, 0)
                
                with col3:
                    if st.button("🔍 Tìm kiếm", use_container_width=True):
                        st.session_state.search_triggered = True
                
                # Hiển thị kết quả
                if st.session_state.get('search_triggered', True):
                    disease_class = None
                    if search_disease != 'Tất cả':
                        # Convert VI name back to class name
                        for class_name, vi_name in CLASS_NAMES_VI.items():
                            if vi_name == search_disease:
                                disease_class = class_name
                                break
                    
                    history = firebase_service.search_analysis(
                        st.session_state.user_id,
                        disease_class,
                        min_confidence
                    )
                    
                    if history:
                        st.success(f"✅ Tìm thấy {len(history)} kết quả")
                        
                        for idx, record in enumerate(history):
                            with st.expander(f"📝 {record['diseaseNameVi']} - {record['confidence']:.1f}% - {record.get('timestamp', 'N/A')}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown(f"**Ảnh:** {record['imageFileName']}")
                                    # Xử lý timestamp - có thể là string hoặc datetime
                                    timestamp = record.get('timestamp', 'N/A')
                                    if isinstance(timestamp, str):
                                        try:
                                            # Chuyển ISO format string sang datetime
                                            dt = datetime.fromisoformat(timestamp)
                                            time_str = dt.strftime('%d/%m/%Y %H:%M:%S')
                                        except:
                                            time_str = timestamp
                                    else:
                                        time_str = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                                    st.markdown(f"**Thời gian:** {time_str}")
                                    st.markdown(f"**Độ tin cậy:** {record['confidence']:.1f}%")
                                
                                with col2:
                                    st.markdown(f"**Triệu chứng:** {record['symptoms'][:100]}...")
                                    if record.get('notes'):
                                        st.markdown(f"**Ghi chú:** {record['notes']}")
                                
                                st.markdown("**Chi tiết xác suất:**")
                                pred_col1, pred_col2 = st.columns(2)
                                
                                for i, (disease_name, prob) in enumerate(record['allPredictions'].items()):
                                    col = pred_col1 if i % 2 == 0 else pred_col2
                                    with col:
                                        st.write(f"{CLASS_NAMES_VI[disease_name]}: {prob*100:.2f}%")
                                
                                col_view, col_delete = st.columns(2)
                                
                                with col_view:
                                    if st.button("👁️ Xem Chi Tiết", key=f"view_{record['id']}"):
                                        st.session_state.selected_analysis = record
                                        st.rerun()
                                
                                with col_delete:
                                    if st.button("🗑️ Xóa", key=f"delete_{record['id']}"):
                                        result = firebase_service.delete_analysis(
                                            st.session_state.user_id,
                                            record['id']
                                        )
                                        if result['success']:
                                            st.success(result['message'])
                                            st.rerun()
                                        else:
                                            st.error(result['message'])
                    else:
                        st.info("ℹ️ Không có kết quả nào")

# Main logic
if st.session_state.user_id is None:
    show_auth_page()
else:
    show_main_app()

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("© 2026 - Rice Leaf Disease Classifier • Firebase Edition")
