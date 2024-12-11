from crawler import run_crawler
from storeDB import create_database
from datetime import datetime
from flaskapp import app

def main():
    # Create database with current datetime
    current_datetime = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    db_name = f'reddit_{current_datetime}.db'
    create_database(db_name)
    
    # Run the crawler
    run_crawler(db_name)

if __name__ == "__main__":
    #main() # Not needed since db is created by the web app (flaskapp.py - UI)
    app.run(debug=True)