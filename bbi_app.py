import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import re
import numpy as np

st.set_page_config(page_title="Mangfold i barnebokslitteraturen", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title("Mangfold og barnebøker")
st.write('---')

@st.cache_data()
def korpus():
    kudos = pd.read_csv("kudos.csv").fillna('').drop_duplicates().fillna('').set_index('dhlabid')
    barn = pd.read_csv("barn.csv").fillna('').drop_duplicates().fillna('').set_index('dhlabid')
    barn.year = barn.year.replace('', np.nan)
    kudos.year = kudos.year.replace('', np.nan)
    #kudos.year = kudos.year.astype(int)
    #barn.year = barn.year.astype(int)
    
    return kudos.dropna(), barn.dropna()

kudos, barn = korpus()


corpus_name = st.selectbox("Velg korpus", ['kudos', 'barn'])
if corpus_name == 'kudos':
    st.session_state['korpus'] = kudos
elif corpus_name == 'barn':
    st.session_state['korpus'] = barn

st.write(f'korpuset inneholder {len(st.session_state["korpus"])} dokumenter')
st.write("## Et lite utvalg fra korpuset")
st.dataframe(st.session_state['korpus'].sample(100))