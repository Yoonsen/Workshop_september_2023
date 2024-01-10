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
#st.write(len(kudos), len(barn))
splits = [1945, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2030]
groups = [splits[a:a+2] for a in range(len(splits)-1)]
make_splits = lambda df: {f"{str(x[0])}-{str(x[1])}": df.loc[df.year >= x[0]].loc[df.year < x[1]] for x in groups}
    
barn_år = make_splits(barn)
kudos_år = make_splits(kudos)

corpus_col, year_col, _ = st.columns([2,5,3])
#if "corpus_name" not in st.session_state:
#    st.session_state.corpus_name = 'barn'

choices = ['kudos', 'barn']
with corpus_col:
    corpus_name = st.selectbox("Velg korpus", choices, index=choices.index(st.session_state.get('corpus_name','barn')), key='corpus_name')
    if corpus_name == 'kudos':
        korpus = kudos_år
    elif corpus_name == 'barn':
        korpus = barn_år

if "counts" not in st.session_state:
    st.session_state["counts"] = 0

if 'periods' not in st.session_state:
    st.session_state.periods = list(korpus.keys())[-2:]
    
with year_col:
    period = st.multiselect("Velg periode:", korpus.keys(), default = st.session_state.periods, key='periods')


title_col, author_col, publisher_col, subject_col, literary_col, null_col = st.columns([2,2,2,2,2,1])

for key in ["title_str", "author_str", "subject_str", "literary_str", "publisher_str"]:
    if key not in st.session_state:
        st.session_state[key] = ''

with null_col:
    st.markdown("<br>", unsafe_allow_html=True) 
    if st.button('Nullstill', help="Klikk for å slette søketermene"):
        for k in ["title_str", "author_str", "subject_str", "literary_str", "publisher_str"]:
            st.session_state[k] =  ''
  
with title_col:
    corpus_title = st.text_input("Ord i tittel:",st.session_state.title_str, help="Skriv inn del av tittel", key='title_str')

with author_col:
    corpus_author = st.text_input("Forfatter:",st.session_state.author_str, help="Angi forfatter, eller del av forfatternavn", key='author_str')

with subject_col:
    corpus_subject = st.text_input("Subject:",st.session_state.subject_str, help="angi del av temaord", key='subject_str')

with literary_col:
    corpus_literary = st.text_input("Type dokument:",st.session_state.literary_str, help="Litterær form/sjanger eller dokument-type", key='literary_str')

with publisher_col:
    corpus_literary = st.text_input("Forlag (publisher-kolonne):",st.session_state.literary_str, help="Legg inn forlag eller departement", key='publisher_str')



cols = "dhlabid authors title year subjects literaryform city publisher langs urn".split()

if st.session_state.periods != []:
    st.session_state['korpus'] = pd.concat([korpus[k] for k in period])[cols]
else:
    st.session_state['korpus'] = pd.concat([korpus[k] for k in korpus])[cols]

#st.write(st.session_state.corpus_name, len(st.session_state.korpus), st.session_state.periods)
         
str_map = {
    'literary_str':'literaryform',
    'subject_str': 'subjects',
    'author_str': 'authors',
    'title_str':'title',
    'publisher_str':'publisher'
}

if st.session_state.periods != []:                                    
    for reduction in ['literary_str','subject_str', 'author_str', 'title_str', 'publisher_str']:
        if st.session_state[reduction].strip() != '':
            st.write(reduction,'sub')
            df2 = pd.concat([
                korpus[k][korpus[k][str_map[reduction]].str.contains(st.session_state[reduction], flags=re.IGNORECASE, regex=True)] 
                for k in period])[cols]
            st.session_state['korpus'] = st.session_state['korpus'].merge(df2, how = 'inner')
else:
    for reduction in ['literary_str','subject_str', 'author_str', 'title_str', 'publisher_str']:
        if st.session_state[reduction].strip() != '':
            st.write(reduction,'all')
            df2 = pd.concat([
                korpus[k][korpus[k][str_map[reduction]].str.contains(st.session_state[reduction], flags=re.IGNORECASE, regex=True)] 
                for k in korpus])[cols]
            st.session_state['korpus'] = st.session_state['korpus'].merge(df2, how = 'inner')

    
kdict = {k:len(korpus[k]) for k in korpus.keys() }

#st.write(f'korpuset inneholder {kdict}')
st.write(f"##  Utvalg på oppunder 100 rader fra korpuset med {' '.join(period)} med {len(st.session_state['korpus'])} dokumenter")

st.dataframe(st.session_state['korpus'].sample(min(100, len(st.session_state['korpus'])))[["authors","publisher","title","year","literaryform","subjects"]].style.format(thousands=''), hide_index=True)
