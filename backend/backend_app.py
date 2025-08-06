from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint  # NEU
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Swagger Configuration
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Initial posts data
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

# GET endpoint
@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Check if pagination is requested
    page_param = request.args.get('page')
    per_page_param = request.args.get('per_page')

    # Get sorting parameters
    sort_field = request.args.get('sort', '').lower()
    direction = request.args.get('direction', 'asc').lower()

    # Validate sort field (if provided)
    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Use 'title' or 'content'"}), 400

    # Validate direction
    if direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'"}), 400

    # Apply sorting if requested
    posts_to_return = POSTS.copy()
    if sort_field:
        posts_to_return = sorted(
            posts_to_return,
            key=lambda post: post[sort_field].lower(),
            reverse=(direction == 'desc')
        )

    # If no pagination params, return simple array (for frontend compatibility)
    if page_param is None and per_page_param is None:
        return jsonify(posts_to_return)

    # Parse pagination parameters
    try:
        page = int(page_param) if page_param else 1
        per_page = int(per_page_param) if per_page_param else 10
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    # Validate pagination parameters
    if page < 1 or per_page < 1:
        return jsonify({"error": "Page and per_page must be positive"}), 400

    # Calculate pagination
    total_posts = len(posts_to_return)
    start = (page - 1) * per_page
    end = start + per_page

    # Get paginated posts
    paginated_posts = posts_to_return[start:end]

    # Return paginated response with metadata
    return jsonify({
        'posts': paginated_posts,
        'pagination': {
            'total': total_posts,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_posts + per_page - 1) // per_page,
            'has_next': end < total_posts,
            'has_prev': page > 1
        }
    })

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

    # Create new post with extended fields
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content'],
        'author': data.get('author', 'Anonymous'),  # Optional mit Default
        'created_at': datetime.now().isoformat(),  # Automatisch
        'tags': data.get('tags', []),  # Optional, Default: leere Liste
        'category': data.get('category', 'General'),  # Optional mit Default
        'likes': 0  # Automatisch 0
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