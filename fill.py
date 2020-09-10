from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import re

def get_book_info(name):
        driver = webdriver.Chrome()
        driver.get("http://google.com")
        inputElement = driver.find_element_by_name("q")
        inputElement.send_keys(name + " goodreads")
        inputElement.submit()
        driver.find_element_by_tag_name("cite").click()
        description_raw = driver.find_elements_by_id("description")
        description = ' '.join(re.split(r'(?<=[.;?!])\s',description_raw[0].text)[:2])
        author_raw = driver.find_elements_by_id("bookAuthors")
        author = ' '.join(re.split(r'(?<=[,])\s',author_raw[0].text)[:1])
        author = author[3:len(author) - 1]
        title = driver.find_element_by_id("bookTitle").text

        print(title)
        print(author)
        print(description)
        driver.close()

books = ["Harry Potter Deathly Hallows", "Four Hour work week", "Harry Potter Philosopher Stone", "The Butcher", "Tools of Titans"]

for i in books:
        get_book_info(i)