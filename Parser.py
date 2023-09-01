import re
import time
import pandas as pd
import requests
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class WLWParser:
    def __init__(self):
        self.chrome_service = Service('/Applications/Google Chrome.app/Contents/MacOS/chromedriver')
        self.data = []
        self.class_names = ['CybotCookiebotDialogButtonAcceptAll', "company-name", "address",
                            "email", "website-button", "phone-button", "copy-button"]
        self.id_nums = None
        self.tag_names = "h1"
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.path_to_save = "./base/base_{}.html"
        self.database_filename = "BAZA_NIEMCY"

    def collect_data(self, firm_url):
        result = []
        self.driver.get(firm_url)
        time.sleep(1)
        name = self.driver.find_element(By.TAG_NAME, self.tag_names)
        address = "no address"
        email = " "
        website = "no_website"
        telephone = "no_tel"
        result.append(name.text)

        try:
            button_overlay = self.driver.find_element(By.CLASS_NAME, "modal-overlay-close")
            button_overlay.click()
        except NoSuchElementException:
            pass

        try:
            address = self.driver.find_element(By.CLASS_NAME, self.class_names[2])
            result.append(address.text.rstrip())
        except NoSuchElementException:
            result.append(address)

        try:
            phone_button = self.driver.find_element(By.CLASS_NAME, self.class_names[5])
            phone_button.click()
            telephone = self.driver.find_element(By.CLASS_NAME, self.class_names[6])
            result.append(telephone.get_attribute("href"))
        except NoSuchElementException:
            result.append(telephone)

        try:
            self.driver.refresh()
            email = self.driver.find_element(By.CLASS_NAME, self.class_names[3])
            result.append(email.text.rstrip())
        except NoSuchElementException:
            result.append(email)

        try:
            web_button = self.driver.find_element(By.CLASS_NAME, "more-button")
            web_button.click()
            website = self.driver.find_element(By.CLASS_NAME, self.class_names[4])
            result.append(website.get_attribute("href"))
        except Exception:
            pass
        try:
            website = self.driver.find_element(By.CLASS_NAME, self.class_names[4])
            result.append(website.text.rstrip())
        except NoSuchElementException:
            result.append(website)

        return result

    def parse_links(self, url):
        self.url = url
        self.driver = webdriver.Chrome(service=self.chrome_service, options=self.options)
        self.driver.get(self.url)
        time.sleep(3)
        result = []
        try:
            button1 = self.driver.find_element(By.CLASS_NAME, self.class_names[0])
            button1.click()
        except NoSuchElementException:
            pass
        try:
            button_overlay = self.driver.find_element(By.CLASS_NAME, "modal-overlay-close")
            button_overlay.click()
        except NoSuchElementException:
            pass

        time.sleep(3)
        href = self.driver.find_elements(By.CLASS_NAME, self.class_names[1])
        for elem in href:
            link = elem.get_attribute("href")
            result.append(link)

        for _ in result:
            self.data.append(self.collect_data(_))
        self.driver.close()

    def save_data_to_excel(self):
        df = pd.DataFrame(data=self.data)
        df.to_excel(f'{self.database_filename}.xlsx', 'sheet1', index=False)

    def save_web_pages(self):
        self.driver = webdriver.Chrome(service=self.chrome_service, options=self.options)
        data_to_extract = pd.read_excel(
            f"{self.database_filename}.xlsx")
        count = 1
        for email in data_to_extract['strona_int']:
            if data_to_extract['email'] == ' ':
                url = f"{email}kontakt/"
                try:
                    self.driver.get(url)
                    check_url = self.driver.current_url
                    response = requests.head(check_url)
                    status_code = response.status_code

                    if status_code == 200:
                        count += 1
                        source_page = self.driver.page_source
                        with open(self.path_to_save.format(count), 'w') as file:
                            file.write(source_page)
                        emails = self.the_mail_extractor(count)

                        if len(emails) == 1:
                            data_to_extract['email'] = emails[0]
                        else:
                            for _ in emails:
                                print(_)
                    else:
                        pass
                except Exception:
                    pass

    def the_mail_extractor(self, num_of_file):
        with open(self.path_to_save.format(num_of_file)) as file:
            content = file.read()
            pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            result = re.findall(pattern, content)
            emails = set(result)
            return emails


if __name__ == '__main__':
    URL = ...
    c = WLWParser()
    for _ in range(1, 2):
        c.parse_links(URL.format(f"{_}"))
    c.save_data_to_excel()
    for _ in c.data:
        print(_)
