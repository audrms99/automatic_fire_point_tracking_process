# automatic_fire_point_tracking_process

2024-2학기 캡스톤 디자인 프로젝트

## 프로젝트 설명

화재 감지 시스템 (Fire Detection System)
프로젝트 개요
이 프로젝트는 실시간 영상에서 화재를 감지하고, 화재 발생 시 즉각적인 알림을 제공하는 시스템입니다. YOLO 기반의 객체 감지와 팬-틸트 카메라 제어를 통해 효과적인 화재 모니터링을 구현했습니다.

## 주요 기능

- 실시간 화재 감지: YOLOv3를 사용한 실시간 화재 감지
- 자동 카메라 제어: 팬-틸트 각도 자동 조절
- SMS 알림 시스템: 화재 감지 시 자동 SMS 발송
- 서버 연동: 감지 데이터 실시간 서버 전송

## 시스템 구성

### 1. 화재 감지 모듈 (`yolov3_detector.py`)

- YOLOv3 기반 객체 감지
- 화재 감지를 위한 커스텀 모델 사용
- 실시간 영상 처리 및 객체 인식

### 2. 카메라 제어 모듈 (`cal_angle.py`)

- 팬-틸트 카메라 각도 계산
- 화재 위치 기반 최적 각도 산출
- 자동 카메라 포지셔닝

### 3. 알림 시스템 (`cv_handler.py`)

- SMS 발송 기능
- 실시간 알림 처리
- 알림 쿨다운 관리

### 4. 서버 통신 모듈 (`server_connection.py`)

- 실시간 데이터 전송
- 서버 연결 관리
- 감지 데이터 로깅

## 기술 스택

- 언어: Python
- 딥러닝: YOLOv3
- 영상처리: OpenCV
- 통신: Socket
- SMS: Coolsms API

## 설치 및 실행

1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

2. 설정 파일 생성

- `config.example.py`를 `config.py`로 복사하고 필요한 설정 입력
- API 키, 서버 정보 등 설정

3. 실행

```bash
python main.py
```

## 설정

`config.py`에서 다음 설정을 관리:

- SMS 설정 (API 키, 발신번호 등)
- 카메라 설정 (스트림 URL, 해상도)
- YOLO 모델 설정
- 서버 연결 설정
- 각도 계산 설정

## 주의사항

- 보안을 위해 `config.py` 파일은 반드시 `.gitignore`에 포함
- SMS 발송 기능 사용 시 Coolsms API 키 필요
- YOLO 모델 파일은 용량 문제로 별도 다운로드 필요

## 라이센스

MIT License

## 기여

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다.

## 연락처

- 이메일: myeonggeun.kim@gmail.com
- 깃허브: https://github.com/myeonggeun
