import requests
import json
import time
import os

API_BASE = "http://127.0.0.1:8001"

print("=====================================================")
print(" 🏛️ AKASHA - SOVEREIGN VAULT & OUROBOROS STRESS TEST")
print("=====================================================")

def check_backend_health():
    print(f"[?] Checking Akasha Archivist at {API_BASE}...")
    try:
        res = requests.get(f"{API_BASE}/", timeout=5)
        if res.status_code == 200:
            print("✅ Archivist is AWAKE.")
            return True
        else:
            print(f"❌ Backend returned error: {res.text}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def submit_wikipedia(topic):
    print(f"\n[1] Submitting Wikipedia Artifact: {topic}")
    try:
        res = requests.post(f"{API_BASE}/sync/wikipedia?topic={topic}", timeout=30)
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Ingested: {data.get('title')}")
            print(f"🔒 Ouroboros Subchain TX: {data.get('transaction_id')}")
            print(f"🛡️ Sovereign Vault ID: {data.get('vault_id')}")
        else:
            print(f"❌ Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

def check_subchain_status():
    print("\n[?] Checking Bifrost Subchain Status...")
    try:
        res = requests.get(f"{API_BASE}/subchain/status", timeout=5)
        if res.status_code == 200:
            data = res.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Subchain endpoint error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    if check_backend_health():
        check_subchain_status()
        
        # 1. Trigger first transaction
        submit_wikipedia("Cryptography")
        time.sleep(2)
        
        # 2. Trigger second transaction
        submit_wikipedia("Directed_acyclic_graph")
        time.sleep(2)
        check_subchain_status()
        
        # 3. Trigger third transaction
        print("\n⚠️ SUBMITTING 3rd ARTIFACT: EXPECTING OUROBOROS ANCHOR EVENT ⚠️")
        submit_wikipedia("Library_of_Alexandria")
        time.sleep(2)
        
        check_subchain_status()
    
    print("\n✅ Stress Test Sequence Finished.")
