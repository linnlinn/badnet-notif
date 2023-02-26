import os
import time
import re
from datetime import datetime
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from badnet.sql_connection import badminton_db

class Tournament:
    def __init__(self, name: str, url: str, departement: str, date: str, ville: str, source="badnet"):
        self.name = name
        self.url = url
        self.id = url.split("=")[-1]
        self.departement = departement
        self.date = date
        self.description = ''
        self.category = [ 'N', 'R', 'D','P', 'NC']
        self.disciplines = ['simple', 'double', 'mixte']
        self.source = source
        self.date_publication = datetime.now()
        self.ville = ville
        self.date_registration_opening = ''
        self.date_registration_closed = ''
        self.ja = 'Non renseigné'
        self.url_affiche='https://badnet.fr/Img/poster/affiche_default.png'
        self.volant = 'Non renseigné'
        self.date_publication = datetime.now()
    
    def __repr__(self) -> str:

        return f"Tournament {self.id} {self.name}"

    def get_additional_info(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x6080')
        chromedriver = os.getcwd() + "/chromedriver"
        self.driver = webdriver.Chrome(options = chrome_options, service=Service(chromedriver))
        self.driver.get(self.url)
        time.sleep(3)
        self.driver.find_element("xpath", "/html/body/div[2]/div/section/div/div/nav/ul/li[1]/span").click()
        time.sleep(1)
        infos = self.driver.find_element("class name", "infos")
        
        dates = self.driver.find_element("class name", "limit")

        try:
            notes = self.driver.find_element("class name", "text")
            self.description = re.search('Notes des organisateurs\n((.*\n*)*)',notes.text).group(1)
        except:
            pass
        ja = re.search('Juge-arbitre : (.+)', infos.text)
        self.ja = ja.group(1) if ja else 'unknown'
        volant = re.search('Volant officiel : (.+)', infos.text)
        self.volant = volant.group(1) if volant else 'unknown'
        
        try:
            simple = infos.text.split('\n')[infos.text.split('\n').index('Simple Double Mixte')+1].split()[0]=='check'
            double = infos.text.split('\n')[infos.text.split('\n').index('Simple Double Mixte')+1].split()[1]=='check'
            mixte = infos.text.split('\n')[infos.text.split('\n').index('Simple Double Mixte')+1].split()[2]=='check'

            discipline = {'simple': simple, 'double': double, 'mixte': mixte}
            self.disciplines = [key for key, value in discipline.items() if value]
            if self.disciplines==[]:
                self.disciplines = ['simple', 'double', 'mixte']
        except:
            pass
        try:
            N = infos.text.split('\n')[-1].split()[0]=='check'
            R = infos.text.split('\n')[-1].split()[1]=='check'
            D = infos.text.split('\n')[-1].split()[2]=='check'
            P = infos.text.split('\n')[-1].split()[3]=='check'
            NC = infos.text.split('\n')[-1].split()[4]=='check'

            categories = {'N': N, 'R': R, 'D': D, 'P': P, 'NC': NC}
            self.category = [key for key, value in categories.items() if value]
            if self.category == []:
                self.category = [ 'N', 'R', 'D','P', 'NC']
        except:
            pass
        try:
            self.date_registration_opening = dates.text.split('\n')[1]
            self.date_registration_closed = dates.text.split('\n')[3]
        except:
            pass    

        self.url_affiche = self.driver.find_element("class name", 'flex.top').find_element("tag name", "figure").find_element("tag name", "a").get_attribute("href")
        
        self.driver.quit()
    
    def is_in_db(self):
        if badminton_db.execute(f"SELECT True FROM tournaments WHERE id={self.id}").fetchone():
            return True
        else:
            return False

    def save_to_db(self):
        if not self.is_in_db():
            tournament = pd.DataFrame(
                {'id':self.id,
                'name': self.name,
                'url':self.url,
                'departement': self.departement, 
                'date': self.date,
                'source': "badnet",
                'description': self.description,
                "date_publication": self.date_publication}, index=[0]
                )
            tournament.to_sql('tournaments', badminton_db, if_exists='append', index=False)