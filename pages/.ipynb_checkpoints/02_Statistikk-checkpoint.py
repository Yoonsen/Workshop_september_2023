# -*- coding: utf-8 -*-
import streamlit as st
import dhlab.text as dh
import pandas as pd
from PIL import Image
import urllib
import os
import re
import matplotlib.pyplot as plt
import altair as alt

@st.cache_data()
def counting(corpus, search_expr):
    return dh.Counts(corpus, search_expr).frame

st.session_state.update(st.session_state)

count_conc = st.session_state['counts']
corpus = st.session_state['korpus']
corpus = corpus.drop_duplicates(subset="dhlabid", keep="first").copy()
corpus["dhlabid"] = corpus["dhlabid"].astype(str)

st.title('Oversikt')

col1, col2, col3, _ = st.columns([2, 2, 3, 5])

if "rolling" not in st.session_state:
    st.session_state.rolling = 5

if "type" not in st.session_state:
    st.session_state.type = "søylediagram"

if "bins" not in st.session_state:
    st.session_state.bins = 10

if "freq_words" not in st.session_state:
    st.session_state.freq_words = ''
    
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

#st.write(search_expr)
if search_expr == ['']:
    st.write('Legg inn noen ord adskilt med komma')
else:
    counts = counting(corpus, search_expr)

    ct = counts.T.copy()
    ct.index = ct.index.astype(str)
    ct = ct[~ct.index.duplicated(keep="first")]   
    
    meta = corpus[["dhlabid","title","authors","year"]]
    ct_reset = ct.reset_index().rename(columns={"index":"dhlabid"})
    #a = meta.merge(ct_reset, on="dhlabid", how="left")
    
    a = pd.concat([corpus.set_index('dhlabid')["title authors year".split()], ct], axis = 1).reset_index()

    if vis == 'dataramme':
        a['bins'] = pd.cut(a.year, num, precision=0)
        groups = a.groupby('bins', observed = True).sum()[ct.columns]
        st.write(groups)

    elif vis == 'søylediagram':
        a['bins'] = pd.cut(a.year, num, precision=0)
        groups = a.groupby('bins', observed = True).sum().reset_index()
        columns_to_select = ['bins'] + [col for col in ct.columns if col in groups.columns]
        groups = groups[columns_to_select]

        # Now you can safely access 'bins' column
        #groups['bins'] = groups['bins'].astype(str).map(lambda x: '-'.join(x[1:-1].split(',')))
        groups['bins'] = groups['bins'].astype(str).map(
            lambda x: '-'.join([str(int(float(edge))) for edge in x[1:-1].split(',')])
        )
        #groups['bins'] = groups['bins'].astype(str).map(lambda x: '-'.join(x[1:-1].split(',')))

        #groups.index = groups.index.astype(str).map(lambda x: '-'.join(x[1:-1].split(',')))
        #st.bar_chart(groups)

        # Creating a bar chart using Matplotlib
        #fig, ax = plt.subplots()
        #groups.plot(kind='bar', stacked=True, ax=ax)

        # Rotating x-axis labels
        #plt.xticks(rotation='horizontal')

        # Displaying the chart in Streamlit
        #st.pyplot(fig)

        melted = groups.melt('bins', var_name='category', value_name='value')

        # Create a stacked bar chart
        chart = alt.Chart(melted).mark_bar().encode(
            x=alt.X('bins:O', axis=alt.Axis(labelAngle=-20)),  # O for ordinal
            y='value:Q',  # Q for quantitative
            color='category:N',  # N for nominal
            order=alt.Order('category', sort='ascending')  # Sort the stack order
        ).properties(
            width=600,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)

    elif vis == 'linjediagram':
        lines = a
        #lines.year = lines.year.apply(lambda x:int(x))
        lines = lines.set_index('year')[ct.columns]
        #st.write(lines)
        st.line_chart(lines) #.rolling(st.session_state.get('rolling',1)).mean())
        #lines

    else:
        pass

