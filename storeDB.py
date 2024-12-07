import sqlite3
from datetime import datetime

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            time_of_post DATETIME NOT NULL,
            post_text TEXT NOT NULL,
            user TEXT NOT NULL,
            url TEXT NOT NULL
        )
    ''')

    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            datetime DATETIME NOT NULL,
            comment_body TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')

    conn.commit()
    conn.close()

def store_posts_data(db_name, posts_data, ):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    for post in posts_data:
        cursor.execute('''
            INSERT INTO posts (title, time_of_post, post_text, user)
            VALUES (?, ?, ?, ?)
        ''', (post['title'], post['time_of_post'], post['post_text'], post['user'], post['url']))
    
    conn.commit()
    conn.close()

def store_comments_data(db_name, comments_data):
    # Placeholder function for storing comments data
    pass

# Example usage
if __name__ == "__main__":
    current_datetime = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    db_name = f'reddit_{current_datetime}.db'
    create_database(db_name)