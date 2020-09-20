from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import re

import sqlite3

driver = webdriver.Chrome()
conn = sqlite3.connect('main.db')
c = conn.cursor()

id_count = 0

def get_book_info(name):
        driver.get("http://google.com")
        inputElement = driver.find_element_by_name("q")
        inputElement.send_keys(name + " site:librarything.com\n")
        driver.find_element_by_tag_name("cite").click()

        description = driver.find_elements_by_class_name("wslsummary")[0].text
        title_des = driver.find_elements_by_class_name("headsummary")[0].text
        tag_des = driver.find_elements_by_class_name("tag")

        largest = 0
        tags = ""
        for i in tag_des:
                t = int(re.findall(r'\d+', i.value_of_css_property("font-size"))[0])
                if t > largest:
                        tags = i.text
                        largest = t

        title = re.findall(r"(?P<name>[A-Za-z\t' -:.]+)", title_des)
        date = driver.find_element_by_xpath('//td[@fieldname="originalpublicationdate"]').text
        
        with open('static/images/Books/' + title[0] + '.png', "wb") as file:
                file.write(driver.find_element_by_xpath('//div[@id="maincover"]/img').screenshot_as_png)

        driver.get("http://google.com")
        inputElement = driver.find_element_by_name("q")
        inputElement.send_keys(name + " site:amazon.in\n")
        driver.find_element_by_tag_name("cite").click()
        link = driver.current_url

        id_count += 1

        c.execute("INSERT INTO Listing (id, name, summary, date_published, author, tag, external_link, likes, is_author) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (id_count, title[0], description, date,title[1][3: len(title[1])], tags, link, 0, 0))
        

        print(link)
        print(title[0])
        print(title[1][3: len(title[1])])
        print(date)
        print(tags)
        print(description)

books = open("books.txt", "r")


for i in books.readlines():
        id_count += 1
        get_book_info(i)

books.close()
driver.close()