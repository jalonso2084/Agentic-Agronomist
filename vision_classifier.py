import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf # <-- CORRECT IMPORT

# --- 1. SETUP: Load the TFLite model and labels ---
# Load the TFLite model and allocate tensors.
# This uses the interpreter from the main TensorFlow package.
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Get input and output tensor details.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load the labels
with open("labels.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]


# --- 2. THE CLASSIFIER FUNCTION ---
def classify_leaf(image_path: str) -> dict:
    """
    Takes an image path, runs it through the TFLite model,
    and returns the diagnosis and confidence.
    """
    image = Image.open(image_path).convert("RGB")
    size = (224, 224) # The size the model expects
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
    # The model expects a batch of images, so we add a dimension
    data = np.expand_dims(normalized_image_array, axis=0)

    # --- 3. MAKE PREDICTION ---
    interpreter.set_tensor(input_details[0]['index'], data)
    interpreter.invoke()
    
    prediction = interpreter.get_tensor(output_details[0]['index'])
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    return {"diagnosis": class_name[2:], "confidence": float(confidence_score)}


# --- 4. DEMONSTRATION ---
if __name__ == "__main__":
    image_to_test = "test_leaf.jpg"
    
    print(f"--- Analyzing {image_to_test} ---")
    try:
        result = classify_leaf(image_to_test)
        confidence_percent = result['confidence'] * 100
        print(f"Diagnosis: {result['diagnosis']}", flush=True)
        print(f"Confidence: {confidence_percent:.2f}%", flush=True)
    except FileNotFoundError:
        print(f"Error: Make sure you have a test image named '{image_to_test}' in this folder.")
    except Exception as e:
        print(f"An error occurred: {e}")