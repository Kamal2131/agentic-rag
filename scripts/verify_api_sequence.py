import time

import requests

BASE_URL = "http://localhost:8000"


def print_step(step):
    print(f"\n{'='*50}")
    print(f"STEP: {step}")
    print(f"{'='*50}")


def verify_api_sequence():
    # 1. Health Check
    print_step("Checking Health")
    try:
        resp = requests.get(f"{BASE_URL}/health/")
        print(f"Health Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 200:
            print("Health check failed!")
            return
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Upload Document
    print_step("Uploading Document")
    doc_content = "The Agentic RAG system uses a three-tier memory architecture: Short-term, Medium-term, and Long-term."
    upload_data = {
        "title": "Memory System Architecture",
        "content": doc_content,
        "metadata": {"category": "architecture"},
    }

    resp = requests.post(f"{BASE_URL}/api/rag/upload/", json=upload_data)
    print(f"Upload Status: {resp.status_code}")
    if resp.status_code == 201:
        doc_id = resp.json().get("id")
        print(f"Document Uploaded. ID: {doc_id}")
    else:
        print(f"Upload Failed: {resp.text}")
        return

    # Wait for indexing (simulated)
    print("\nWaiting for indexing...")
    time.sleep(2)

    # 3. Query Agent
    print_step("Querying Agent")
    query = "How many tiers are in the memory architecture?"
    query_data = {"query": query, "user": "test_user_001"}

    resp = requests.post(f"{BASE_URL}/api/rag/query/", json=query_data)
    print(f"Query Status: {resp.status_code}")

    if resp.status_code == 200:
        result = resp.json()
        print(f"Answer: {result.get('answer')}")

        # Verify sources
        sources = result.get("sources", [])
        print(f"Sources found: {len(sources)}")
        if sources:
            print(f"First Source: {sources[0].get('title')}")

        # Verify steps
        steps = result.get("steps_taken", [])
        print(f"Steps taken: {len(steps)}")
    else:
        print(f"Query Failed: {resp.text}")
        return

    # 3.5. Query Agent (Follow-up)
    print_step("Querying Agent (Follow-up)")
    # Assuming the previous answer mentioned "three tiers" or similar, we ask "What are they?"
    query_followup = "What are they?"
    query_data_followup = {"query": query_followup, "user": "test_user_001"}

    resp = requests.post(f"{BASE_URL}/api/rag/query/", json=query_data_followup)
    print(f"Follow-up Query Status: {resp.status_code}")

    if resp.status_code == 200:
        result = resp.json()
        print(f"Follow-up Answer: {result.get('answer')}")
    else:
        print(f"Follow-up Query Failed: {resp.text}")

    # 4. Check History
    print_step("Checking Chat History")
    resp = requests.get(f"{BASE_URL}/api/rag/chat-history/", params={"user": "test_user_001"})
    print(f"History Status: {resp.status_code}")

    if resp.status_code == 200:
        history = resp.json()
        print(f"History entries: {len(history)}")
        if history:
            last_msg = history[0]
            print(f"Last interaction user: {last_msg.get('user')}")
            # Check if messages exist in the history entry
            messages = last_msg.get("messages", [])
            if messages:
                print(f"Last query in history: {messages[0].get('content')}")
    else:
        print(f"History Check Failed: {resp.text}")


if __name__ == "__main__":
    verify_api_sequence()
