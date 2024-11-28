import asyncio
import logging
import threading
import time
from client import TranslationClient, format_time
import uvicorn
from server import TranslationServer
from client import TranslationClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def run_server(server):
    uvicorn.run(server.app, host="127.0.0.1", port=8000, log_level="critical")

async def test_workflow():
    server = TranslationServer()
    server_thread = threading.Thread(target=run_server, args=(server,))
    server_thread.daemon = True
    server_thread.start()
    await asyncio.sleep(1)

    test_scenarios = [
        ("Invalid Video Length", -5.0),
        ("Zero Video Length", 0.0),
        ("Short Video (No Error)", 20.0),
        ("Medium Video (Low Error)", 35.0),
        ("Longer Video (Medium Error)", 45.0),
        ("Long Video (High Error)", 52.0),
        ("Very Long Video (Very High Error)", 58.0),
        ("Over Limit Video (Immediate Error)", 65.0)
    ]

    print("\n🎥 HEYGEN VIDEO TRANSLATION TEST SUITE")
    print("="*60)

    async with TranslationClient("http://localhost:8000") as client:
        for i, (name, video_length) in enumerate(test_scenarios, 1):
            print(f"\nTest #{i}: {name}")
            print(f"├── Video Length: {format_time(video_length)}")
            
            try:
                error_prob = server.calculate_error_probability(video_length)
                print(f"└── Error Probability: {error_prob * 100}%")
                print("\nProcessing:")
                
                start_time = time.time()
                server.create_job(video_length)
                
                def progress_callback(response):
                    elapsed = time.time() - start_time
                    status = response['result']
                    print(f"└── [{format_time(elapsed)}] {status}", end="\r")

                final_status = await client.wait_for_completion(
                    timeout=max(video_length * 2, 1.0),
                    progress_callback=progress_callback
                )
                
                elapsed = time.time() - start_time
                print(f"\n\nFinal Status: {final_status['result'].upper()}")
                print(f"Total Time: {format_time(elapsed)}")
                
            except ValueError as e:
                print(f"\nValidation Error: {str(e)}")
            except Exception as e:
                print(f"\nError: {str(e)}")
            
            print("-"*60)

if __name__ == "__main__":
    asyncio.run(test_workflow())