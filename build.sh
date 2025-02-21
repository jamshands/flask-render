#!/bin/bash
# Render 배포 시 Tesseract-OCR 강제 설치
echo "🔹 시스템 패키지 업데이트 중..."
apt-get update && apt-get install -y tesseract-ocr libleptonica-dev libtesseract-dev

# 🔹 Tesseract 실행 경로 확인 (설치된 위치 출력)
echo "✅ Tesseract 설치 완료, 실행 경로 확인:"
which tesseract
tesseract --version || echo "❌ Tesseract 실행 불가"


echo "✅ 시스템 패키지 업데이트 및 Tesseract 설치"
apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

echo "✅ Tesseract 한국어 데이터 파일(kor.traineddata) 다운로드"
mkdir -p /usr/share/tesseract-ocr/5/tessdata
wget -O /usr/share/tesseract-ocr/5/tessdata/kor.traineddata \
    https://github.com/tesseract-ocr/tessdata_best/raw/main/kor.traineddata

echo "✅ TESSDATA_PREFIX 환경 변수 설정"
export TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata"

echo "✅ 설치 완료"
