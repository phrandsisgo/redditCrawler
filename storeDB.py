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

    # Create the comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique ID for each comment
            post_id INTEGER NOT NULL,              -- ID of the post this comment belongs to
            parent_id INTEGER,                     -- ID of the parent comment (NULL for top-level comments)
            user TEXT NOT NULL,                  -- username of the comment
            comment_body TEXT NOT NULL,            -- The content of the comment
            permalink TEXT NOT NULL,               -- The permalink of the comment
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE, -- Link to the post
            FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE -- Link to the parent comment
        )
    ''')

    conn.commit()
    conn.close()

def store_posts_data(db_name, posts_data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    post_ids = []
    
    for post in posts_data:
        cursor.execute('''
            INSERT INTO posts (title, time_of_post, post_text, user, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (post['title'], post['time_of_post'], post['post_text'], post['user'], post['url']))
        post_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    return post_ids

def store_comments_data(db_name, post_id, comments_data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    for comment in comments_data:
        cursor.execute('''
            INSERT INTO comments (post_id, parent_id, user, comment_body, permalink)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            post_id,
            comment.get('parent_id'),
            comment.get('author'),
            comment.get('comment_body'),
            comment.get('permalink')
        ))
    
    conn.commit()
    conn.close()

def store_single_post(db_name, post):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (title, time_of_post, post_text, user, url)
        VALUES (?, ?, ?, ?, ?)
    ''', (post['title'], post['time_of_post'], post['post_text'], post['user'], post['url']))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

# Example usage
if __name__ == "__main__":
    current_datetime = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    db_name = f'reddit_{current_datetime}.db'
    create_database(db_name)