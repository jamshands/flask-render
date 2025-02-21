# ✅ Render에서 Tesseract-OCR이 포함된 Ubuntu 기반 컨테이너 생성
FROM python:3.9

# 🔹 시스템 패키지 업데이트 및 Tesseract-OCR 설치
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev

# 🔹 Python 패키지 설치 (requirements.txt 사용)
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 Flask 애플리케이션 코드 복사
COPY . /app

# 🔹 기본 실행 포트 설정
ENV PORT=10000

# 🔹 컨테이너 시작 시 실행할 명령어
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:10000", "app:app"]
