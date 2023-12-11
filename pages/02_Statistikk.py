# -*- coding: utf-8 -*-
import streamlit as st
import dhlab.text as dh
import pandas as pd
from PIL import Image
import urllib
import os
import re
import matplotlib.pyplot as plt

st.session_state.update(st.session_state)
max_conc = 20000


if not 'bins' in st.session_state:
    st.session_state['bins'] = 10

st.session_state.update(st.session_state)

corpus = st.session_state['korpus']

counts = st.session_state['counts']

st.title('Oversikt')
col1, col2, _ = st.columns([2, 2, 5])
with col1:
    if st.session_state.get('type', 'linjediagram') == 'linjediagram':
        num = st.number_input("Angi glatting", min_value = 1, max_value= 20, value =1, key="rolling", disabled = True)
    else:
        num = st.number_input("Angi antall grupper", min_value = 3, max_value= 20, value =10, key="bins")
with col2:
    vis = st.selectbox("Vis som", [ 'linjediagram', 'søylediagram'], key='type')




st.write(corpus.sample(2))
st.write(counts.sample(2))
a = pd.concat([corpus.set_index('dhlabid'), counts], axis = 1).reset_index()[['urn','year', 'freq']].dropna()
#a = a[a.year>0]

st.write(f"Antallet avsnitt som gir treff på __{st.session_state['konk']}__.")
st.dataframe(counts.sample(100, replace=True))

if vis == 'dataramme':
    st.write(groups)

elif vis == 'søylediagram':
    #st.write(a.year)
    a['bins'] = pd.cut(a.year, num, precision=0)
    st.dataframe(a)
    groups = a.groupby('bins').sum()[['freq']]
    st.dataframe(groups)
    groups.index = groups.index.astype(str).map(lambda x: '-'.join(x[1:-1].split(',')))
    st.bar_chart(groups)

elif vis == 'linjediagram':
    lines = a[['year','freq']]
    #lines.year = lines.year.apply(lambda x:int(x))
    lines = lines.set_index('year')
    #lines.index = pd.to_datetime(lines.index.astype(int))
    st.line_chart(lines) #.rolling(st.session_state.get('rolling',1)).mean())
    #lines

else:
    pass

