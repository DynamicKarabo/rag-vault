import requests
import time

def verify_cloud_connection():
    url = "http://127.0.0.1:8000/api/test-brain"
    print("Testing connection to Brain...")
    
    attempts = 0
    while attempts < 5:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                print("\nSUCCESS: Brain is Online")
                print(f"Status: {data.get('status')}")
                print(f"Model: {data.get('model')}")
                print(f"Latency: {data.get('latency')}")
                print(f"Response: {data.get('response')}")
                return
            else:
                print(f"Server Error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"Waiting for server... ({e})")
        
        time.sleep(2)
        attempts += 1
        
    print("FAILED: Could not connect to Brain.")

if __name__ == "__main__":
    verify_cloud_connection()
