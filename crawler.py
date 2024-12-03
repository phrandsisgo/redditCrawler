from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Optional: Konfiguriere Optionen
options = Options()
#options.add_argument("--headless")  # Optional: Für Hintergrundausführung
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

# Erstelle eine Service-Instanz mit lokalem ChromeDriver
service = Service("/usr/bin/chromedriver")  # Pfad zum ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

print('Chrome WebDriver is ready')

# Navigiere zu Reddit
driver.get("https://old.reddit.com/r/languagelearning/search/?q=flashcards&sort=new")

# Warte bis die Seite vollständig geladen ist
driver.implicitly_wait(10)

# Gib die titel der ersten 5 Posts aus
posts = driver.find_elements(By.CSS_SELECTOR, "a.search-title")  # Updated syntax
for post in posts[:10]:
    print(post.text)

# Gib den Seitentitel aus
print(driver.title)

# Browser offen halten (optional)
input("Press Enter to close the browser...")
driver.quit()
