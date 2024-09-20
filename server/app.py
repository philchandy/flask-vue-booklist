from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import jwt
import datetime
from flask_bcrypt import Bcrypt
import uuid
import os 
from dotenv import load_dotenv
import json 


load_dotenv()

#instantiate the app
app = Flask(__name__, static_folder='../client/dist', static_url_path='')
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

with open('books.json', 'r') as f:
    BOOKS = json.load(f)

BOOKS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'read': True
    }
]

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

        with open('books.json', 'w') as f:
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
        with open('books.json', 'w') as f:
            json.dump(BOOKS, f, indent=4)

    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book Removed!'

        # Save the updated list of books to the JSON file
        with open('books.json', 'w') as f:
            json.dump(BOOKS, f, indent=4)

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

@app.route('/api/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Serve the index.html for all other routes (fallback)
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run()