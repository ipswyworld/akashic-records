import requests
import json

API_BASE = "http://localhost:8001"

def test_pii_redaction():
    print("--- Testing Pillar 3: PII Redaction ---")
    query = "My email is secret_agent@example.com and my phone is +1-555-0199. What is my mission?"
    payload = {"query": query, "user_id": "system_user"}
    
    try:
        r = requests.post(f"{API_BASE}/query/rag", json=payload)
        if r.status_code == 200:
            data = r.json()
            print(f"Original Query: {query}")
            # We can't easily see the scrubbed query sent to the LLM from the response 
            # unless we modified the response to show it.
            # But we can check if the 'privacy_redaction' flag is present.
            print(f"Privacy Flag: {data.get('privacy_redaction')}")
            print(f"Response: {data.get('answer')}")
            
            # Let's also test the clipper endpoint if possible, but that needs a real URL.
            # Instead, let's verify the redactor directly if we can import it.
            print("PII Redaction test sent successfully.")
        else:
            print(f"Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

def test_visual_scraper_telemetry():
    print("\n--- Testing Pillar 1: Visual Scraper Telemetry ---")
    payload = {
        "type": "ELEMENT_TARGETED",
        "title": "Targeted: #price-tag",
        "url": "https://example.com/shop",
        "content": "$99.99",
        "user_id": "system_user"
    }
    
    try:
        r = requests.post(f"{API_BASE}/telemetry", json=payload)
        if r.status_code == 200:
            print("Telemetry successfully vaulted.")
            print(f"Logged Activity: {r.json().get('activity_type')}")
        else:
            print(f"Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_pii_redaction()
    test_visual_scraper_telemetry()
