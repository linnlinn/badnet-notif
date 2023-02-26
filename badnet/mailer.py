import smtplib
from email.mime.text import MIMEText
from badnet.sql_connection import badminton_db

from .tournament import Tournament
#from .emails.notification_email import notification_email
#from .emails.notification_html_email import html_email


class Mailer:
    def __init__(self, user: str, password: str):
        self.SMTP_HOST='smtp.gmail.com'
        self.SMTP_PORT=587
        self.sent_from = user
        self.password = password

    def send_mail(self, destinataires: str, message: str):
        server = smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(self.sent_from, self.password)

        server.sendmail(self.sent_from, destinataires, message)
        server.close()

    def notify_tournament(self, tournament:Tournament):
        tournament.get_additional_info()
        destinataires = self.get_destinataires(tournament)

        subject = f"Nouveau tournoi : {tournament.name}"

        body = f'''
DO NOT REPLY TO THIS EMAIL
==========================

Hello,

Un nouveau tournoi a été ajouté sur Badnet :
    {tournament.name}

Lien : {tournament.url}
Dates : {tournament.date}
Ville : {tournament.ville}
Departement : {tournament.departement}
Ouvert aux classements : {', '.join(tournament.category)}
Disciplines : {', '.join(tournament.disciplines)}

Presentation : 
{tournament.description}

Informations pratiques:

Juge-arbitre : {tournament.ja}
Volant officiel : {tournament.volant}
Ouverture des inscriptions le {tournament.date_registration_opening}


Cheers!

Pour tout problème ou demande modification merci d'envoyer un mail à Arthur (arthur.bossuet@gmail.com)
        '''

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = "annonces.tournois.bad@gmail.com"
        msg['To'] = ''#, '.join(destinataires)

        self.send_mail(destinataires=destinataires, message = msg.as_string())
        

    def get_destinataires(self, tournament: Tournament):
        query = f"""
        SELECT email 
            FROM users 
            WHERE 
                (departements REGEXP '{tournament.departement}')
                AND (classements REGEXP '{"|".join(tournament.category)}')
                AND (disciplines REGEXP '{"|".join(tournament.disciplines)}')

        """
        
        emails = badminton_db.execute(query).fetchall()
        emails = [a[0] for a in emails ]
        return emails

    def send_error_notification(self, error):
        pass

    def notify_html_tournament(self, tournament:Tournament):
        tournament.get_additional_info()
        destinataires = self.get_destinataires(tournament)

        subject = f"Nouveau tournoi : {tournament.name}"

        body = f'''
<h3>DO NOT REPLY TO THIS EMAIL</h3>
<p>==========================</p>
<p>&nbsp;</p>
<p>Hello,</p>
<p>&nbsp;</p>
<div>Un nouveau tournoi a &eacute;t&eacute; ajout&eacute; sur Badnet :</div>
<h2>{tournament.name}</h2>
<p>&nbsp;</p>
        ''' +('' if tournament.url_affiche=='https://badnet.fr/Img/poster/affiche_default.png' else f'<p><img src="{tournament.url_affiche}" /></p><p>&nbsp;</p>') + f'''
<div><strong>Lien :</strong> {tournament.url}</div>
<div><strong>Dates :</strong> {tournament.date}</div>
<div><strong>Ville :</strong> {tournament.ville}</div>
<div><strong>Departement :</strong> {tournament.departement}</div>
<div><strong>Ouvert aux classements :</strong> {', '.join(tournament.category)}</div>
<div><strong>Disciplines :</strong> {', '.join(tournament.disciplines)}</div>
<p>&nbsp;</p>
<h4>Presentation :</h4>
<div>{tournament.description}</div>
<p>&nbsp;</p>
<div>Informations pratiques:</div>
<p>&nbsp;</p>
<div><strong>Juge-arbitre :</strong> {tournament.ja}</div>
<div><strong>Volant officiel :</strong> {tournament.volant}</div>
<div>Ouverture des inscriptions <span style="color: #800000;"><strong>le {tournament.date_registration_opening}</strong></span></div>
<p><br /><br /></p>
<div>Cheers!</div>
<p>&nbsp;</p>
<div>Pour tout probl&egrave;me ou demande modification merci d'envoyer un mail &agrave; Arthur (arthur.bossuet@gmail.com)</div>
        '''

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = "annonces.tournois.bad@gmail.com"
        msg['To'] = ''#, '.join(destinataires)

        self.send_mail(destinataires=destinataires, message = msg.as_string())