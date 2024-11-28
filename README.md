# HeyGen Video Translation Simulator

A client-server implementation simulating HeyGen's video translation service with configurable delays and error rates.

## Features

- Async client implementation with proper resource management
- Configurable error rates based on video length
- Real-time progress tracking
- Random completion delays (90-110% of video length)
- Interactive and automated testing modes

## Error Probability

| Video Length | Error Rate |
|-------------|------------|
| 0-30s       | 0%         |
| 30-40s      | 20%        |
| 40-50s      | 40%        |
| 50-55s      | 60%        |
| 55-60s      | 80%        |
| >60s        | 100%       |

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode
```bash
python client.py
```

### Automated Test Suite
```bash
python test.py
```

### Client Library
```python
async with TranslationClient("http://localhost:8000") as client:
    # Create job on server side first
    server.create_job(video_length)
    
    # Wait for completion with progress updates
    final_status = await client.wait_for_completion(
        timeout=video_length * 2,
        progress_callback=progress_callback
    )
```

## Requirements

- Python 3.7+
- aiohttp
- fastapi
- uvicorn

## Development

The server runs on `http://localhost:8000` with a single endpoint:
- GET /status: Returns current job status (pending/completed/error)
