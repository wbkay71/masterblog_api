from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

# GET endpoint
@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Get sorting parameters
    sort_field = request.args.get('sort', '').lower()
    direction = request.args.get('direction', 'asc').lower()

    # Validate sort field (if provided)
    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Use 'title' or 'content'"}), 400

    # Validate direction
    if direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'"}), 400

    # If no sort field specified, return original order
    if not sort_field:
        return jsonify(POSTS)

    # Sort the posts
    sorted_posts = sorted(
        POSTS,
        key=lambda post: post[sort_field].lower(),
        reverse=(direction == 'desc')
    )

    return jsonify(sorted_posts)


# ADD endpoint
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


# DELETE endpoint
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Find the post with the given id
    post_to_delete = None
    post_index = None

    for index, post in enumerate(POSTS):
        if post['id'] == post_id:
            post_to_delete = post
            post_index = index
            break

    # If post not found, return 404
    if post_to_delete is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    # Delete the post
    POSTS.pop(post_index)

    # Return success message
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


# UPDATE endpoint
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # Get JSON data from request
    data = request.get_json()

    # Find the post with the given id
    post_to_update = None

    for post in POSTS:
        if post['id'] == post_id:
            post_to_update = post
            break

    # If post not found, return 404
    if post_to_update is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    # Update only provided fields
    if data and 'title' in data:
        post_to_update['title'] = data['title']

    if data and 'content' in data:
        post_to_update['content'] = data['content']

    # Return the updated post
    return jsonify(post_to_update), 200


# SEARCH endpoint
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Get query parameters
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # If no search parameters provided, return all posts
    if not title_query and not content_query:
        return jsonify(POSTS)

    # Filter posts based on search criteria
    matching_posts = []

    for post in POSTS:
        # Check if title matches (case-insensitive)
        if title_query and title_query in post['title'].lower():
            matching_posts.append(post)
            continue

        # Check if content matches (case-insensitive)
        if content_query and content_query in post['content'].lower():
            matching_posts.append(post)

    return jsonify(matching_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)