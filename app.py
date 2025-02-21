import os
import re
import pytesseract
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)
CORS(app)  # 🔹 CORS 설정 (모든 도메인 허용)

# 🔹 Google Sheets에서 엑셀 데이터를 가져오기 (Apps Script API URL 사용)
SHEET_API_URL = "https://script.google.com/macros/s/AKfycbxyz123/exec"

def load_excel():
    """ Google Sheets에서 엑셀 데이터를 가져와 데이터프레임으로 변환 """
    response = requests.get(SHEET_API_URL)
    data = response.json()
    df = pd.DataFrame(data)
    return df

def extract_info_from_image(image):
    """ 이미지에서 '당첨' 단어와 5자리 숫자(접수번호)를 추출 """
    text = pytesseract.image_to_string(image, lang="kor")  # OCR로 텍스트 추출
    print(f"추출된 텍스트: {text}")

    if "당첨" in text:
        match = re.search(r"\b\d{5}\b", text)  # 5자리 숫자 찾기
        if match:
            receipt_number = match.group()
            return receipt_number
    return None

@app.route("/")
def home():
    """ 기본 경로(/) 요청 시 안내 메시지 출력 """
    return "✅ Flask 서버가 정상적으로 실행 중입니다! /verify 엔드포인트를 사용하세요."

@app.route("/verify", methods=["POST"])
def verify():
    """ 이미지 인증 API """
    if "image" not in request.files:
        return jsonify({"success": False, "message": "이미지를 업로드해주세요!"}), 400

    image_file = request.files["image"]
    
    try:
        image = Image.open(image_file)
    except Exception as e:
        return jsonify({"success": False, "message": f"이미지 처리 오류: {str(e)}"}), 400

    receipt_number = extract_info_from_image(image)

    if not receipt_number:
        return jsonify({"success": False, "message": "❌ 인증 실패! '당첨' 및 접수번호를 찾을 수 없습니다."}), 400

    df = load_excel()  # 최신 엑셀 데이터 로드

    match = df[df["접수번호"] == int(receipt_number)]

    if not match.empty:
        return jsonify({"success": True, "message": "✅ 인증 성공!", "receipt_number": receipt_number})
    else:
        return jsonify({"success": False, "message": "❌ 인증 실패! 접수번호가 일치하지 않습니다."}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render에서 제공하는 PORT 환경 변수 사용
    app.run(host="0.0.0.0", port=port, debug=True)
