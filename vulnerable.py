import os
import sqlite3

# Hardcoded secret (A3: Sensitive Data Exposure)
secret_key = "mysecretpassword"

# SQL Injection vulnerability (A1: Injection)
def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = %s" % user_id
    cursor.execute(query)
    return cursor.fetchall()

# XSS Vulnerability (A7: Cross-Site Scripting)
def render_output(user_input):
    print("<html><body>Hello, " + user_input + "</body></html>")

# Insecure default configuration (A6: Security Misconfiguration)
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')    #1234
 