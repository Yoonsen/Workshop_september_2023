import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import re

st.set_page_config(page_title="Mangfold i barnebokslitteraturen", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title("Mangfold og barnebøker")
st.write('---')

@st.cache_data()
def korpus():
    kudos = pd.read_csv("kudos.csv", index_col = 0).fillna('')
    barn = pd.read_csv("barn.csv", index_col = 0).fillna('')
    kudos.year = kudos.year.astype(str)
    barn.year = barn.year.astype(str)
    
    return kudos, barn

kudos, barn = korpus()


corpus_name = st.selectbox("Velg korpus", ['kudos', 'barn'])
if corpus_name == 'kudos':
    st.session_state['korpus'] = kudos
elif corpus_name == 'barn':
    st.session_state['korpus'] = barn

st.write(f'korpuset inneholder {len(st.session_state["korpus"])} dokumenter')