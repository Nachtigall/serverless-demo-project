import time

from env_variables import docker_browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Driver:
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()

        if docker_browser:
            self.chrome_options.binary_location = "/opt/chrome/chrome"

        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-dev-tools")
        self.chrome_options.add_argument("--no-zygote")
        self.chrome_options.add_argument("--single-process")
        self.chrome_options.add_argument("window-size=2560x1440")
        self.chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        self.chrome_options.add_argument("--remote-debugging-port=9222")
        self.chrome_options.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'"
        )

        self.driver = webdriver.Chrome("/opt/chromedriver", options=self.chrome_options)

    def scrape_data(self, url: str) -> str:
        """scrapes requested page"""
        self.driver.get(url)
        self.wait_until_completion()

        return self.driver.page_source

    def wait_until_completion(self) -> None:
        """waits until the page have completed loading"""

        state = ""
        while state != "complete":
            time.sleep(1.5)
            state = self.driver.execute_script("return document.readyState")
