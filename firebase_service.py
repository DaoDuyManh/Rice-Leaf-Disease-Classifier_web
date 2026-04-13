"""
Firebase Service Module
Xử lý Authentication, Database operations
"""
from firebase_admin import auth, firestore
from firebase_config import initialize_firebase, get_firestore_client, get_auth_instance
from datetime import datetime
import json
import os
from pathlib import Path


class FirebaseService:
    def __init__(self):
        self.initialized = initialize_firebase()
        # Tạo thư mục để lưu dữ liệu local (demo mode)
        self.local_data_dir = Path('./local_data')
        self.local_data_dir.mkdir(exist_ok=True)
        
        if self.initialized:
            self.db = get_firestore_client()
            self.auth = get_auth_instance()
        else:
            # Demo mode - Firebase not available
            self.db = None
            self.auth = None
            print("⚠️  Demo mode: Firebase features disabled")

    # ============ LOCAL STORAGE (Demo Mode) ============
    
    def _get_user_history_file(self, user_id: str) -> Path:
        """Lấy đường dẫn file JSON lưu lịch sử của user"""
        return self.local_data_dir / f'{user_id}_history.json'
    
    def _load_user_history(self, user_id: str) -> list:
        """Tải lịch sử phân tích của user từ file JSON"""
        history_file = self._get_user_history_file(user_id)
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert timestamp strings back to datetime objects
                    for record in data:
                        if 'timestamp' in record and isinstance(record['timestamp'], str):
                            try:
                                record['timestamp'] = datetime.fromisoformat(record['timestamp'])
                            except:
                                record['timestamp'] = datetime.now()
                    return data
            except:
                return []
        return []
    
    def _save_user_history(self, user_id: str, history: list) -> bool:
        """Lưu lịch sử phân tích của user vào file JSON"""
        history_file = self._get_user_history_file(user_id)
        try:
            # Convert datetime objects to ISO format strings
            data_to_save = []
            for record in history:
                record_copy = record.copy()
                if 'timestamp' in record_copy and isinstance(record_copy['timestamp'], datetime):
                    record_copy['timestamp'] = record_copy['timestamp'].isoformat()
                data_to_save.append(record_copy)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving history: {str(e)}")
            return False


    # ============ AUTHENTICATION ============
    
    def sign_up(self, email: str, password: str, name: str) -> dict:
        """
        Đăng ký user mới
        Returns: {'success': bool, 'user_id': str, 'message': str}
        """
        if not self.initialized:
            return {'success': True, 'user_id': f'demo_{name}_{email.split("@")[0]}', 'message': f'✅ Demo Mode: Đăng ký thành công! Xin chào {name}'}
        
        try:
            # Tạo user với Firebase Auth
            user = self.auth.create_user(email=email, password=password)
            user_id = user.uid
            
            # Lưu user info vào Firestore
            self.db.collection('users').document(user_id).set({
                'email': email,
                'name': name,
                'createdAt': datetime.now(),
                'totalAnalysis': 0,
                'lastAnalysis': None,
            })
            
            return {
                'success': True,
                'user_id': user_id,
                'message': f'✅ Đăng ký thành công! Xin chào {name}'
            }
        except auth.EmailAlreadyExistsError:
            return {'success': False, 'message': '❌ Email này đã được sử dụng'}
        except Exception as e:
            error_str = str(e).lower()
            if 'weak' in error_str or 'password' in error_str:
                return {'success': False, 'message': '❌ Mật khẩu yếu (tối thiểu 6 ký tự)'}
            return {'success': False, 'message': f'❌ Lỗi: {str(e)}'}

    def sign_in(self, email: str, password: str) -> dict:
        """
        Đăng nhập
        Returns: {'success': bool, 'user_id': str, 'message': str}
        """
        if not self.initialized:
            return {'success': True, 'user_id': f'demo_{email.split("@")[0]}', 'message': '✅ Demo Mode: Đăng nhập thành công'}
        
        try:
            # Firebase Admin SDK không hỗ trợ sign-in trực tiếp
            # Sử dụng REST API hoặc client SDK
            # Tạm thời kiểm tra user tồn tại
            users = self.db.collection('users').where('email', '==', email).stream()
            user_list = list(users)
            
            if user_list:
                user_id = user_list[0].id
                return {
                    'success': True,
                    'user_id': user_id,
                    'message': f'✅ Đăng nhập thành công'
                }
            else:
                return {'success': False, 'message': '❌ Email không tồn tại'}
        except Exception as e:
            return {'success': False, 'message': f'❌ Lỗi: {str(e)}'}

    def get_user_info(self, user_id: str) -> dict:
        """Lấy thông tin user"""
        if not self.initialized:
            return {'name': 'Demo User', 'email': f'{user_id.replace("demo_", "")}@demo.com', 'totalAnalysis': 0}
        
        try:
            user_doc = self.db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"❌ Error getting user: {str(e)}")
            return None

    # ============ ANALYSIS HISTORY ============
    
    def save_analysis(self, user_id: str, analysis_data: dict) -> dict:
        """
        Lưu kết quả phân tích vào Firestore (hoặc local storage ở demo mode)
        """
        if not self.initialized:
            # Demo mode - lưu vào file JSON local
            history = self._load_user_history(user_id)
            
            analysis_record = {
                'userId': user_id,
                'timestamp': datetime.now().isoformat(),
                'id': f'demo_{len(history)}_{int(datetime.now().timestamp())}',
                **analysis_data
            }
            
            history.append(analysis_record)
            success = self._save_user_history(user_id, history)
            
            if success:
                return {
                    'success': True,
                    'message': '✅ Demo Mode: Lưu kết quả phân tích thành công',
                    'analysis_id': analysis_record['id']
                }
            else:
                return {
                    'success': False,
                    'message': '❌ Lỗi: Không thể lưu kết quả'
                }
        
        try:
            analysis_record = {
                'userId': user_id,
                'timestamp': datetime.now(),
                **analysis_data
            }
            
            # Thêm vào Firestore
            doc_ref = self.db.collection('analysis_history').add(analysis_record)
            
            # Cập nhật totalAnalysis của user
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'totalAnalysis': firestore.Increment(1),
                'lastAnalysis': datetime.now()
            })
            
            return {
                'success': True,
                'message': '✅ Lưu kết quả phân tích thành công',
                'analysis_id': doc_ref[1].id
            }
        except Exception as e:
            return {'success': False, 'message': f'❌ Lỗi: {str(e)}'}

    def get_analysis_history(self, user_id: str, limit: int = 50) -> list:
        """
        Lấy lịch sử phân tích của user
        Returns: list of analysis records (mới nhất trước)
        """
        if not self.initialized:
            # Demo mode - lấy từ file JSON local
            history = self._load_user_history(user_id)
            # Sắp xếp theo timestamp từ mới nhất đến cũ nhất
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return history[:limit]
        
        try:
            # Lấy tất cả records của user (không dùng order_by vì cần index)
            docs = self.db.collection('analysis_history')\
                .where('userId', '==', user_id)\
                .stream()
            
            records = []
            for doc in docs:
                record = doc.to_dict()
                record['id'] = doc.id
                records.append(record)
            
            # Sắp xếp client-side theo timestamp từ mới nhất đến cũ nhất
            records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return records[:limit]
        except Exception as e:
            print(f"❌ Error getting history: {str(e)}")
            return []

    def search_analysis(self, user_id: str, disease_class: str = None, 
                       min_confidence: float = 0) -> list:
        """
        Tìm kiếm lịch sử phân tích (filter client-side)
        """
        # Lấy tất cả lịch sử của user
        history = self.get_analysis_history(user_id, limit=1000)
        
        # Lọc theo diseaseClass
        if disease_class:
            history = [h for h in history if h.get('diseaseClass') == disease_class]
        
        # Lọc theo độ tin cậy
        if min_confidence > 0:
            history = [h for h in history if h.get('confidence', 0) >= min_confidence]
        
        return history

    def get_analysis_detail(self, analysis_id: str) -> dict:
        """Lấy chi tiết một kết quả phân tích"""
        if not self.initialized:
            return None
        
        try:
            doc = self.db.collection('analysis_history').document(analysis_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"❌ Error getting analysis: {str(e)}")
            return None

    def delete_analysis(self, user_id: str, analysis_id: str) -> dict:
        """Xóa một kết quả phân tích"""
        if not self.initialized:
            # Demo mode - xóa từ file JSON local
            history = self._load_user_history(user_id)
            
            # Tìm và xóa record theo id
            original_len = len(history)
            history = [h for h in history if h.get('id') != analysis_id]
            
            if len(history) < original_len:
                # Lưu lại file JSON đã xóa
                self._save_user_history(user_id, history)
                return {'success': True, 'message': '✅ Xóa thành công'}
            else:
                return {'success': False, 'message': '❌ Không tìm thấy kết quả'}
        
        try:
            self.db.collection('analysis_history').document(analysis_id).delete()
            return {'success': True, 'message': '✅ Xóa thành công'}
        except Exception as e:
            return {'success': False, 'message': f'❌ Lỗi: {str(e)}'}

    # ============ STATISTICS ============
    
    def get_user_statistics(self, user_id: str) -> dict:
        """Lấy thống kê của user"""
        if not self.initialized:
            return {
                'totalAnalysis': 0,
                'diseaseDistribution': {}
            }
        
        try:
            user = self.get_user_info(user_id)
            history = self.get_analysis_history(user_id, limit=1000)
            
            stats = {
                'totalAnalysis': user.get('totalAnalysis', 0) if user else 0,
                'diseaseDistribution': {}
            }
            
            # Thống kê bệnh
            for record in history:
                disease = record.get('diseaseNameVi', 'Unknown')
                stats['diseaseDistribution'][disease] = \
                    stats['diseaseDistribution'].get(disease, 0) + 1
            
            return stats
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")
            return {}


# Import firestore.Increment
from firebase_admin import firestore
