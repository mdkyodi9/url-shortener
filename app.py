# Import necessary libraries
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import uuid
import re
import os

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS for all routes, allowing cross-origin requests from the frontend
CORS(app)

# This dictionary will act as our "database" to store URL mappings.
# In a real-world application, this should be replaced with a persistent database.
url_mapping = {}

# Regex for basic URL validation
url_regex = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)')

def generate_short_key():
    """Generates a unique 6-character short key."""
    while True:
        # Generate a random 6-character string from a UUID
        key = uuid.uuid4().hex[:6]
        if key not in url_mapping:
            return key

# NEW: Added a simple root route for health checks and verification
@app.route('/', methods=['GET'])
def home():
    """Provides a simple response to indicate the service is running."""
    return "URL Shortener Backend is running!", 200

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """
    API endpoint to shorten a URL.
    - Expects a JSON payload with a 'url' key.
    - Generates a unique short key and stores the mapping.
    - Returns the short key. The frontend will construct the full URL.
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

    # Return a JSON response with the short key
    return jsonify({'shortKey': short_key}), 201

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
        # Redirect the user to the original URL with a 302 temporary redirect code
        return redirect(long_url, code=302)
    else:
        # If the key is not found, return a 404 Not Found error
        return jsonify({'error': 'URL not found'}), 404

# This part is updated to use Gunicorn for production environments.
# To run locally for development, you can still use 'flask run'
# or use the Gunicorn command line directly: 'gunicorn --bind 0.0.0.0:5000 app:app'
if __name__ == '__main__':
    # Use environment variable for port or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

# To use this with a production server, you need to install Flask, Flask-CORS, and Gunicorn:
# The `requirements.txt` file below lists these dependencies.
