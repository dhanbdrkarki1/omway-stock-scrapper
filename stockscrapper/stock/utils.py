import re
import pandas as pd
import time
from datetime import date, timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

DRIVER_PATH = '/usr/bin/chromedriver'


class Scrapper:
    def __init__(self, url: str, driver_path: str) -> None:
        self.url: str = url
        self.driver_path: str = driver_path
        self.driver: Chrome = self._setup_driver()

    def _setup_driver(self) -> Chrome:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:113.0) Gecko/20100101 Firefox/113.0')
        service = Service(self.driver_path)
        self.driver = Chrome(service=service, options=options)
        self.driver.set_window_size(1920, 1080)
        return self.driver

    def load_page(self, locator: tuple[str, str]) -> WebElement | None:
        """Loads the web page and waits till the target element is found.

        locator - used to find the element
        returns True if found.
        """
        self.driver.get(self.url)
        try:
            element = WebDriverWait(self.driver, timeout=10).until(
                EC.presence_of_element_located(locator)
            )
            return element

        except TimeoutException:
            return None

    def wait_for_element(self, driver, locator, timeout=10):
        """
        Waits for an element to be present on the page.

        :param driver: The WebDriver instance
        :param locator: A tuple containing the method to locate the element (By, value)
        :param timeout: The maximum time to wait for the element (default is 10 seconds)
        :return: The WebElement if found, otherwise raises a TimeoutException
        """
        try:
            # Wait for the element to be present
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            print("Timed out waiting for element to load")
            return None

    def parse_numeric(self, text):
        try:
            # Removes non-numeric characters except for dot and minus
            return float(re.sub(r'[^\d.-]', '', text))
        except ValueError:
            return None


class PriceHistoryScrapper(Scrapper):
    def __init__(self, url: str, driver_path: str) -> None:
        super().__init__(url, driver_path)
        self.locator = (By.ID, 'pricehistory-tab')
        self.content_element = super().load_page(locator=self.locator)
        self.content_element.click()
        self.data = []

    def _get_table_data(self):
        tbody = super().wait_for_element(
            self.driver, locator=(
                By.CSS_SELECTOR, '#pricehistorys > div.table-responsive > table > tbody'
            )
        )
        soup = BeautifulSoup(tbody.get_attribute('outerHTML'), 'lxml')
        rows = soup.find_all('tr')

        columns = ["sn", "date", "open_price", "high_price", "low_price", "close_price",
                   "total_traded_quantity", "total_turnover", "previous_day_closing_price",
                   "week_high_52", "week_low_52", "total_trades", "average_traded_price"]

        for row in rows:
            cols = row.find_all('td')
            row_data = {}
            for i, col in enumerate(cols):
                if i == 1:
                    row_data[columns[i]] = col.get_text(strip=True)
                else:
                    row_data[columns[i]] = self.parse_numeric(
                        col.get_text(strip=True)
                    )
            self.data.append(row_data)

    def scrap_data(self):
        next_button = super().wait_for_element(
            self.driver, locator=(
                By.CSS_SELECTOR, "#pricehistorys > div.pagination_ngx > pagination-controls > pagination-template > ul > li.pagination-next")
        )
        while True:
            self._get_table_data()
            next_button = super().wait_for_element(
                self.driver, locator=(
                    By.CSS_SELECTOR, "#pricehistorys > div.pagination_ngx > pagination-controls > pagination-template > ul > li.pagination-next")
            )
            if 'disabled' in next_button.get_attribute('class'):
                break
            next_button.click()
        return self.data