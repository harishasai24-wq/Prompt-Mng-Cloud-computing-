import requests
import sys

BASE_URL = "http://localhost:5001/api"

def test_register():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "testuser_repro",
        "email": "testuser_repro@example.com",
        "password": "password123",
        "full_name": "Test User Repro"
    }
    
    print(f"Sending POST request to {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("Registration successful!")
            return True
        elif response.status_code == 409:
            print("User already exists (this might be expected if run multiple times)")
            return True
        else:
            print("Registration failed!")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_register()
    if not success:
        sys.exit(1)
