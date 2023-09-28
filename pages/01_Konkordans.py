import streamlit as st
import dhlab.text as dh
import pandas as pd
from PIL import Image
import urllib


st.session_state.update(st.session_state)

max_conc = 20000

@st.cache_data( show_spinner = False)
def konk(corpus = None, query = None): 
    concord = dh.Concordance(corpus, query, limit = max_conc)
    return concord


def set_markdown_link_conc(conc, corpus, query):
    try:
        corps = corpus.set_index('urn')
        conc['link'] = conc['urn'].apply(lambda c: "[{display}](https://www.nb.no/items/{x}?searchText={q})".format(x = c, display = f"{corps.loc[c].title} - {corps.loc[c].authors} : {corps.loc[c].year}" , q = urllib.parse.quote(query)))
    except:
        conc['link'] = ""
        
    return conc[[
         'link', 'concordance'
    ]].sort_values(by='link')


corpus = st.session_state['korpus']


st.title(f'Søk etter uttrykk i korpuset')

if not 'konk' in st.session_state:
    st.session_state['konk'] = '"religiøst mangfold"'

words = st.text_input(
    'Søk etter ord og fraser', 
    st.session_state['konk'],
    key='konk',
    help="Bruk anførselstegn for å gruppere fraser. Trunker med * etter ord. Kombiner med OR eller AND. For ord nær hverandre bruk NEAR(ord1 ord2, Antall ord i mellom)")

concord_dh = konk(corpus = corpus, query = words) 

samplesize = int(
    st.number_input(
        "Vis et visst antall konkordanser i gangen:", 
        min_value=5,
        value=100, 
        help="Minste verdi er 5, default er 100"
    )
)

konk = set_markdown_link_conc(
concord_dh.show(
    style=False, 
    n=int(samplesize)
), 
corpus, 
words
)

    
st.markdown(f"## Konkordanser for __{words}__")

if samplesize < concord_dh.size:
    if st.button(f"Klikk her for flere konkordanser. Sampler {samplesize} av {concord_dh.size}"):
        #st.write('click')
        konk = set_markdown_link_conc(concord_dh.show(style=False, n=int(samplesize)), corpus, words)
else:
    if concord_dh.size == 0:
        st.write(f"Ingen treff")
    else:
        st.write(f"Viser alle {concord_dh.size} konkordansene ")

counts = concord_dh.show(n=concord_dh.size, style=False).groupby('urn').count()[['concordance']]
counts.columns = ['freq']

st.session_state['counts'] = counts


st.markdown('\n\n'.join(
    [f"{r[1][0]}  {r[1][1]}" for r in konk.iterrows()]
).replace('<b>','**').replace('</b>', '**'))


