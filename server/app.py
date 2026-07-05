from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import jwt
import datetime
from flask_bcrypt import Bcrypt
import uuid
import os 
from pathlib import Path
from dotenv import load_dotenv
import json 


load_dotenv()

SERVER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SERVER_DIR.parent
CLIENT_DIST_DIR = PROJECT_DIR / 'client' / 'dist'
BOOKS_FILE = SERVER_DIR / 'books.json'
BLOG_POSTS_FILE = SERVER_DIR / 'blog_posts.json'

#instantiate the app
app = Flask(__name__, static_folder=str(CLIENT_DIST_DIR), static_url_path='/static')
bcrypt = Bcrypt(app)
app.config.from_object(__name__)

#enable cors
CORS(app, resources= {r'/*': {"origins": '*'}})

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

#is it worth creating an actual database for one user login? 
#probably not

users_db = {
    "admin": {
        "username": ADMIN_USERNAME,
        "password": bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')  # Store hashed password
    }
}

with open(BOOKS_FILE, 'r') as f:
    BOOKS = json.load(f)

with open(BLOG_POSTS_FILE, 'r') as f:
    BLOG_POSTS = json.load(f)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users_db.get(username)

    if user and bcrypt.check_password_hash(user['password'], password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'])

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'message': 'Token is valid', 'username': data['username']})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/api/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        BOOKS.append({
            'id' : uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book Added!'

        with open(BOOKS_FILE, 'w') as f:
            json.dump(BOOKS, f, indent=4)
    else:
        response_object['books'] = BOOKS
    return jsonify(response_object)

@app.route('/api/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        BOOKS.append({
            'id' : uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read'),
        })
        response_object['message'] = 'Book updated!'

        # Save the updated list of books to the JSON file
        with open(BOOKS_FILE, 'w') as f:
            json.dump(BOOKS, f, indent=4)

    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book Removed!'

        # Save the updated list of books to the JSON file
        with open(BOOKS_FILE, 'w') as f:
            json.dump(BOOKS, f, indent=4)

    return jsonify(response_object)

@app.route('/api/posts', methods=['GET', 'POST'])
def all_posts():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        BLOG_POSTS.append({
            'id': post_data.get('id') or uuid.uuid4().hex,
            'title': post_data.get('title'),
            'date': post_data.get('date'),
            'readTime': post_data.get('readTime'),
            'excerpt': post_data.get('excerpt'),
            'book': post_data.get('book'),
            'tags': post_data.get('tags', []),
        })
        response_object['message'] = 'Post Added!'

        with open(BLOG_POSTS_FILE, 'w') as f:
            json.dump(BLOG_POSTS, f, indent=4)
    else:
        response_object['posts'] = BLOG_POSTS
    return jsonify(response_object)

def remove_book(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            BOOKS.remove(book)
            return True
    return False

#sanity check route
@app.route('/api/ping', methods=['GET'])
def ping_pong():
    return jsonify("pong")

# Serve the built Vue frontend and fall back to index.html for client-side routes.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_client(path):
    requested_path = CLIENT_DIST_DIR / path
    if path and requested_path.is_file():
        return send_from_directory(CLIENT_DIST_DIR, path)
    return send_from_directory(CLIENT_DIST_DIR, 'index.html')

if __name__ == '__main__':
    app.run()