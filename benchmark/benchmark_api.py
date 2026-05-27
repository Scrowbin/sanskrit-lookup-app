import time
import urllib.request
import urllib.error
import json
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

API_URL = "http://127.0.0.1:5199"

def run_benchmarks():
    print("=" * 50)
    print(" SANSKRIT HTTP API BENCHMARK ".center(50))
    print("=" * 50)

    # 1. Start Server & Measure HTTP Warmup Time
    print("\n[1] Measuring Server Startup & FST Warmup via HTTP...")
    
    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logic_handler", "api_server.py"))
    
    # Start the server as a background process
    print("    Spawning api_server.py...")
    start_time = time.time()
    server_proc = subprocess.Popen([sys.executable, server_path, "--port", "5199"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Poll until the health endpoint returns OK
    startup_time = 0
    attempts = 0
    while attempts < 100:
        try:
            req = urllib.request.Request(f"{API_URL}/api/health")
            with urllib.request.urlopen(req, timeout=1) as response:
                if response.status == 200:
                    startup_time = time.time() - start_time
                    break
        except (urllib.error.URLError, ConnectionError):
            time.sleep(0.1)
            attempts += 1
            
    if startup_time == 0:
        print("    [!] Failed to start server in time!")
        server_proc.terminate()
        return
        
    print(f" -> Time from spawn to HTTP ready (App Load Time): {startup_time:.4f} seconds")

    # 2. Benchmark Full Paradigm Request
    print("\n[2] Measuring Full Paradigm API Request Latency...")
    test_cases_full = [
        {"root": "bhū", "class": "1", "derivative": "primary"},
        {"root": "kṛ", "class": "8", "derivative": "primary"},
        {"root": "gam", "class": "1", "derivative": "causative"},
        {"root": "stu", "class": "2", "derivative": "intensive"},
    ]
    
    total_latency = 0
    print(f"    Sending {len(test_cases_full)} unique requests to /api/conjugate/derivative")
    for req_data in test_cases_full:
        data = json.dumps(req_data).encode("utf-8")
        req = urllib.request.Request(f"{API_URL}/api/conjugate/derivative", data=data, headers={"Content-Type": "application/json"})
        
        t0 = time.time()
        try:
            with urllib.request.urlopen(req) as response:
                duration = time.time() - t0
                if response.status == 200:
                    total_latency += duration
                    print(f"      - {req_data['root']} ({req_data['derivative']}): {duration:.4f}s")
                else:
                    print(f"      - {req_data['root']} ({req_data['derivative']}): FAILED ({response.status})")
        except Exception as e:
            print(f"      - {req_data['root']} ({req_data['derivative']}): FAILED ({e})")
            
    print(f" -> Average HTTP response latency: {(total_latency / len(test_cases_full)):.4f} seconds")

    # 3. Benchmark Declension Request
    print("\n[3] Measuring Declension API Request Latency...")
    test_cases_decl = [
        {"stem": "rāma", "gender": "m"},
        {"stem": "nadī", "gender": "f"},
        {"stem": "jñāna", "gender": "n"},
    ]
    
    decl_latency = 0
    print(f"    Sending {len(test_cases_decl)} unique requests to /api/declense")
    for req_data in test_cases_decl:
        data = json.dumps(req_data).encode("utf-8")
        req = urllib.request.Request(f"{API_URL}/api/declense", data=data, headers={"Content-Type": "application/json"})
        
        t0 = time.time()
        try:
            with urllib.request.urlopen(req) as response:
                duration = time.time() - t0
                if response.status == 200:
                    decl_latency += duration
                    print(f"      - {req_data['stem']} ({req_data['gender']}): {duration:.4f}s")
                else:
                    print(f"      - {req_data['stem']} ({req_data['gender']}): FAILED ({response.status})")
        except Exception as e:
            print(f"      - {req_data['stem']} ({req_data['gender']}): FAILED ({e})")

    print(f" -> Average declension HTTP response latency: {(decl_latency / len(test_cases_decl)):.4f} seconds")

    print("\n" + "=" * 50)
    print(" Cleaning up server...")
    server_proc.terminate()
    print(" Benchmark Complete.")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    run_benchmarks()
