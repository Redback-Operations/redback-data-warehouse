# Test file with intentional security vulnerabilities

# SQL Injection vulnerability
def unsafe_sql_query(user_input):
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    return query

# Hardcoded secrets
# Check with Tristan 
API_KEY = "1234567890abcdef"
SECRET_TOKEN = "my_super_secret_token"