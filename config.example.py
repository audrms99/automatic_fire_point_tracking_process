# SMS 설정
SMS_CONFIG = {
    'api_key': 'YOUR_API_KEY',
    'api_secret': 'YOUR_API_SECRET',
    'from_number': 'YOUR_SENDER_NUMBER',
    'to_number': 'YOUR_RECEIVER_NUMBER',
    'default_message': "화재가 감지되었습니다! 즉시 확인이 필요합니다.",
    'sms_cooldown': 60
}

# 카메라 설정
CAMERA_CONFIG = {
    'stream_url': "YOUR_STREAM_URL",
    'frame_width': 416,
    'frame_height': 416
}

# YOLO 모델 설정
YOLO_CONFIG = {
    'weights': "path/to/your/weights/file.weights",
    'config': "path/to/your/config/file.cfg",
    'names': "path/to/your/names/file.names",
    'confidence_threshold': 0.5,
    'nms_threshold': 0.4,
    'input_scale': 0.00392
}

# 서버 설정
SERVER_CONFIG = {
    'host': 'YOUR_SERVER_HOST',
    'port': 8000,
    'reconnect_attempts': 3,
    'reconnect_delay': 5
}

# 각도 계산 설정
ANGLE_CONFIG = {
    'position_threshold': 10,
    'pan_range': (-90, 90),
    'tilt_range': (-45, 45)
}

# 디버그 설정
DEBUG_CONFIG = {
    'show_frames': True,
    'save_detections': False,
    'log_level': 'INFO'
}
