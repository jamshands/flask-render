#!/bin/bash
# Render 배포 시 Tesseract-OCR 강제 설치
echo "🔹 시스템 패키지 업데이트 중..."
apt-get update && apt-get install -y tesseract-ocr libleptonica-dev libtesseract-dev

# 🔹 Tesseract 실행 경로 확인 (설치된 위치 출력)
echo "✅ Tesseract 설치 완료, 실행 경로 확인:"
which tesseract
tesseract --version || echo "❌ Tesseract 실행 불가"
