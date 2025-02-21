#!/bin/bash
# Render 배포 시 Tesseract-OCR 강제 설치
apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev

# Tesseract 실행 경로 확인 (설치된 위치 출력)
echo "✅ Tesseract 설치 완료, 실행 경로 확인:"
which tesseract
tesseract --version
