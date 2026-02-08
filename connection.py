import os
import streamlit as st
import mysql.connector



def get_connection():
    # Accedemos a la sección específica del TOML
    credentials = st.secrets["connections"]["mysql"]
    
    return mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"], # Nota: en tu TOML es "username", no "user"
        password=credentials["password"],
        database=credentials["database"], # Nota: en tu TOML es "database", no "SuperBowlParty"
        port=int(credentials["port"])
    )
