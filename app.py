import re
import pytesseract
import pandas as pd
from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

# 🔹 Google Sheets에서 엑셀 데이터를 가져오기 (Apps Script API URL 사용)
SHEET_API_URL = "https://script.google.com/macros/s/AKfycbxyz123/exec"

def load_excel():
    response = requests.get(SHEET_API_URL)
    data = response.json()
    df = pd.DataFrame(data)
    return df

# 🔹 이미지에서 "당첨"과 5자리 접수번호 추출
def extract_info_from_image(image):
    text = pytesseract.image_to_string(image, lang="kor")  # OCR 처리 (한국어)
    print(f"추출된 텍스트: {text}")

    # 🔍 "당첨"이 포함된 경우만 처리
    if "당첨" in text:
        match = re.search(r"\b\d{5}\b", text)  # 5자리 숫자 찾기
        if match:
            receipt_number = match.group()
            return receipt_number
    return None

@app.route("/verify", methods=["POST"])
def verify():
    if "image" not in request.files:
        return jsonify({"success": False, "message": "이미지를 업로드해주세요!"})

    image_file = request.files["image"]
    image = Image.open(image_file)

    receipt_number = extract_info_from_image(image)

    if not receipt_number:
        return jsonify({"success": False, "message": "❌ 인증 실패! '당첨' 및 접수번호를 찾을 수 없습니다."})

    df = load_excel()  # 최신 엑셀 데이터 로드

    match = df[df["접수번호"] == int(receipt_number)]

    if not match.empty:
        return jsonify({"success": True, "message": "✅ 인증 성공!", "receipt_number": receipt_number})
    else:
        return jsonify({"success": False, "message": "❌ 인증 실패! 접수번호가 일치하지 않습니다."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
