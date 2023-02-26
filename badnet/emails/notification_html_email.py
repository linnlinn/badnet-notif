html_email = f'''
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