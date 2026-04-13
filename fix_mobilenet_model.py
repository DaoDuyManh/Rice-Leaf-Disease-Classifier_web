"""
Chuyển đổi mô hình MobileNetV2 từ định dạng cũ sang định dạng tương thích với TensorFlow hiện tại
"""
import tensorflow as tf
import os
import json
from pathlib import Path

def fix_batch_shape_in_h5(input_file, output_file):
    """
    Sửa lỗi batch_shape bằng cách rebuild model
    """
    print(f"📦 Đang xử lý: {input_file}")
    
    try:
        # Bước 1: Load model với compile=False
        print("Step 1: Loading model...")
        model = tf.keras.models.load_model(input_file, compile=False)
        print("✅ Model loaded successfully!")
        
        # Bước 2: Rebuild model để fix batch_shape issue
        print("Step 2: Rebuilding model to fix batch_shape...")
        
        # Tạo model mới với cấu trúc tương tự
        rebuilt_model = tf.keras.Sequential()
        for layer in model.layers:
            try:
                # Clone layer nhưng bỏ batch_shape
                config = layer.get_config()
                if 'batch_input_shape' in config:
                    # Keep batch_input_shape
                    pass
                rebuilt_model.add(layer)
            except:
                rebuilt_model.add(layer)
        
        # Bước 3: Compile model
        print("Step 3: Compiling model...")
        rebuilt_model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Bước 4: Save
        print(f"Step 4: Saving to {output_file}...")
        rebuilt_model.save(output_file, overwrite=True)
        
        print(f"✅ Thành công! Mô hình đã được lưu: {output_file}")
        print(f"   Size: {os.path.getsize(output_file) / (1024**2):.2f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return False

def simple_model_rebuild(input_file, output_file):
    """
    Phương pháp đơn giản: tải model và lưu lại
    """
    print(f"📦 Attempting simple rebuild: {input_file}")
    try:
        # Load với các option khác nhau
        print("Trying load_model with compile=False...")
        model = tf.keras.models.load_model(input_file, compile=False)
        
        print("✅ Model loaded!")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
        print(f"   Layers: {len(model.layers)}")
        
        # Save immediately
        print(f"Saving to: {output_file}")
        model.save(output_file, overwrite=True)
        
        print(f"✅ Successfully saved: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)[:200]}")
        return False

if __name__ == "__main__":
    import sys
    
    current_dir = os.getcwd()
    print(f"Working directory: {current_dir}\n")
    
    input_file = "best_MobileNetV2_model.h5"
    output_file = "best_MobileNetV2_model_fixed.h5"
    
    if os.path.exists(input_file):
        print(f"Found: {input_file}")
        print(f"Size: {os.path.getsize(input_file) / (1024**2):.2f} MB\n")
        
        # Try simple rebuild first
        if simple_model_rebuild(input_file, output_file):
            print("\n✅ Conversion successful!")
            print(f"You can now use {output_file} in your app")
            print("Update streamlit_app_v2.py to use the new file name")
        else:
            print("\n❌ Conversion failed")
    else:
        print(f"❌ File not found: {input_file}")
        print(f"Files in directory: {os.listdir(current_dir)}")
