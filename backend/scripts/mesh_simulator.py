import time
import requests
import json
import threading

AKASHA_NODE_URL = "http://127.0.0.1:8000"
MESH_NODE_ID = "bifrost_mesh_node_002"

print(f"🌐 Starting Bifrost Mesh Simulator [{MESH_NODE_ID}]")
print("📡 Listening for P2P Subchain Gossip...\n")

def simulate_gossip_protocol():
    last_batch_count = -1
    
    while True:
        try:
            # Simulate a P2P ping to the main Akasha node
            res = requests.get(f"{AKASHA_NODE_URL}/subchain/status")
            if res.status_code == 200:
                data = res.json()
                current_batch = data.get("batch_count", 0)
                pending = data.get("pending_tx_count", 0)
                
                # Check for state changes
                if current_batch > last_batch_count and last_batch_count != -1:
                    print(f"⚡ [GOSSIP ALERT] New Subchain Anchor Detected!")
                    print(f"   => Ouroboros Batch #{current_batch} confirmed by {data.get('bifrost_public_key')[:16]}...")
                    print("   => Synchronizing local DAG state... [OK]\n")
                
                last_batch_count = current_batch
                
                # Status heartbeats
                if pending > 0:
                    print(f"🔄 [MESH SYNC] Node {data.get('bifrost_node_id')[:8]} has {pending} unanchored txs. Waiting for batch...")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Main Akasha Node offline. Waiting for mesh discovery...")
            
        time.sleep(5) # Poll every 5 seconds

if __name__ == "__main__":
    try:
        simulate_gossip_protocol()
    except KeyboardInterrupt:
        print("\n🛑 Mesh Node Offline.")
