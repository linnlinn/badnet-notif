notification_email = f'''
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