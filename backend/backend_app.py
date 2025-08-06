from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


# NEU: Add endpoint
@app.route('/api/posts', methods=['POST'])
def add_post():
    # Get JSON data from request
    data = request.get_json()

    # Error handling - check if title and content exist
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'title' not in data:
        return jsonify({"error": "No title provided"}), 400

    if 'content' not in data:
        return jsonify({"error": "No content provided"}), 400

    # Generate new ID (highest ID + 1)
    if POSTS:
        new_id = max(post['id'] for post in POSTS) + 1
    else:
        new_id = 1

    # Create new post
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content']
    }

    # Add to POSTS list
    POSTS.append(new_post)

    # Return the new post with status 201
    return jsonify(new_post), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)