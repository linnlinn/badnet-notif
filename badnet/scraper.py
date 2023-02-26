import os
import time
import html
import re
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from badnet.tournament import Tournament

class BadnetScraper:
    def __init__(self, url):
        self.url=url
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x6080')
        chromedriver = os.getcwd() + "/chromedriver"
        self.driver = webdriver.Chrome(options = chrome_options, service=Service(chromedriver))
        self.tournaments = []
        self.tournaments_df = pd.DataFrame({'id':pd.Series(dtype='str'), 
            'name': pd.Series(dtype='str'),
            'url':pd.Series(dtype='str'),
            'departement': pd.Series(dtype='str'), 
            'date': pd.Series(dtype='str'),
            'source': pd.Series(dtype='str'),
            'description': pd.Series(dtype='str'),
            "date_publication": pd.Series(dtype='datetime64[ns]')})

    def extract_tournaments(self):
        self.driver.get(self.url)
        time.sleep(10)

        self.driver.find_element("id","btn_card").click()
        time.sleep(3)
        self.driver.find_element("id", "area_9").click()
        self.driver.find_element("id", "btn_young").click()
        self.driver.find_element("id", "btn_handi").click()
        time.sleep(3)
        result = self.driver.find_element("class name", "mod_prog_tournois")
        tournaments = result.find_elements("class name", "bn-link-external")
        for tournament in tournaments:
            url = tournament.get_attribute("href")
            name = html.unescape(tournament.find_element('class name', 'mod_prog_item_data_nom').text.split(']'))
            departement = re.search('\[\d+\]', tournament.find_element('class name', 'mod_prog_item_data_nom').text).group(0)[1:-1]
            titre = html.unescape(name[2]).rstrip()
            date = tournament.find_element('class name', 'mod_prog_item_data_date').text
            ville = tournament.find_element('class name', 'mod_prog_item_data_ville').text
            self.tournaments.append(Tournament(name=titre, url=url, departement = departement, date=date, ville = ville))
            self.tournaments_df = pd.concat([pd.DataFrame({
                'id':url.split("=")[-1],
                'name':titre,
                'url':url,
                'departement':departement,
                'date':date,
                'source':'badnet',
                'description': '',
                'date_publication':datetime.now()
            }, index=[0]
            ),self.tournaments_df.loc[:]]).reset_index(drop=True)

    def quit(self):
        self.driver.quit()