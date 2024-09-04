import os
import pickle

# Potential hardcoded secret
API_KEY = "my_secret_api_key_12345"

def insecure_function(user_input):
    # Potential SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    return query

def insecure_deserialization(data):
    # Potential insecure deserialization
    return pickle.loads(data)

def potential_ssrf(url):
    # Potential SSRF vulnerability
    import requests
    return requests.get(url)

# Potential sensitive data exposure
with open("sensitive_data.txt", "w") as f:
    f.write("This is sensitive data")

# Insufficient logging
def main():
    print("Application started")
    
if __name__ == "__main__":
    main()