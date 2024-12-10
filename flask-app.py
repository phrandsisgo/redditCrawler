import os
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_posts(db_name):
    try:
        # Get the absolute path of the database file
        db_path = os.path.abspath(db_name)
        print(f"Database path: {db_path}")  # Debugging statement
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        print(f"Connected to database: {db_name}")  # Debugging statement
        
        cursor.execute('SELECT title, time_of_post, post_text, user, url FROM posts')
        posts = cursor.fetchall()
        print(f"Posts: {posts} \n db_name: {db_name}")  # Debugging statement
        
        connection.close()
        print("Connection closed")  # Debugging statement
        return posts
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")  # Debugging statement
        return []


@app.route('/')
def main_page():
    db_files = sorted([f for f in os.listdir('.') if f.startswith('reddit_') and f.endswith('.db')], reverse=True)
    return render_template('index.html', db_files=db_files)

@app.route('/view/<db_name>')
def view_page(db_name):
    # Fetch posts from the selected database
    #print(f"Fetching posts from database: {db_name}")  # Debugging statement
    # db_name = "reddit_08-12-2024_00-03-16.db"
    posts = get_posts(db_name)
    # Convert posts to a list of dictionaries
    posts = [{'title': post[0], 'time_of_post': post[1], 'post_text': post[2], 'user': post[3], 'url': post[4]} for post in posts]
    return render_template('view.html', db_name=db_name, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)