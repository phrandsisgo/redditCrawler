from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from storeDB import store_posts_data, create_database
from datetime import datetime


# Optional: Konfiguriere Optionen
options = Options()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")  # Fügen Sie diese Zeile hinzu

# Erstelle eine Service-Instanz mit lokalem ChromeDriver
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

            if main:
                posts_data = []
            
            posts_data.append({
                "title": post_title,
                "time_of_post": post_time,
                "post_text": post_text,
                "user": post_author,
                "url": post_url
            })
            
            if main:
                store_posts_data(db_name, posts_data)
                input("Press Enter to continue...")
            
            
            # Close the current tab and switch back to the original tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # Close the browser
    driver.quit()
    
    # Store posts data into the database
    if not main:
        store_posts_data(db_name, posts_data)

if __name__ == "__main__":
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    db_name = f"1reddit-crawler_{current_time}.db"
    run_crawler(db_name, main=True)