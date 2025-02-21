import os
import re
import pytesseract
import pandas as pd
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO

# ✅ Tesseract 환경 변수 설정
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata"

# ✅ Flask 서버 설정
app = Flask(__name__)
CORS(app)  # CORS 활성화

# ✅ Google Sheets API URL (Apps Script에서 생성한 Web App URL 입력)
SHEET_API_URL = "https://script.google.com/macros/s/AKfycbxyz123/exec"  # 📌 실제 Web App URL 입력

def load_excel():
    """ Google Sheets에서 데이터를 가져와 데이터프레임으로 변환 """
    try:
        response = requests.get(SHEET_API_URL)
        if response.status_code != 200:
            print(f"❌ Google Sheets API 요청 실패 (HTTP {response.status_code})")
            return None
        
        data = response.json()
        df = pd.DataFrame(data)
        print(f"✅ Google Sheets 데이터 로드 완료 (총 {len(df)}개 항목)")
        return df
    except Exception as e:
        print(f"❌ Google Sheets 데이터 로드 오류: {str(e)}")
        return None  

def preprocess_image(image):
    """ 이미지 대비 및 선명도 조정하여 OCR 인식률 향상 """
    image = image.convert("L")  # 그레이스케일 변환
    image = image.filter(ImageFilter.SHARPEN)  # 선명도 증가
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # 대비 조정 (2.0 배)
    return image

@app.route("/")
def home():
    """ 기본 경로(/) 요청 시 안내 메시지 """
    return "✅ Flask 서버 실행 중! /verify 엔드포인트 사용 가능."

@app.route("/verify", methods=["POST"])
def verify():
    """ 이미지 인증 API """
    try:
        if "image" not in request.files:
            return jsonify({"success": False, "message": "이미지를 업로드해주세요!"}), 400

        image_file = request.files["image"]
        image = Image.open(image_file)

        # ✅ 이미지 전처리 적용
        image = preprocess_image(image)

        # ✅ OCR 실행
        text = pytesseract.image_to_string(image, lang="kor")

        # ✅ 로그 출력 (OCR로 추출된 텍스트 확인)
        print(f"📌 OCR 추출된 텍스트:\n{text}")

        if "당첨" not in text:
            return jsonify({"success": False, "message": "❌ 인증 실패! '당첨'이 포함되지 않았습니다."}), 400

        match = re.search(r"\b\d{5}\b", text)  # 5자리 숫자 찾기
        if not match:
            return jsonify({"success": False, "message": "❌ 인증 실패! 접수번호(5자리 숫자)를 찾을 수 없습니다."}), 400

        receipt_number = match.group()

        # ✅ Google Sheets 데이터 가져오기
        df = load_excel()
        if df is None:
            return jsonify({"success": False, "message": "서버 오류: Google Sheets 데이터를 불러올 수 없습니다."}), 500

        # ✅ 접수번호 대조
        match = df[df["접수번호"] == int(receipt_number)]
        if not match.empty:
            return jsonify({"success": True, "message": f"✅ 인증 성공! 접수번호: {receipt_number}"})
        else:
            return jsonify({"success": False, "message": "❌ 인증 실패! 접수번호가 일치하지 않습니다."}), 400

    except Exception as e:
        print(f"📌 서버 오류 발생: {str(e)}")
        return jsonify({"success": False, "message": f"서버 오류 발생: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
