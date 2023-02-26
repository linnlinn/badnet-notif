from decouple import config

from badnet.sql_connection import SqlConnector

import html

#from tournament import Tournament
from badnet.scraper import BadnetScraper
from badnet.mailer import Mailer


print('start session')
badnet = BadnetScraper(url = "https://www.badnet.org/Src/")
print('start tournament extraction')
badnet.extract_tournaments()
badnet.quit()
print('end tournament extraction')
gmail = Mailer(user = 'annonces.tournois.bad@gmail.com', password = config('PASSWORD'))
print('mailer initialized successfully')

for tournament in badnet.tournaments:
    if not tournament.is_in_db():
        print(f'Sending notification for tournament {tournament.id}')
        gmail.notify_html_tournament(tournament)
        tournament.save_to_db()
print('end session')


        
    
