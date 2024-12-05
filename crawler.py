from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Optional: Konfiguriere Optionen
options = Options()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")  # Fügen Sie diese Zeile hinzu

# Erstelle eine Service-Instanz mit lokalem ChromeDriver
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

print('Chrome WebDriver is ready')

# Navigiere zu Reddit
driver.get("https://old.reddit.com/r/languagelearning/search/?q=flashcards&sort=new")

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

if posts:
    for post in posts:
        post_title = post.text
        post_url = post.get_attribute("href")
        print(post_url)
        print(f"Title: {post_title}")
        
        # Open the link of the post in a new tab
        driver.execute_script("window.open(arguments[0], '_blank');", post_url)
        
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])
        
        # Extract and print all text within <p> tags of the specified classes
        paragraphs = driver.find_elements(By.XPATH, "//form[contains(@class, 'usertext warn-on-unload')]//div[contains(@class, 'md')]//p")
        for paragraph in paragraphs:
            print(paragraph.text)
        
        input("Press Enter to continue...")
        
        # Close the current tab and switch back to the original tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])


# Close the browser
driver.quit()