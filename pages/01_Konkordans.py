import streamlit as st
#import dhlab.text as dh
import dhlab_api as api
import dhlab as dh
import pandas as pd
from PIL import Image
import urllib
import requests

def concordance(
        urns = None, words = None, window = 25, limit = 100
):
    """Get a list of concordances from the National Library's database.

    Call the API :py:obj:`~dhlab.constants.BASE_URL` endpoint
    `/conc <https://api.nb.no/dhlab/#/default/post_conc>`_.

    :param list urns: uniform resource names, for example:
        ``["URN:NBN:no-nb_digibok_2008051404065", "URN:NBN:no-nb_digibok_2010092120011"]``
    :param str words: Word(s) to search for.
        Can be an SQLite fulltext query, an fts5 string search expression.
    :param int window: number of tokens on either side to show in the collocations, between 1-25.
    :param int limit: max. number of concordances per document. Maximum value is 1000.
    :return: a table of concordances
    """
    if words is None:
        return {}  # exit condition
    else:
        params = {"dhlabids": urns, "query": words, "window": window, "limit": limit}
        r = requests.post(dh.constants.BASE_URL + "/conc", json=params)
        if r.status_code == 200:
            res = r.json()
        else:
            res = []
    return pd.DataFrame(res)

st.session_state.update(st.session_state)
max_conc = 20000

@st.cache_data( show_spinner = False)
def konk(corpus = None, query = None): 
    #st.write(list(corpus.index)[:20])
    concord = concordance(list(corpus.dhlabid), query, limit = max_conc)
    #concord = dh.Concordance(corpus, query, limit = max_conc)
    return concord #[['urn','conc']]


def set_markdown_link_conc(conc, corpus, query):
    try:
        corps = corpus.set_index('urn')
        st.dataframe(conc.sample(5))
        conc['link'] = conc['urn'].apply(lambda c: "[{display}](https://www.nb.no/items/{x}?searchText={q})".format(x = c, display = f"{corps.loc[c].title} - {corps.loc[c].authors} : {corps.loc[c].year}" , q = urllib.parse.quote(query)))
    except:
        conc['link'] = ""
        
    return conc[[
         'link', 'concordance'
    ]].sort_values(by='link')

def set_html_link_conc(conc, corpus, query):
    try:
        corps = corpus.set_index('urn')
        conc['link'] = conc['urn'].apply(lambda c: "<a href='https://www.nb.no/items/{x}?searchText={q}'>{display}</a>".format(x = c, display = f"{corps.loc[c].title} - {corps.loc[c].authors} : {corps.loc[c].year}" , q = urllib.parse.quote(query)))
    except:
        st.write('noe')
        conc['link'] = ""
        
    return conc[[
         'link', 'conc'
    ]].sort_values(by='link')
corpus = st.session_state['korpus']



st.title(f'Søk etter uttrykk i korpuset "{st.session_state.corpus_name}"')


if not 'konk' in st.session_state:
    st.session_state['konk'] = 'mangfold'

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

#konk = set_markdown_link_conc(
#concord_dh(
#    style=False, 
#    n=int(samplesize)
#), 
#corpus, 
#words
#)


st.markdown(f"## Konkordanser for __{words}__")

if samplesize < len(concord_dh):
    konkordans = set_html_link_conc(concord_dh.sample(samplesize), corpus, words)
    if st.button(f"Klikk her for flere konkordanser. Sampler {samplesize} av {concord_dh.size}"):
        #st.write('click')
        konkordans = set_html_link_conc(concord_dh.sample(samplesize), corpus, words)
        #st.markdown(konkordans.to_html(escape=False), unsafe_allow_html=True)
    
else:
    if concord_dh.size == 0:
        st.write(f"Ingen treff")
        konkordans = pd.DataFrame()
    else:
        st.write(f"Viser alle {concord_dh.size} konkordansene ")
        konkordans = set_html_link_conc(concord_dh, corpus, words)
st.markdown(konkordans.to_html(escape=False), unsafe_allow_html=True)




