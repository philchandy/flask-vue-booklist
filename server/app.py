from flask import Flask, Response, abort, jsonify, request, send_from_directory
from flask_cors import CORS
import jwt
import datetime
from flask_bcrypt import Bcrypt
import uuid
import os 
import re
from pathlib import Path
from dotenv import load_dotenv
import json 
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse


load_dotenv()

SERVER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SERVER_DIR.parent
CLIENT_DIST_DIR = PROJECT_DIR / 'client' / 'dist'
BOOKS_FILE = SERVER_DIR / 'books.json'
BLOG_POSTS_FILE = SERVER_DIR / 'blog_posts.json'
UPLOAD_DIR = SERVER_DIR / 'uploads'
ALLOWED_IMAGE_EXTENSIONS = {'gif', 'jpeg', 'jpg', 'png', 'webp'}
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'book_blog')
AWS_REGION = os.getenv('AWS_REGION')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_S3_PUBLIC_BASE_URL = os.getenv('AWS_S3_PUBLIC_BASE_URL')
S3_IMAGE_PREFIX = 'blog-images/'

#instantiate the app
app = Flask(__name__, static_folder=str(CLIENT_DIST_DIR), static_url_path='/static')
bcrypt = Bcrypt(app)
app.config.from_object(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

#enable cors
CORS(app, resources= {r'/*': {"origins": '*'}})

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')

missing_auth_settings = [
    name for name, value in {
        'ADMIN_USERNAME': ADMIN_USERNAME,
        'ADMIN_PASSWORD': ADMIN_PASSWORD,
        'SECRET_KEY': SECRET_KEY,
    }.items() if not value
]
if missing_auth_settings:
    raise RuntimeError(f"Missing required auth environment settings: {', '.join(missing_auth_settings)}")

app.config['SECRET_KEY'] = SECRET_KEY

users_db = {
    "admin": {
        "username": ADMIN_USERNAME,
        "password": bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')  # Store hashed password
    }
}

mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = mongo_client[MONGO_DB_NAME]
books_collection = db.books
posts_collection = db.blog_posts
s3_client = boto3.client('s3', region_name=AWS_REGION) if AWS_REGION else boto3.client('s3')

def seed_collection(collection, source_file):
    if collection.count_documents({}) > 0:
        return
    with open(source_file, 'r') as f:
        seed_data = json.load(f)
    if seed_data:
        collection.insert_many(seed_data)

def serialize_documents(cursor):
    return list(cursor)

def serialize_posts(cursor):
    return [serialize_post(post) for post in cursor]

def serialize_post(post):
    post['excerpt'] = rewrite_s3_image_references(post.get('excerpt', ''))
    post['imageUrl'] = rewrite_s3_image_url(post.get('imageUrl'))
    return post

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def decode_authorization_header():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.removeprefix('Bearer ').strip()
    if not token:
        return None
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def s3_image_url(object_key):
    if AWS_S3_PUBLIC_BASE_URL:
        return f"{AWS_S3_PUBLIC_BASE_URL.rstrip('/')}/{object_key}"
    return f"/api/uploads/{object_key}"

def rewrite_s3_image_url(image_url):
    object_key = s3_object_key_from_url(image_url)
    if object_key:
        return s3_image_url(object_key)
    return image_url

def rewrite_s3_image_references(text):
    if not text:
        return text

    rewritten_text = text
    for possible_url in set(re.findall(r'https?://[^\s)"\']+', text)):
        object_key = s3_object_key_from_url(possible_url)
        if object_key:
            rewritten_text = rewritten_text.replace(possible_url, s3_image_url(object_key))
    return rewritten_text

def s3_object_key_from_url(image_url):
    if not image_url or not AWS_S3_BUCKET:
        return None

    if image_url.startswith(S3_IMAGE_PREFIX):
        return image_url

    if image_url.startswith('/api/uploads/'):
        return image_url.removeprefix('/api/uploads/')

    parsed_url = urlparse(image_url)
    if parsed_url.path.startswith('/api/uploads/'):
        return parsed_url.path.removeprefix('/api/uploads/')

    host = parsed_url.netloc.lower()
    bucket_host_prefix = f"{AWS_S3_BUCKET}.s3"
    if host == f"{AWS_S3_BUCKET}.s3.amazonaws.com" or host.startswith(f"{bucket_host_prefix}."):
        return parsed_url.path.lstrip('/')
    return None

def s3_object_keys_from_text(text):
    if not text:
        return set()

    image_urls = re.findall(r'!\[[^\]]*]\(([^)]+)\)', text)
    return {
        object_key for object_key in (s3_object_key_from_url(image_url) for image_url in image_urls)
        if object_key and object_key.startswith(S3_IMAGE_PREFIX)
    }

def s3_object_keys_from_post(post):
    if not post:
        return set()

    object_keys = s3_object_keys_from_text(post.get('excerpt', ''))
    image_url_key = s3_object_key_from_url(post.get('imageUrl'))
    if image_url_key and image_url_key.startswith(S3_IMAGE_PREFIX):
        object_keys.add(image_url_key)
    return object_keys

def delete_s3_objects(object_keys):
    if not AWS_S3_BUCKET or not object_keys:
        return

    for object_key in object_keys:
        try:
            s3_client.delete_object(Bucket=AWS_S3_BUCKET, Key=object_key)
        except ClientError:
            app.logger.warning('Could not delete S3 object %s', object_key)

try:
    mongo_client.admin.command('ping')
    seed_collection(books_collection, BOOKS_FILE)
    seed_collection(posts_collection, BLOG_POSTS_FILE)
except ServerSelectionTimeoutError as exc:
    raise RuntimeError(
        f"Could not connect to MongoDB at {MONGO_URI}. Start MongoDB locally or set MONGO_URI in .env."
    ) from exc

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
    data = decode_authorization_header()
    if not data:
        return jsonify({'message': 'Invalid or missing token'}), 401
    return jsonify({'message': 'Token is valid', 'username': data['username']})

@app.route('/api/uploads', methods=['POST'])
def upload_image():
    if not decode_authorization_header():
        return jsonify({'message': 'Log in to upload images.'}), 401

    if not AWS_S3_BUCKET or not AWS_REGION:
        return jsonify({'message': 'S3 is not configured on the server.'}), 500

    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        return jsonify({'message': 'Choose an image to upload.'}), 400

    if not image_file.mimetype.startswith('image/') or not allowed_image_file(image_file.filename):
        return jsonify({'message': 'Upload a JPG, PNG, GIF, or WebP image.'}), 400

    original_name = secure_filename(image_file.filename)
    extension = original_name.rsplit('.', 1)[1].lower()
    object_key = f"{S3_IMAGE_PREFIX}{uuid.uuid4().hex}.{extension}"

    try:
        s3_client.upload_fileobj(
            image_file,
            AWS_S3_BUCKET,
            object_key,
            ExtraArgs={'ContentType': image_file.mimetype},
        )
    except ClientError:
        return jsonify({'message': 'Could not upload image to S3.'}), 500

    return jsonify({'url': s3_image_url(object_key)})

@app.route('/api/uploads/<path:object_key>', methods=['GET'])
def serve_s3_image(object_key):
    if not AWS_S3_BUCKET:
        abort(404)

    try:
        s3_object = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=object_key)
    except ClientError:
        abort(404)

    return Response(
        s3_object['Body'].read(),
        mimetype=s3_object.get('ContentType', 'application/octet-stream'),
        headers={'Cache-Control': 'public, max-age=31536000'},
    )

@app.route('/api/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        books_collection.insert_one({
            'id' : uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book Added!'
    else:
        response_object['books'] = serialize_documents(books_collection.find({}, {'_id': 0}))
    return jsonify(response_object)

@app.route('/api/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        books_collection.update_one(
            {'id': book_id},
            {'$set': {
                'title': post_data.get('title'),
                'author': post_data.get('author'),
                'read': post_data.get('read'),
            }}
        )
        response_object['message'] = 'Book updated!'

    if request.method == 'DELETE':
        books_collection.delete_one({'id': book_id})
        response_object['message'] = 'Book Removed!'

    return jsonify(response_object)

@app.route('/api/posts', methods=['GET', 'POST'])
def all_posts():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        posts_collection.insert_one({
            'id': post_data.get('id') or uuid.uuid4().hex,
            'title': post_data.get('title'),
            'date': post_data.get('date'),
            'readTime': post_data.get('readTime'),
            'excerpt': post_data.get('excerpt'),
            'book': post_data.get('book'),
            'imageUrl': post_data.get('imageUrl'),
            'tags': post_data.get('tags', []),
        })
        response_object['message'] = 'Post Added!'
    else:
        response_object['posts'] = serialize_posts(posts_collection.find({}, {'_id': 0}))
    return jsonify(response_object)

@app.route('/api/posts/<post_id>', methods=['PUT', 'DELETE'])
def single_post(post_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        existing_post = posts_collection.find_one({'id': post_id}, {'_id': 0})
        post_data = request.get_json()
        updated_post = {
            'excerpt': post_data.get('excerpt'),
            'imageUrl': post_data.get('imageUrl'),
        }
        posts_collection.update_one(
            {'id': post_id},
            {'$set': {
                'title': post_data.get('title'),
                'date': post_data.get('date'),
                'readTime': post_data.get('readTime'),
                'excerpt': post_data.get('excerpt'),
                'book': post_data.get('book'),
                'imageUrl': post_data.get('imageUrl'),
                'tags': post_data.get('tags', []),
            }}
        )
        delete_s3_objects(s3_object_keys_from_post(existing_post) - s3_object_keys_from_post(updated_post))
        response_object['message'] = 'Post updated!'

    if request.method == 'DELETE':
        existing_post = posts_collection.find_one({'id': post_id}, {'_id': 0})
        posts_collection.delete_one({'id': post_id})
        delete_s3_objects(s3_object_keys_from_post(existing_post))
        response_object['message'] = 'Post removed!'

    return jsonify(response_object)

#sanity check route
@app.route('/api/ping', methods=['GET'])
def ping_pong():
    return jsonify("pong")

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

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