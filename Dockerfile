# Python 베이스 이미지 선택
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 전체 코드를 컨테이너에 복사
COPY . .

# 실행 명령
CMD ["python", "main.py"]
