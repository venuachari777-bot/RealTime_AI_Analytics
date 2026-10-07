import os
import time
import json
import random
from datetime import datetime, timezone

# Sample user pool & cities for realism
USERS = [f"USER_{i:04d}" for i in range(101, 130)]
CITIES = ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai"]
DEVICE_TYPES = ["Mobile_Android", "Mobile_iOS", "Web_Chrome", "Unknown_Proxy"]

# Buffer file path
BUFFER_FILE = os.path.join(os.path.dirname(__file__), "live_stream.jsonl")

def generate_transaction():
    """Simulates a live incoming payment transaction."""
    user = random.choice(USERS)
    receiver = random.choice(USERS)
    while receiver == user:
        receiver = random.choice(USERS)
        
    device = random.choice(DEVICE_TYPES)
    location = random.choice(CITIES)
    
    # 90% normal transactions, 10% potential anomalies (fraud spikes)
    is_anomaly_candidate = random.random() < 0.10
    
    if is_anomaly_candidate:
        amount = round(random.uniform(25000.0, 95000.0), 2)
        device = "Unknown_Proxy"
        status = "PENDING_REVIEW"
    else:
        amount = round(random.uniform(50.0, 4500.0), 2)
        status = "COMPLETED"

    transaction_record = {
        "transaction_id": f"TXN_{int(time.time() * 1000)}_{random.randint(10, 99)}",
        "sender_id": user,
        "receiver_id": receiver,
        "amount": amount,
        "location": location,
        "device": device,
        "status": status,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return transaction_record

def start_stream(interval_seconds=1):
    """Continuously generates transactions and writes to a live stream file."""
    print("🚀 [Producer Started] Streaming live transactions to buffer... (Press Ctrl+C to stop)")
    try:
        while True:
            txn = generate_transaction()
            
            # Append record to buffer file
            with open(BUFFER_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(txn) + "\n")
                
            print(f"Pushed: {txn['transaction_id']} | Amount: ₹{txn['amount']} | City: {txn['location']}")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 [Producer Stopped] Transaction stream terminated.")

if __name__ == "__main__":
    start_stream(interval_seconds=1.2)