from fastapi import FastAPI
from enum import Enum
import time
import random

class JobStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"

class TranslationServer:
    def __init__(self):
        self.app = FastAPI()
        self.start_time = None
        self.completion_time = None
        self.final_status = None
        
        @self.app.get("/status")
        async def get_status():
            if not self.start_time:
                return {"result": JobStatus.ERROR}
            
            current_time = time.time()
            elapsed = current_time - self.start_time
            if elapsed >= self.completion_time:
                return {"result": self.final_status}
            return {"result": JobStatus.PENDING}

    def calculate_error_probability(self, video_length: float) -> float:
        if video_length <= 0:
            raise ValueError("Video length must be positive")
        if video_length > 60:
            return 1.0
        elif video_length <= 30:
            return 0.0
        elif video_length <= 40:
            return 0.2
        elif video_length <= 50:
            return 0.4
        elif video_length <= 55:
            return 0.6
        else:  # 55-60
            return 0.8

    def create_job(self, video_length: float):
        if video_length <= 0:
            raise ValueError("Video length must be positive")
        if video_length > 60:
            self.start_time = time.time()
            self.completion_time = 0
            self.final_status = JobStatus.ERROR
            return
            
        self.start_time = time.time()
        self.completion_time = video_length * random.uniform(0.9, 1.1)
        error_prob = self.calculate_error_probability(video_length)
        self.final_status = JobStatus.ERROR if random.random() < error_prob else JobStatus.COMPLETED

server = TranslationServer()
app = server.app