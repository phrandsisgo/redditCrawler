from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from storeDB import store_posts_data

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

def run_crawler(db_name):
    posts_data = []
    if posts:
        for post in posts[:3]:
            post_title = post.text
            post_url = post.get_attribute("href")
            print(post_url)
            print(f"Title: {post_title}")
            
            #get the datetime to print of the post with the <time> tag embedded within the span.search-time tag
            post_time = post.find_element(By.XPATH, "./ancestor::div[contains(@class, 'search-result')]//span[contains(@class, 'search-time')]/time").get_attribute("datetime")
            user = post.find_element(By.XPATH, "./ancestor::div[contains(@class, 'search-result')]//a[contains(@class, 'author')]").text
            print(f"Time: {post_time}")
            # Open the link of the post in a new tab
            driver.execute_script("window.open(arguments[0], '_blank');", post_url)
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            
            # Extract and print the main post text within the <div> tag with class 'md'
            post_content = driver.find_element(By.XPATH, "//div[contains(@class, 'entry unvoted')]//div[contains(@class, 'md')]")
            paragraphs = post_content.find_elements(By.TAG_NAME, "p")
            for paragraph in paragraphs:
                print(paragraph.text)
            print("\n end of post \n\n")
            post_text = "\n".join([paragraph.text for paragraph in paragraphs])
            posts_data.append({
                "title": post_title,
                "time_of_post": post_time,
                "post_text": post_text,
                "user": user,  # Placeholder for user, modify as needed
                "url": post_url
            })
            
            # Close the current tab and switch back to the original tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # Close the browser
    driver.quit()
    
    # Store posts data into the database
    store_posts_data(db_name, posts_data)

if __name__ == "__main__":
    run_crawler("reddit-crawler.db")