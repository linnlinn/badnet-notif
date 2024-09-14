import os
import time
import re
from datetime import datetime
import pandas as pd
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from sqlalchemy import text
from decouple import config

from badnet.sql_connection import badminton_db
from badnet.utils import logger
from badnet.error_mailer import Errormailer

gmail_err = Errormailer(user = 'annonces.tournois.bad@gmail.com', password = config('PASSWORD'))

class Tournament:
    def __init__(self, name: str, url: str, date: str, ville: str, nb_participants:str, departement = "99", source="badnet"):
        self.name = name
        self.url = url
        self.id = url.split("=")[-1]
        self.departement = departement
        self.date = date
        self.description = ''
        self.category = [ 'N', 'R', 'D','P', 'NC']
        self.list_classements = ['']
        self.disciplines = ['simple', 'double', 'mixte']
        self.age_group = ['jeunes', 'seniors', 'veterans']
        self.source = source
        self.date_publication = datetime.now()
        self.ville = ville
        self.date_registration_opening = ''
        self.date_registration_closed = ''
        self.ja = 'Non renseigné'
        self.url_affiche='https://badnet.fr/Img/poster/affiche_default.png'
        self.volant = 'Non renseigné'
        self.date_publication = datetime.now()
        if "/" in nb_participants:
            self.max_participants = nb_participants.split('/')[1]
        else:
            self.max_participants = nb_participants
    
    def __repr__(self) -> str:

        return f"Tournament {self.id} {self.name}"

    def get_additional_info(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x6080')
        chromedriver = os.getcwd() + "/chromedriver"
        self.driver = webdriver.Chrome(options = chrome_options, service=Service(chromedriver))
        self.driver.get(self.url)
        time.sleep(10)
        self.driver.find_element("xpath", "/html/body/div[2]/div/section/div/div/nav/ul/li[1]/span").click()
        time.sleep(5)
        infos_tt = self.driver.find_elements("class name", "infos")
        titre = infos_tt[0].find_element('tag name', 'h2').text
        if titre == 'Informations pratiques':
            infos = infos_tt[0]
        else:
            infos = infos_tt[len(infos_tt)-1]
        
        dates = self.driver.find_element("class name", "limit")

        try:
            notes = self.driver.find_element("class name", "text")
            self.description = re.search('Notes des organisateurs\n((.*\n*)*)',notes.text).group(1)
        except Exception as e:
            logger.error(f"Could not extract organizer's notes for {self.name} ID={self.id}")
            logger.error(traceback.format_exc())
            gmail_err.send_error_notification(error=f"Could not extract organizer's notes for {self.name} ID={self.id}")

        ja = re.search('Juge-arbitre : (.+)', infos.text)
        self.ja = ja.group(1) if ja else 'unknown'
        volant = re.search('Volant officiel : (.+)', infos.text)
        self.volant = volant.group(1) if volant else 'unknown'
        
        try:
            simple = infos.text.split('\n')[infos.text.split('\n').index('SIMPLE DOUBLE MIXTE')+1].split()[0]=='check'
            double = infos.text.split('\n')[infos.text.split('\n').index('SIMPLE DOUBLE MIXTE')+1].split()[1]=='check'
            mixte = infos.text.split('\n')[infos.text.split('\n').index('SIMPLE DOUBLE MIXTE')+1].split()[2]=='check'

            discipline = {'simple': simple, 'double': double, 'mixte': mixte}
            self.disciplines = [key for key, value in discipline.items() if value]
            if self.disciplines==[]:
                self.disciplines = ['simple', 'double', 'mixte']
        except Exception as e:
            logger.error(f"Could not extract disciplines for {self.name} ID={self.id}")
            logger.error(traceback.format_exc())
            gmail_err.send_error_notification(error=f"Could not extract disciplines for {self.name} ID={self.id}")

        try:
            jeunes = infos.text.split('\n')[infos.text.split('\n').index('JEUNES SÉNIORS VÉTÉRANS HANDIBAD INCLUSIF')+1].split()[0]=='check'
            seniors = infos.text.split('\n')[infos.text.split('\n').index('JEUNES SÉNIORS VÉTÉRANS HANDIBAD INCLUSIF')+1].split()[1]=='check'
            veterans = infos.text.split('\n')[infos.text.split('\n').index('JEUNES SÉNIORS VÉTÉRANS HANDIBAD INCLUSIF')+1].split()[2]=='check'

            age_group = {'jeunes': jeunes, 'seniors': seniors, 'veterans': veterans}
            self.age_group = [key for key, value in age_group.items() if value]
            print(','.join(self.age_group))
            if self.age_group==[]:
                self.age_group = ['jeunes', 'seniors', 'veterans']
        except Exception as e:
            logger.error(f"Could not extract age groups for {self.name} ID={self.id}")
            logger.error(traceback.format_exc())
            gmail_err.send_error_notification(error=f"Could not extract age groups for {self.name} ID={self.id}")
        
        try:
            classements = infos.text.split('\n')[-1]
            N = 'N' in classements #=='check'
            R = 'R' in classements #=='check'
            D = 'D' in classements
            P = 'P' in classements
            NC = 'check' in classements

            self.list_classements = [x for x in classements.split() if len(x) in (2,3)]

            categories = {'N': N, 'R': R, 'D': D, 'P': P, 'NC': NC}
            self.category = [key for key, value in categories.items() if value]
            if self.category == []:
                self.category = ['N', 'R', 'D','P', 'NC']
        except Exception as e:
            logger.error(f"Could not extract category for {self.name} ID={self.id}")
            logger.error(traceback.format_exc())
            gmail_err.send_error_notification(error=f"Could not extract category for {self.name} ID={self.id}")
        try:
            self.date_registration_opening = dates.text.split('\n')[1]
            self.date_registration_closed = dates.text.split('\n')[3]
        except Exception as e:
            logger.error("Could not extract registration dates for {self.name} ID={self.id}")
            logger.error(traceback.format_exc())    
            gmail_err.send_error_notification(error=f"Could not extract registration dates for {self.name} ID={self.id}")

        self.url_affiche = self.driver.find_element("class name", 'flex.top').find_element("tag name", "figure").find_element("tag name", "a").get_attribute("href")
        
        self.driver.quit()
    
    def is_in_db(self):
        conn = badminton_db.connect()
        result = conn.execute(text(f"SELECT True FROM tournaments WHERE id={self.id}")).fetchone()
        if result:
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
                'date_publication': self.date_publication,
                'disciplines' : ','.join(self.disciplines),
                'agegroup': ','.join(self.age_group),
                'categories': ','.join(self.category),
                'participants': self.max_participants
                }, index=[0]
                )
            tournament.to_sql('tournaments', badminton_db, if_exists='append', index=False)