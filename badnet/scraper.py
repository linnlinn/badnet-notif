import os
import time
import html
import re
import pandas as pd
from datetime import datetime
import logging
from decouple import config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select


from badnet.tournament import Tournament
from badnet.mailer import Mailer

gmail = Mailer(user = 'annonces.tournois.bad@gmail.com', password = config('PASSWORD'))

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

        affichage = self.driver.find_element('class name', 'b-views')
        affichage.find_elements('tag name','li')[2].click()
    
        time.sleep(15)
        print('affichage => liste')

        departements = {'75':'62','77':'63','78':'64','91':'65','92':'66','93':'67','94':'68','95':'69','60':'100'}
        for departement, departement_code in departements.items():
            print(departement)
            print("page d'acceuil chargée")
            #ligue_selector = Select(self.driver.find_element("id","ligue"))
            #ligue_selector.select_by_value('12')

            departement_selector = Select(self.driver.find_element("id","departement"))
            departement_selector.select_by_value(departement_code)
            time.sleep(15)

            

            tournaments=self.driver.find_element('id', 'search_results').find_elements('class name', 'row')
            #print(tournaments.text)
            print(f"trouvé {len(tournaments)} tournois")
            time.sleep(15)
            #
            try:
                pages = self.driver.find_element('class name', 'pager')
                next_page = pages.find_element('xpath', '//a[text()="›"]')
                pager="›" in pages.text
                
            except:
                pager = False
            
            for tournament in tournaments:
                url = tournament.get_attribute("href")
                name = html.unescape(tournament.find_element('class name', 'name').text)
                date = tournament.find_element('class name', 'date').text
                ville = tournament.find_element('class name', 'location').text
                self.tournaments.append(Tournament(name=name, url=url, departement = departement, date=date, ville = ville))
                self.tournaments_df = pd.concat([pd.DataFrame({
                    'id':url.split("=")[-1],
                    'name':name,
                    'url':url,
                    'departement':departement,
                    'date':date,
                    'source':'badnet',
                    'description': '',
                    'date_publication':datetime.now()
                }, index=[0]
                ),self.tournaments_df.loc[:]]).reset_index(drop=True)

            while pager:
                next_page.click()    
                time.sleep(15)
                tournaments=self.driver.find_element('id', 'search_results').find_elements('class name', 'row')
                pages = self.driver.find_element('class name', 'pager')
                try:
                    next_page = pages.find_element('xpath', '//a[text()="›"]')
                    pager="›" in pages.text
                except:
                    pager = False
                
                for tournament in tournaments:
                    url = tournament.get_attribute("href")
                    name = html.unescape(tournament.find_element('class name', 'name').text)
                    date = tournament.find_element('class name', 'date').text
                    ville = tournament.find_element('class name', 'location').text
                    self.tournaments.append(Tournament(name=name, url=url, departement = departement, date=date, ville = ville))
                    self.tournaments_df = pd.concat([pd.DataFrame({
                        'id':url.split("=")[-1],
                        'name':name,
                        'url':url,
                        'departement':departement,
                        'date':date,
                        'source':'badnet',
                        'description': '',
                        'date_publication':datetime.now()
                    }, index=[0]
                    ),self.tournaments_df.loc[:]]).reset_index(drop=True)
                print(pages.text, pager)
            
            time.sleep(1)

    def quit(self):
        self.driver.quit()