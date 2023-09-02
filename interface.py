from badnet.sql_connection import badminton_db

from pywebio.input import *
from pywebio.output import *

data = input_group(
    "Enter username and password",
    [
        input("Login", name="login", type=TEXT),
        input("Password", name="password", type=PASSWORD)
    ],
)

departements = badminton_db.execute(f"SELECT departements FROM users WHERE email='{data['login']}'").fetchone()

if departements!='':
    put_text(f"Login successful for {data['login']}")

departs = input_group(
checkbox("Departements", options=["75", "77", "78", "92", "93", "94", "95"], selected=True) 
)
put_text(departs["Departements"])