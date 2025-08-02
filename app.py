# Import necessary libraries from Flask
from flask import Flask, request, jsonify, redirect
# Import CORS to allow the frontend to make requests
from flask_cors import CORS
# Import uuid to generate unique short keys
import uuid
# Import re for simple URL validation
import re

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS for all routes, allowing cross-origin requests from the frontend
CORS(app)

# This dictionary will act as our "database" to store URL mappings.
# Key: short URL path (e.g., "abc123")
# Value: original long URL (e.g., "https://www.example.com")
url_mapping = {}

# Regex for basic URL validation
url_regex = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)')

def generate_short_key():
    """Generates a unique 6-character short key."""
    # Use a loop to ensure the generated key is not already in use
    while True:
        # Generate a random 6-character string from a UUID
        key = uuid.uuid4().hex[:6]
        if key not in url_mapping:
            return key

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """
    API endpoint to shorten a URL.
    - Expects a JSON payload with a 'url' key.
    - Generates a unique short key and stores the mapping.
    - Returns the short URL.
    """
    data = request.get_json()
    long_url = data.get('url')

    # Basic input validation
    if not long_url:
        return jsonify({'error': 'URL not provided'}), 400
    
    # Simple URL format validation
    if not url_regex.match(long_url):
        return jsonify({'error': 'Invalid URL format'}), 400

    # Generate a unique key and store the mapping
    short_key = generate_short_key()
    url_mapping[short_key] = long_url

    # Construct the full short URL
    short_url = f"http://127.0.0.1:5000/{short_key}"
    
    # Return a JSON response with the short URL
    return jsonify({'shortUrl': short_url}), 201

@app.route('/<short_key>', methods=['GET'])
def redirect_to_url(short_key):
    """
    API endpoint to redirect to the original URL.
    - Takes a short key from the URL path.
    - Looks up the key in the mapping.
    - If found, redirects the user to the long URL.
    - If not found, returns a 404 error.
    """
    long_url = url_mapping.get(short_key)
    
    if long_url:
        # Redirect the user to the original URL
        return redirect(long_url, code=302)
    else:
        return jsonify({'error': 'URL not found'}), 404

# Main entry point to run the server
if __name__ == '__main__':
    # The server will run on http://127.0.0.1:5000
    app.run(debug=True)

# To use this, you need to install Flask and Flask-CORS:
# pip install Flask Flask-CORS
# Then, save the code as app.py and run it from your terminal:
# python app.py
