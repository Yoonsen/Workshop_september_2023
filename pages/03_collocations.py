

import streamlit as st
import dhlab as dh
import dhlab.text as dt
import pandas as pd
from PIL import Image
import urllib
# for excelnedlastning
from io import BytesIO
import re

st.session_state.update(st.session_state)


from dhlab.api.dhlab_api import urn_collocation


def colloc(corp, words=['working'], before=5, after = 5, reference=None, alpha = False, samplesize= 5000):
    
    coll = pd.concat(
            [
                urn_collocation(
                    urns=list(corp.urn.values),
                    word=w,
                    before=before,
                    after=after,
                    samplesize=samplesize,
                )
                for w in words
            ]
        )[["counts"]]

    if alpha == True:
        coll = coll.loc[[x for x in coll.index if x.isalpha()]]
        if reference is not None:
            reference = reference.loc[[x for x in reference.index if x.isalpha()]]

    collocation = coll.groupby(coll.index).sum()
    if reference is not None:
        if type(reference) == pd.core.frame.DataFrame:
            """assume it has columns freq"""
            reference = reference.freq
        teller = collocation['counts'] / collocation['counts'].sum()
        divided = reference / reference.sum()
        collocation["relevance"] = (teller / divided).drop_duplicates()
    return collocation

@st.cache_data()
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=True, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    writer.close()
    processed_data = output.getvalue()
    return processed_data



@st.cache_data()
def koll(corpus = None, words = None, before = 5, after = 5, reference = None): 
    coll = colloc(corpus, words, before = before, after = after, reference = reference)
    return coll.sort_values(by="relevance", ascending = False)


@st.cache_data()
def reference_corpus():
    return dh.totals(500000)

st.title('Kollokasjoner')
st.markdown("Bygg kollokasjoner for en eller flere ord - her er ordene tolket som de skrives, det gjøres forskjell på stor og liten bokstav")

reference = reference_corpus()
col1, col2, colfilnavn = st.columns([3,1,1])


#with col2:
#    samplesize = int(st.number_input("Maks antall konkordanser:", min_value=5, value=100, help="Minste verdi er 5, default er 100"))

with colfilnavn:
    filnavn = st.text_input("Kollokasjoner ", f"koll_{pd.Timestamp.today()}.xlsx")
 

## ----------------- Code -------------#

## Process file
colw, colbefore, colafter, colcounts = st.columns([3,1,1,1])
with colw:
    words = st.text_input('Søkeuttrykk', st.session_state.get('coll_search', ''), key='coll_search', help="Søk etter hele ord skilt med mellomrom - kapitaliseringssensitiv ")
with colbefore:
    before = st.number_input('Before', 5)
with colafter:
    after = st.number_input("After", 5)
with colcounts:
    countlim = st.number_input("Minste antall forekomster", 3)
if words != "":
    st.write(f"Kollokasjoner for {st.session_state.corpus_name}")
    words = words.split()
    kollok = koll(st.session_state.korpus, words, before = before, after=after, reference = reference.freq  )
    #st.dataframe(konks)
    
    st.dataframe(kollok[kollok['counts'] >= countlim])
                         
    if st.download_button(f'Laste ned 500 topp til {filnavn}', to_excel(kollok.head(500).reset_index()), filnavn, help = "Åpnes i Excel eller tilsvarende"):
        pass            
                