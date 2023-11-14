from decouple import config

from badnet.sql_connection import SqlConnector

import html
from datetime import datetime
from badnet.utils import logger, args

from badnet.tournament import Tournament
from badnet.scraper import BadnetScraper
from badnet.mailer import Mailer
import os


print('start session')
print(f"===========================================")
print(f"start session at {datetime.now()}")
print(f'Environment = {args.env}')
badnet = BadnetScraper(url = "https://badnet.fr/accueil")
print('start tournament extraction')
if args.reload:
    print('Saving tournaments to DB withouth sending notifications')
badnet.extract_tournaments()
badnet.quit()
print(f"Extracted {badnet.tournaments.__len__()} tournaments")
print('end tournament extraction')
#gmail = Mailer(user = 'annonces.tournois.bad@gmail.com', password = config('PASSWORD'))
#print('mailer initialized successfully')

for tournament in badnet.tournaments:
    if not tournament.is_in_db():
        tournament.get_additional_info()
        if any(x in ['seniors', 'veterans'] for x in tournament.age_group) and not args.reload:
            print(f'Sending notification for tournament {tournament.id}')
            print(f'{datetime.now()} Sending notification for tournament {tournament.id} : {tournament.name}')
            print(f'{datetime.now()} Age group for {tournament.name} is {tournament.age_group}')
            #gmail.notify_html_tournament(tournament)
        #tournament.save_to_db()
        print(f'saving tournament {tournament}')
logger.info(msg='end session')



        
    
