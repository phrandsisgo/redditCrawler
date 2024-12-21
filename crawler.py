import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json
from storeDB import store_posts_data, create_database
from datetime import datetime


# Optional: Konfiguriere Optionen
options = Options()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")  # Fügen Sie diese Zeile hinzu

# Erstelle eine Service-Instanz mit lokalem ChromeDriver
if os.name == "nt":
    print('Windows')
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    
else: # Linux
    service = Service("/usr/bin/chromedriver")

driver = webdriver.Chrome(service=service, options=options)

print('Chrome WebDriver is ready')

# Navigiere zu Reddit mit dem search keyword "flashcards" und rewstrikt auf r/languagelearning
driver.get("https://old.reddit.com/r/languagelearning/search?q=flashcards&restrict_sr=on&sort=new&t=all")

# Warte bis die Seite vollständig geladen ist
wait = WebDriverWait(driver, 10)

# Versuche den Cookie-Banner zu entfernen
try:
    cookie_banner = driver.find_element(By.CLASS_NAME, "cookie-infobar")
    driver.execute_script("arguments[0].remove();", cookie_banner)
except:
    pass

# Gib den Titel des ersten Posts aus
posts = driver.find_elements(By.XPATH, "//div[not(@class)]//a[contains(@class, 'search-title')]")
print('First Post Title')

def parse_comment(comment_element):
    comment_id = comment_element.get_attribute("data-fullname")
    author = comment_element.get_attribute("data-author")
    permalink = comment_element.get_attribute("data-permalink")
    timestamp_elem = comment_element.find_element(By.XPATH, ".//p[@class='tagline']//time")
    comment_time = timestamp_elem.get_attribute("datetime") if timestamp_elem else None
    
    # Get the comment body
    try:
        body_elem = comment_element.find_element(By.XPATH, ".//div[@class='usertext-body']//div[contains(@class,'md')]")
        comment_body = body_elem.text
    except NoSuchElementException:
        comment_body = ""
    
    # If comment body is empty, set it to "void"
    if not comment_body:
        comment_body = "void"
    
    # Check parent (None if top-level or if it refers to a post)
    parent_id = comment_element.get_attribute("data-parent-id")
    if parent_id and "t3_" in parent_id: 
        parent_id = None
    
    entry = {
        "comment_id": comment_id,
        "parent_id": parent_id,
        "author": author,
        "comment_time": comment_time,
        "comment_body": comment_body,
        "permalink": permalink
    }
    # Recursively parse children
    children_div = comment_element.find_elements(By.XPATH, ".//div[@class='child']//div[starts-with(@id,'thing_t1_')]")
    child_entries = []
    for child in children_div:
        child_entries.extend(parse_comment(child))
    
    return [entry] + child_entries


def parse_comments(driver):
    comments_data = []
    # Find main comment 'thing' elements
    comment_elements = driver.find_elements(By.XPATH, "//div[@class='commentarea']//div[starts-with(@id,'thing_t1_')]")
    for elem in comment_elements:
        # Only parse top-level comments (those not inside another comment's child)
        try:
            parent_check = elem.find_element(By.XPATH, "./ancestor::div[@class='child']")
            if parent_check:
                continue
        except:
            pass
        comments_data.extend(parse_comment(elem))
    return comments_data

def run_crawler(db_name, main=False):
    posts_data = []
    if main:
        create_database(db_name)
    if posts:
        for post in posts[:6]:

            # Get the parent div of the post to scope our searches
            post_parent = post.find_element(By.XPATH, "./ancestor::div[contains(@class, 'search-result')]")
            post_title = post.text
            post_url = post.get_attribute("href")
            print(post_url)
            print(f"Title: {post_title}")
            
            # Search within the post_parent element
            post_time = post_parent.find_element(By.XPATH, ".//span[contains(@class, 'search-time')]/time").get_attribute("datetime")
            user = post_parent.find_element(By.XPATH, ".//a[contains(@class, 'author')]").text
            
            print(f"\nTime: {post_time}")
            print(f"\n\n User: {user}\n\n")
            # Open the link of the post in a new tab
            driver.execute_script("window.open(arguments[0], '_blank');", post_url)
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            
            # Wait for the post content to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "top-matter")))

            try:
                # Get post details from the actual post page using the specific structure
                post_author = driver.find_element(By.XPATH, "//div[contains(@class,'top-matter')]//a[contains(@class,'author')]").text
                post_time = driver.find_element(By.XPATH, "//div[contains(@class,'top-matter')]//time").get_attribute("datetime")
                print(f"Found author: {post_author}")
                print(f"Found time: {post_time}")
            except Exception as e:
                print(f"Error finding post details: {e}")
                post_author = user  # fallback
                post_time = post_time  # fallback

            # Rest of your existing code for content extraction
            post_content = driver.find_element(By.XPATH, "//div[contains(@class, 'entry unvoted')]//div[contains(@class, 'md')]")
            paragraphs = post_content.find_elements(By.TAG_NAME, "p")
            post_text = "\n".join([paragraph.text for paragraph in paragraphs])

            post_data = {
                "title": post_title,
                "time_of_post": post_time,
                "post_text": post_text,
                "user": post_author,
                "url": post_url
            }

            if main:
                from storeDB import store_single_post, store_comments_data
                post_id = store_single_post(db_name, post_data)
                comments_data = parse_comments(driver)
                print(f"Found {comments_data} comments \n\n")
                store_comments_data(db_name, post_id, comments_data)
            else:
                posts_data.append(post_data)
            
            if main:
                store_posts_data(db_name, posts_data)

                #store the comments
                
                #input("Press Enter to continue...")
            
            
            # Close the current tab and switch back to the original tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # Close the browser
    driver.quit()
    
    # Store posts data into the database
    if not main:
        store_posts_data(db_name, posts_data)

if __name__ == "__main__":
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    db_name = f"1reddit-crawler_{current_time}.db"
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    run_crawler(db_path, main=True)