from app import mysql

class User:
    @staticmethod
    def create_user(email, password, is_admin=False):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        query = "INSERT INTO users (email, password, is_admin) VALUES (%s, %s, %s)"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (email, hashed_password, is_admin))
        mysql.connection.commit()
        return cursor.lastrowid

    @staticmethod
    def get_user_by_email(email):
        query = "SELECT * FROM users WHERE email = %s"
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute(query, (email,))
        return cursor.fetchone()
