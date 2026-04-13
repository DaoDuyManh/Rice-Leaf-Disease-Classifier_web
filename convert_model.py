"""
Model conversion script to fix TensorFlow version compatibility issues
Converts the old H5 model to a compatible format
"""
import tensorflow as tf
import os

def convert_model():
    """Convert H5 model to compatible format"""
    h5_file = "best_MobileNetV2_model.h5"
    output_file = "best_MobileNetV2_model_fixed.h5"
    
    try:
        print("Loading model from H5 file...")
        
        # Try loading with compatibility settings
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        
        # Load model
        model = tf.keras.models.load_model(h5_file, compile=False)
        
        print("Model loaded successfully!")
        print(f"Model architecture: {model.summary()}")
        
        # Save in new format
        print(f"Saving to {output_file}...")
        model.save(output_file, overwrite=True)
        
        print(f"✅ Model converted and saved to {output_file}")
        print(f"You can now use {output_file} in your app")
        
        return True
    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")
        return False

if __name__ == "__main__":
    convert_model()
