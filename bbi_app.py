import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import re
import numpy as np

st.session_state.update(st.session_state)
st.set_page_config(page_title="Mangfold i barnebokslitteraturen", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title("Mangfold og barnebøker")
st.write('---')

@st.cache_data()
def korpus():
    kudos = pd.read_csv("kudos.csv").fillna('').drop_duplicates().fillna('').set_index('dhlabid').reset_index()
    barn = pd.read_csv("barn.csv").fillna('').drop_duplicates().fillna('').set_index('dhlabid').reset_index()
    barn.year = barn.year.replace('', np.nan)
    kudos.year = kudos.year.replace('', np.nan)

    #pd.to_numeric(barn.year)
    #pd.to_numeric(kudos.year)

    kudos.year = kudos.year.dropna().astype(int)
    barn.year = barn.year.dropna().astype(int)
    
    return kudos.dropna(), barn.dropna()

kudos, barn = korpus()


splits = [1945, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2030]
groups = [splits[a:a+2] for a in range(len(splits)-1)]
make_splits = lambda df: {f"{str(x[0])}-{str(x[1])}": df.loc[barn.year >= x[0]].loc[df.year < x[1]] for x in groups}
    
barn_år = make_splits(barn)
kudos_år = make_splits(kudos)

corpus_col, title_col, year_col, _ = st.columns([2,3,4,5])
if "corpus_name" not in st.session_state:
    st.session_state.corpus_name = 'barn'

choices = ['kudos', 'barn']
with corpus_col:
    corpus_name = st.selectbox("Velg korpus", choices, index=choices.index(st.session_state.corpus_name), key='corpus_name')
    if corpus_name == 'kudos':
        korpus = kudos_år
    elif corpus_name == 'barn':
        korpus = barn_år

with title_col:
    
    corpus_title = st.text_input("Ord i tittel:",'', help="La stå blank for ikke å begrense")
    #if corpus_title != '' and corpus_title != ' ':
    #    korpus = korpus[]
if 'periods' not in st.session_state:
    st.session_state.periods = list(korpus.keys())[:2]

#st.write(st.session_state.periods, korpus.keys())
with year_col:
    period = st.multiselect("Velg periode:", korpus.keys(), default = st.session_state.periods, key='periods')

if st.session_state.periods != []:
    if corpus_title != '' and corpus_title != ' ':
        st.session_state['korpus'] = pd.concat([
            korpus[k][korpus[k].title.str.contains(corpus_title)] 
            for k in period])["urn authors title year city publisher langs subjects".split() ]
    else:
        st.session_state['korpus'] = pd.concat([korpus[k] for k in period])["dhlabid urn authors title year city publisher langs subjects".split() ]
else:
    st.session_state['korpus'] = pd.concat([korpus[k] for k in korpus])["dhlabid urn authors title year city publisher langs subjects".split() ]
    
kdict = {k:len(korpus[k]) for k in korpus.keys() }

#st.write(f'korpuset inneholder {kdict}')
st.write(f"## Et lite utvalg fra korpuset bygd over {' '.join(period)} med {len(st.session_state['korpus'])} dokumenter")

st.dataframe(st.session_state['korpus'].sample(min(100, len(st.session_state['korpus']))))