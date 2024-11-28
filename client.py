import aiohttp
import asyncio
import logging
import time
from typing import Optional, Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def format_time(seconds):
    return f"{seconds:.1f}s"

class TranslationClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_status(self):
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        async with self.session.get(f"{self.base_url}/status") as response:
            return await response.json()

    async def wait_for_completion(self, timeout: float = 300.0, progress_callback: Optional[Callable] = None) -> dict:
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job timed out after {timeout} seconds")
            
            status_response = await self.get_status()
            if progress_callback:
                progress_callback(status_response)
            
            if status_response["result"] in ["error", "completed"]:
                return status_response
            
            await asyncio.sleep(0.1)

async def interactive_session():
    from server import TranslationServer
    import threading
    import uvicorn

    def run_server(server):
        uvicorn.run(server.app, host="127.0.0.1", port=8000, log_level="critical")

    print("\n🎥 HEYGEN VIDEO TRANSLATION SIMULATOR")
    print("="*60)

    server = TranslationServer()
    server_thread = threading.Thread(target=run_server, args=(server,))
    server_thread.daemon = True
    server_thread.start()
    await asyncio.sleep(1)

    async with TranslationClient("http://localhost:8000") as client:
        while True:
            try:
                video_length = float(input("\nEnter video length in seconds (max 60s): "))
                if video_length <= 0:
                    print("Video length must be positive")
                    continue
                if video_length > 60:
                    print("Video length cannot exceed 60 seconds")
                    continue
                
                error_prob = server.calculate_error_probability(video_length)
                print(f"\nJob Configuration:")
                print(f"├── Video Length: {format_time(video_length)}")
                print(f"└── Error Probability: {error_prob * 100}%")
                print("\nProcessing:")
                
                start_time = time.time()
                server.create_job(video_length)
                
                try:
                    def progress_callback(response):
                        elapsed = time.time() - start_time
                        status = response['result']
                        print(f"└── [{format_time(elapsed)}] {status}", end="\r")

                    final_status = await client.wait_for_completion(
                        timeout=video_length * 2,
                        progress_callback=progress_callback
                    )
                    
                    elapsed = time.time() - start_time
                    print(f"\n\nFinal Status: {final_status['result'].upper()}")
                    print(f"Total Time: {format_time(elapsed)}")
                    
                except Exception as e:
                    print(f"\n\nError: {str(e)}")
                
                if input("\nTry another video? (y/n): ").lower() != 'y':
                    break
                    
            except ValueError:
                print("Please enter a valid number")

if __name__ == "__main__":
    asyncio.run(interactive_session())