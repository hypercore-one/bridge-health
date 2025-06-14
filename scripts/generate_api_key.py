#!/usr/bin/env python3
"""
API Key Generator for Zenon Orchestrator Status API

This script generates secure API keys that can be manually added to the .env file.
"""
import os
import sys
import secrets
import string

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_api_key(prefix="zn_api_key", length=32):
    """Generate a secure API key with the given prefix."""
    # Generate random string with letters and digits
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}_{random_part}"

def main():
    """Generate API keys with different purposes."""
    print("🔑 Zenon Orchestrator Status API Key Generator")
    print("=" * 50)
    
    # Generate different types of API keys
    keys = [
        ("Admin", generate_api_key("zn_admin")),
        ("ReadOnly", generate_api_key("zn_readonly")),
        ("Monitor", generate_api_key("zn_monitor")),
        ("Dashboard", generate_api_key("zn_dashboard")),
        ("External", generate_api_key("zn_external"))
    ]
    
    print("\n📋 Generated API Keys:")
    print("-" * 30)
    for purpose, key in keys:
        print(f"{purpose:10}: {key}")
    
    print("\n🔧 Usage Instructions:")
    print("-" * 20)
    print("1. Copy the keys you want to use")
    print("2. Add them to your .env file in the API_KEYS variable:")
    print("   API_KEYS=key1,key2,key3")
    print("3. Restart the application")
    
    print("\n📝 Example .env entry:")
    print("-" * 20)
    all_keys = ",".join([key for _, key in keys])
    print(f"API_KEYS={all_keys}")
    
    print("\n🌐 Example API Usage:")
    print("-" * 20)
    example_key = keys[0][1]
    print(f"curl -H 'X-API-Key: {example_key}' http://localhost:5001/api/status")
    print(f"curl http://localhost:5001/api/status?api_key={example_key}")

if __name__ == "__main__":
    main()