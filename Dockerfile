# Python 3.9 이미지를 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일을 컨테이너에 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# main.py 파일을 복사
COPY main.py .

# 봇 실행
CMD ["python", "main.py"]
