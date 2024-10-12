# 베이스 이미지 설정
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 파일을 /app으로 복사
COPY . .

# requirements.txt에 있는 패키지 설치
RUN pip install -r requirements.txt

# 봇 실행
CMD ["python", "main.py"]
