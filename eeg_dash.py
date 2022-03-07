import streamlit as st
from multiapp import MultiApp
from apps import doctor_page, patient_page # import your app modules here

app = MultiApp()

# Add all your application here
app.add_app("Physician Page", doctor_page.app)
app.add_app("Patient Page", patient_page.app)

# The main app
app.run()
