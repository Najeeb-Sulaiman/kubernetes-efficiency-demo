
import concurrent.futures
import time
import urllib.request

URL = "http://localhost:8000/process?duration=2"

CONCURRENT_WORKERS = 20
TEST_DURATION_SECONDS = 90

stop_at = time.time() + TEST_DURATION_SECONDS


def send_request():
    while time.time() < stop_at:
        try:
            with urllib.request.urlopen(URL, timeout=15) as response:
                response.read()
        except Exception as error:
            print(f"Request failed: {error}")


print(f"Starting {CONCURRENT_WORKERS} concurrent workers")

with concurrent.futures.ThreadPoolExecutor(
    max_workers=CONCURRENT_WORKERS
) as executor:

    futures = [
        executor.submit(send_request)
        for _ in range(CONCURRENT_WORKERS)
    ]

    concurrent.futures.wait(futures)

print("Load test completed")
