import streamlit as st
from multiapp import MultiApp
from apps import home, autoML, EDA, twitter

app = MultiApp()
st.image('expicon.png',width=30%)

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Twitter Analysis App", twitter.app)
app.add_app("Exploratory Data Analysis App", EDA.app)
app.add_app("Machine Learning Models Comparison App", autoML.app)

# The main app
app.run()
