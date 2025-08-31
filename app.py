import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Azure! My first Python app deployment."

if __name__ == "__main__":
    # Use PORT environment variable provided by Azure, fallback to 8000 for local development
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
