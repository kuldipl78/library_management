from flask import Flask, request, jsonify, send_file
from flask_mysql_connector import MySQL
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import bcrypt
import csv

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kuldip@9764'
app.config['MYSQL_DATABASE'] = 'library_db'
app.config['JWT_SECRET_KEY'] = 'your_secret_key' 

mysql = MySQL(app)
jwt = JWTManager(app)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        conn = mysql.connection
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        query = "INSERT INTO users (email, password, is_admin) VALUES (%s, %s, %s)"
        cursor.execute(query, (email, hashed_password, is_admin))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and check_password(user['password'], password):
            token = create_access_token(identity={'id': user['id'], 'is_admin': user['is_admin']})
            return jsonify({'token': token}), 200

        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

'''
http://127.0.0.1:5000/register
http://127.0.0.1:5000/login
when person login by postman by post methon then person get token for access. like this {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczMzc2MjMwNywianRpIjoiZGZhOWExYjItZTZhMy00MmY5LThjNzktYTliYjBjMmExMjg0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwiaXNfYWRtaW4iOjF9LCJuYmYiOjE3MzM3NjIzMDcsImNzcmYiOiI3ZmVhODVlNi01ZGMyLTQxYWUtODlhYy1kM2JlN2U4YTU3ZDYiLCJleHAiOjE3MzM3NjMyMDd9.hXo-VcS70cVpq9-Jjq7wnx1GC5JZU0d8KRDf1HixvvI"
}
http://127.0.0.1:5000/add-book
'''
@app.route('/add-book', methods=['POST'])
@jwt_required()
def add_book():
    identity = get_jwt_identity()
    if not identity['is_admin']:
        return jsonify({'error': 'Admin privileges required'}), 

    data = request.json
    title = data.get('title')
    author = data.get('author')
    copies_available = data.get('copies_available', 1)

    if not title or not author:
        return jsonify({'error': 'Title and author are required'}),

    try:
        conn = mysql.connection
        cursor = conn.cursor()
        query = "INSERT INTO books (title, author, copies_available) VALUES (%s, %s, %s)"
        cursor.execute(query, (title, author, copies_available))
        conn.commit()
        return jsonify({'message': 'Book added successfully'}),
    except Exception as e:
        return jsonify({'error': str(e)}),


@app.route('/books', methods=['GET'])
def get_books():
    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM books"
        cursor.execute(query)
        books = cursor.fetchall()
        return jsonify(books), 200
    except Exception as e:
        return jsonify({'error': str(e)}),
        
@app.route('/books', methods=['GET'])
def get_books():
    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM books"
        cursor.execute(query)
        books = cursor.fetchall()
        return jsonify(books), 200
    except Exception as e:
        return jsonify({'error': str(e)}),

## 3. Borrow Requests
@app.route('/borrow-book', methods=['POST'])
@jwt_required()
def borrow_book():
    data = request.json
    user_id = get_jwt_identity()['id']
    book_id = data.get('book_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not book_id or not start_date or not end_date:
        return jsonify({'error': 'Missing required fields'}),

    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT * FROM borrow_requests
            WHERE book_id = %s AND status = 'approved' AND
                  (start_date <= %s AND end_date >= %s)
        """
        cursor.execute(query, (book_id, end_date, start_date))
        if cursor.fetchone():
            return jsonify({'error': 'Book is unavailable for the requested dates'}),

        query = """
            INSERT INTO borrow_requests (user_id, book_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, book_id, start_date, end_date))
        conn.commit()
        return jsonify({'message': 'Borrow request submitted'}),
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/borrow-requests', methods=['GET'])
@jwt_required()
def get_borrow_requests():
    identity = get_jwt_identity()
    if not identity['is_admin']:
        return jsonify({'error': 'Admin privileges required'}),

    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM borrow_requests"
        cursor.execute(query)
        requests = cursor.fetchall()
        return jsonify(requests), 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-history', methods=['GET'])
@jwt_required()
def download_history():
    user_id = get_jwt_identity()['id']

    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT br.id, b.title, br.start_date, br.end_date, br.status
            FROM borrow_requests br
            JOIN books b ON br.book_id = b.id
            WHERE br.user_id = %s
        """
        cursor.execute(query, (user_id,))
        history = cursor.fetchall()

        filename = f"borrow_history_user_{user_id}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'title', 'start_date', 'end_date', 'status'])
            writer.writeheader()
            writer.writerows(history)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
