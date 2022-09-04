#!/usr/bin/env python3
"""This will probably never work, it looks like xfinity's anti-bot software
is very good
"""
import numpy as np

from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox()
driver.get("https://login.xfinity.com/login")


email_form = driver.find_element(By.ID, "user")
email_form.click()
for key in "dyga9911@colorado.edu":
    email_form.send_keys(key)
    WebDriverWait(driver, np.random.random() * 0.1 + 0.05)
lets_go = driver.find_element(By.ID, "sign_in")
WebDriverWait(driver, np.random.random() * 0.5 + 0.1)
lets_go.click_and_hold()
WebDriverWait(driver, np.random.random() * 0.5 + 0.1)
lets_go.release()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "passwd"))
                               )
passwd = driver.find_element(By.ID, "passwd")
password = getpass.getpass()
passwd.send_keys(password)
lets_go = driver.find_element(By.ID, "sign_in")
lets_go.click()

