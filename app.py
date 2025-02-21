import os
import re
import pytesseract
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import requests
from io import BytesIO
import shutil

# ✅ 환경 변수 설정 (Tesseract-OCR 데이터 경로)
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata"

# ✅ Tesseract 실행 경로 확인
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    print(f"✅ Tesseract 실행 경로 확인됨: {tesseract_path}")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print("❌ Tesseract가 설치되지 않았거나, 실행 경로를 찾을 수 없습니다.")
    raise FileNotFoundError("Tesseract-OCR is not installed or not in PATH")

# ✅ Flask 앱 설정
app = Flask(__name__)
CORS(app)  # 모든 도메인에서 접근 가능하도록 CORS 설정

# ✅ Google Sheets API URL (변경 필요)
SHEET_API_URL = "https://script.google.com/macros/s/AKfycbxyz123/exec"

def load_excel():
    """ Google Sheets에서 엑셀 데이터를 가져와 데이터프레임으로 변환 """
    try:
        print("📌 Google Sheets 데이터 로드 시도...")
        response = requests.get(SHEET_API_URL)
        data = response.json()
        df = pd.DataFrame(data)
        print(f"✅ Google Sheets 데이터 로드 완료 (총 {len(df)}개 항목)")
        return df
    except Exception as e:
        print(f"❌ Google Sheets 데이터 로드 오류: {str(e)}")
        return None  

def extract_info_from_image(image):
    """ 이미지에서 '당첨' 단어와 5자리 숫자(접수번호)를 추출 """
    try:
        text = pytesseract.image_to_string(image, lang="kor")  # OCR로 텍스트 추출
        print(f"📌 OCR 추출된 텍스트: {text}")

        if "당첨" not in text:
            return None, "❌ 인증 실패! '당첨'이 포함되지 않았습니다."

        match = re.search(r"\b\d{5}\b", text)  # 5자리 숫자 찾기
        if match:
            return match.group(), None
        return None, "❌ 인증 실패! 접수번호(5자리 숫자)를 찾을 수 없습니다."
    except Exception as e:
        print(f"📌 OCR 오류 발생: {str(e)}")
        return None, f"❌ OCR 오류 발생: {str(e)}"

@app.route("/")
def home():
    """ 기본 경로(/) 요청 시 안내 메시지 출력 """
    return "✅ Flask 서버가 정상적으로 실행 중입니다! /verify 엔드포인트를 사용하세요."

@app.route("/verify", methods=["POST"])
def verify():
    """ 이미지 인증 API """
    try:
        if "image" not in request.files:
            print("❌ 오류: 클라이언트에서 이미지를 전송하지 않음.")
            return jsonify({"success": False, "message": "이미지를 업로드해주세요!"}), 400

        image_file = request.files["image"]
        image = Image.open(image_file)

        receipt_number, error_message = extract_info_from_image(image)

        if not receipt_number:
            print(f"❌ OCR 실패: {error_message}")
            return jsonify({"success": False, "message": error_message}), 400

        df = load_excel()
        if df is None:
            print("❌ 서버 오류: Google Sheets 데이터를 불러올 수 없음.")
            return jsonify({"success": False, "message": "서버 오류: Google Sheets 데이터를 불러올 수 없습니다."}), 500

        match = df[df["접수번호"] == int(receipt_number)]

        if not match.empty:
            print(f"✅ 인증 성공! 접수번호: {receipt_number}")
            return jsonify({"success": True, "message": f"✅ 인증 성공! 접수번호: {receipt_number}"})
        else:
            print("❌ 인증 실패: 접수번호가 일치하지 않음.")
            return jsonify({"success": False, "message": "❌ 인증 실패! 접수번호가 일치하지 않습니다."}), 400

    except Exception as e:
        print(f"📌 서버 오류 발생: {str(e)}")  # 서버 콘솔에 오류 출력
        return jsonify({"success": False, "message": f"서버 오류 발생: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render에서 제공하는 PORT 환경 변수 사용
    app.run(host="0.0.0.0", port=port, debug=True)
