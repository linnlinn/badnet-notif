#streamlit interface
import streamlit as st

import streamlit_authenticator as stauth

from badnet.sql_connection import SqlConnector
from sqlalchemy import create_engine, MetaData,Table, Column, Text, Integer, update, insert, select, func

from itertools import compress
import pandas as pd

from random import randint

page_title = "Annonces tournois badminton"
page_icon = ":incoming_envelope:"
layout = "centered"

env = 'dev'

if env=='prod':
    badminton_db = SqlConnector(db="badminton").get_engine()
else:
    badminton_db = SqlConnector(db="badminton_dev").get_engine()

meta = MetaData(bind=badminton_db)
MetaData.reflect(meta)

users = Table(
'users', meta,
Column('id', Integer, primary_key=True, autoincrement=True),
Column('nom', Text),
Column('prenom', Text),
Column('email', Text),
Column('departements', Text),
Column('classements', Text),
Column('disciplines', Text),
extend_existing=True
)



st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# with st.expander("registration form"):
#     with st.form(key='my-form', clear_on_submit=True):
#         name = st.text_input('Enter your name')
#         submit = st.form_submit_button('Submit')

#     st.write('Press submit to have your name printed below')

#     if submit:
#         st.write(f'hello {name}')


class Auto(stauth.Authenticate):
    def __init__(self, credentials: dict, cookie_name: str, key: str, cookie_expiry_days: int=30, 
        preauthorized: list=None):
        super().__init__(credentials, cookie_name, key, cookie_expiry_days, preauthorized)

    def register_user(self, form_name: str, location: str='main', preauthorization=True) -> bool:
        """
        Creates a password reset widget.
        Parameters
        ----------
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        preauthorization: bool
            The preauthorization requirement, True: user must be preauthorized to register, 
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if preauthorization:
            if not self.preauthorized:
                raise ValueError("preauthorization argument must not be None")
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            register_user_form = st.form('Register user', clear_on_submit=True)
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')
        with register_user_form:
            st.subheader(form_name)
            new_email = st.text_input('Email')
            new_username = st.text_input('Login').lower()
            new_name = st.text_input('Nom et prénom')
            new_password = st.text_input('Password', type='password')
            new_password_repeat = st.text_input('Repeat password', type='password')
            print('form created')
            submitted = st.form_submit_button('Enregistrer')
        if submitted:
            print(f'username : {new_username}')
            
            if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                if new_username not in self.credentials['usernames']:
                    if new_password == new_password_repeat:
                        if preauthorization:
                            if new_email in self.preauthorized['emails']:
                                self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                                return True
                        else:
                            self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
                            st.success(f'Utilisateur  {new_username}  est enregistré')
                            max_id = badminton_db.execute(select(func.max(users.c.id))).fetchone()[0]
                            stmt = insert(users).values(id=max_id+1 ,nom=new_name, prenom=new_username, email=new_email, departements='75,77,78,91,92,93,94,95',classements='N,R,P,D,NC', disciplines='simple,double,mixte')
                            badminton_db.execute(stmt)

                            return True

        # register_user_form.subheader(form_name)
        # new_email = register_user_form.text_input('Email')
        # new_username = register_user_form.text_input('Username').lower()
        # new_name = register_user_form.text_input('Name')
        # new_password = register_user_form.text_input('Password', type='password')
        # new_password_repeat = register_user_form.text_input('Repeat password', type='password')

        # submitted = register_user_form.form_submit_button('Register new user')
        # if submitted:
        #     print(f'username : {new_username}')
        # if submitted:
        #     print("buttor register clicked")
        #     st.success('buttor register clicked')
        #     if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
        #         if new_username not in self.credentials['usernames']:
        #             if new_password == new_password_repeat:
        #                 if preauthorization:
        #                     if new_email in self.preauthorized['emails']:
        #                         self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
        #                         return True
        #                 else:
        #                     self._register_credentials(new_username, new_name, new_password, new_email, preauthorization)
        #                     return True
    


import yaml
from yaml.loader import SafeLoader
with open('./logins.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

#authenticator = stauth.Authenticate(
authenticator = Auto(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

departements = ["75", "77", "78", "91", "92", "93", "94", "95"]

name, authentication_status, username = authenticator.login('Login', 'sidebar')


if not authentication_status:
    with st.expander("New user registration form"):
        try:
            print('user being registered')
            #authenticator._register_credentials('username', 'name', 'password', 'email', False)
            #st.success(f'{authenticator.credentials["usernames"].keys()}')
            if authenticator.register_user('Enregister un nouvel utilisateur', 'main', preauthorization=False):
                print('User registered successfully')
                with open('./logins.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                    print('yaml dumped')
            
        except Exception as e:
            print('User registered unsuccessfully')
            st.error(e)

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    st.write(f"{authenticator.credentials['usernames'][username]['email']}")
    st.title('Your subscriptions:')
    email = authenticator.credentials['usernames'][username]['email']
    id, nom, prenom = badminton_db.execute(f"SELECT id, nom, prenom FROM users WHERE email='{email}'").fetchone()

    depratements = badminton_db.execute(f"SELECT departements FROM users WHERE email='{email}'").fetchone()
    depratements = list(depratements)[0].split(",")
    disciplines = badminton_db.execute(f"SELECT disciplines FROM users WHERE email='{email}'").fetchone()
    disciplines = list(disciplines)[0].split(",")
    classements = badminton_db.execute(f"SELECT classements FROM users WHERE email='{email}'").fetchone()
    classements = list(classements)[0].split(",")
    st.write(f'Departements : {", ".join(depratements)}')
    st.write(f'Disciplines : {", ".join(disciplines)}')
    st.write(f'Classements : {", ".join(classements)}')

    with st.form("departements", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        col1.write("Choisissez vos departements: ")
        option_75 = col1.checkbox(label = "75", value=('75' in departements))
        option_77 = col1.checkbox(label = "77", value=('77' in departements))
        option_78 = col1.checkbox(label = "78", value=('78' in departements))
        option_91 = col1.checkbox(label = "91", value=('91' in departements))
        option_92 = col1.checkbox(label = "92", value=('92' in departements))
        option_93 = col1.checkbox(label = "93", value=('93' in departements))
        option_94 = col1.checkbox(label = "94", value=('94' in departements))
        option_95 = col1.checkbox(label = "95", value=('95' in departements))

        col2.write("Choisissez vos disciplines: ")
        option_simple = col2.checkbox(label = "simple", value=('simple' in disciplines))
        option_double = col2.checkbox(label = "double", value=('double' in disciplines))
        option_mixte = col2.checkbox(label = "mixte", value=('mixte' in disciplines))    

        col3.write("Choisissez vos classements: ")
        option_nc = col3.checkbox(label = "NC", value=('NC' in classements))
        option_p = col3.checkbox(label = "P", value=('P' in classements))
        option_d = col3.checkbox(label = "D", value=('D' in classements))
        option_r = col3.checkbox(label = "R", value=('R' in classements))  
        option_n = col3.checkbox(label = "N", value=('N' in classements))  
        choice_submitted = st.form_submit_button()
        if choice_submitted:
            st.success('Vos choix sont enrégistrés')
            st.write(f"{', '.join(compress(['simple','double','mixte'],[option_simple,option_double,option_mixte]))}")
            st.write(f"{', '.join(compress(['N','R','D','P','NC'],[option_n,option_r,option_d,option_p,option_nc]))}")
            st.write(f"{', '.join(compress(['75','77','78','91','92','93','94','95'],[option_75,option_77,option_78,option_91,option_92,option_93,option_94,option_95]))}")
            new_departements = ','.join(compress(['75','77','78','91','92','93','94','95'],[option_75,option_77,option_78,option_91,option_92,option_93,option_94,option_95]))
            new_classements = ','.join(compress(['N','R','D','P','NC'],[option_n,option_r,option_d,option_p,option_nc]))
            new_disciplines = ','.join(compress(['simple','double','mixte'],[option_simple,option_double,option_mixte]))
            
            user = pd.DataFrame(
                {'id':id,
                'nom': nom,
                'prenom':prenom,
                'email': email, 
                'departements': new_departements,
                'classements': new_classements,
                'disciplines': new_disciplines
                }, index=[0]
                )
        
            #user.to_sql('users', badminton_db, if_exists='append', index=False)
            
            #setattr(user, 'departements', new_departements)
            u = update(users)
            u = u.values({'departements':new_departements, 'classements':new_classements, 'disciplines': new_disciplines})
            u = u.where(users.c.email == email)
            badminton_db.execute(u)

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
