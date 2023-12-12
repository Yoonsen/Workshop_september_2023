# -*- coding: utf-8 -*-
import streamlit as st
import dhlab.text as dh
import pandas as pd
from PIL import Image
import urllib
import os
import re
import matplotlib.pyplot as plt

@st.cache_data()
def counting(corpus, search_expr):
    return dh.Counts(corpus, search_expr).frame

st.session_state.update(st.session_state)

count_conc = st.session_state['counts']
corpus = st.session_state['korpus']


st.title('Oversikt')

col1, col2, col3, _ = st.columns([2, 2, 3, 5])

if "rolling" not in st.session_state:
    st.session_state.rolling = 5

if "type" not in st.session_state:
    st.session_state.type = "søylediagram"

if "bins" not in st.session_state:
    st.session_state.bins = 10

if "freq_words" not in st.session_state:
    st.session_state.freq_words = 'mangfold, lek, gutter'
    
select_options = [ 'linjediagram', 'søylediagram','dataramme']

with col1:
    if st.session_state.get('type', 'linjediagram') == 'linjediagram':
        num = st.number_input(
            "Angi glatting", 
            min_value = 1, 
            max_value= 20, 
            value = st.session_state.rolling, 
            key="rolling", 
            disabled = True
        )
    else:
        num = st.number_input(
            "Angi antall grupper", 
            min_value = 3, 
            max_value= 20, 
            value = st.session_state.bins, 
            key="bins"
        )

with col2:
    vis = st.selectbox(
        "Vis som", 
        select_options, 
        index = select_options.index(st.session_state.type),                
        key='type'
    )

with col3:
    words = st.text_input(
        "Søk etter frekvens for", 
        value = st.session_state['freq_words'],
        key = "freq_words",
        help = "Skriv en liste med ord som skal sammenlignes adskilt med komma"
    )                   
    search_expr = [w.strip() for w in words.split(',')]

counts = counting(corpus, search_expr)
#st.write(corpus.sample(5))
ct = counts.transpose()
#st.write(ct.sample(5))

a = pd.concat([corpus.set_index('dhlabid')["title authors year".split()], ct], axis = 1).reset_index()

#[['urn','year', 'freq']].dropna()
#a = a[a.year>0]

#st.write(f"Antallet avsnitt som gir treff på __{st.session_state['konk']}__.")
#st.dataframe(counts.sample(100, replace=True))

if vis == 'dataramme':
    a['bins'] = pd.cut(a.year, num, precision=0)
    groups = a.groupby('bins').sum()[ct.columns]
    st.write(groups)

elif vis == 'søylediagram':
    a['bins'] = pd.cut(a.year, num, precision=0)
    groups = a.groupby('bins').sum()[ct.columns]
    groups.index = groups.index.astype(str).map(lambda x: '-'.join(x[1:-1].split(',')))
    st.bar_chart(groups)

elif vis == 'linjediagram':
    lines = a
    #lines.year = lines.year.apply(lambda x:int(x))
    lines = lines.set_index('year')[ct.columns]
    #st.write(lines)
    st.line_chart(lines) #.rolling(st.session_state.get('rolling',1)).mean())
    #lines

else:
    pass

