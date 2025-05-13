import argparse
import numpy as np
from PIL import Image
import io
import base64
import easyocr
from flask import Flask, request, jsonify

# Initialize EasyOCR Reader
reader = easyocr.Reader(["en"], model_storage_directory="./EasyOCR")

# Initialize Flask app
app = Flask(__name__)

def extract_text_from_image(base64_image):
    try:
        # Strip base64 header if present
        if base64_image.startswith("data:image"):
            base64_image = base64_image.split(",", 1)[1]

        image_bytes = base64.b64decode(base64_image)
        image_buffer = io.BytesIO(image_bytes)
        image = Image.open(image_buffer).convert("L")  # Convert to grayscale
        open_cv_image = np.array(image)

        result = reader.readtext(open_cv_image, detail=0)
        return result[0].replace(" ", "") if result else "ABCDEF"
    except Exception as e:
        return f"Error processing image: {str(e)}"

@app.route("/extract-text", methods=["POST"])
def extract_text():
    data = request.get_json()
    base64_image = data.get("image", "")
    if not base64_image:
        return jsonify({"error": "No base64 image string provided"}), 400

    extracted_text = extract_text_from_image(base64_image)
    return jsonify({"extracted_text": extracted_text})

@app.route('/')
def health_check():
    return "Server is running", 200

def main():
    parser = argparse.ArgumentParser(description="Run the OCR extraction server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
