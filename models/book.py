from app import mysql

class Book:
    @staticmethod
    def get_books():
        query = "SELECT * FROM books"
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
