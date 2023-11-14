import smtplib
import time
from email.mime.text import MIMEText
from sqlalchemy import text


class Errormailer:
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

    def send_error_notification(self, error):
        subject = f"Error de script Badnet: {error}"

        body = f'''
<p>&nbsp;</p>
<p>Hello,</p>
<p>&nbsp;</p>
<div>Le script Badnet a rencontré une erreur :</div>
<p>{error}</p>
<p>{time.ctime()}</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p><br /><br /></p>
<div>Cheers!</div>
        '''

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = "annonces.tournois.bad@gmail.com"
        msg['To'] = ''

        self.send_mail(destinataires='arthur.bossuet@gmail.com', message = msg.as_string())
