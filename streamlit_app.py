#%% Imports

import pandas as pd
import time
import random

import streamlit as st
import tableauserverclient as TSC
import streamlit.components.v1 as components
# from .src.mpi import MessagePassing, mpi_get_data, mpi_select_status, mpi_run_fig, mpi_select_fig
from streamlit_plotly_events import plotly_events
import plotly.express as px
import plotly.graph_objects as go

#%%

import sys
print(sys.path)
import os
print(os.path.dirname(os.path.abspath(__file__)))
st.write(os.path.dirname(os.path.abspath(__file__)))
st.write(sys.path)


#%% Page Config
st.set_page_config(
    page_title="Ties That Bind",
    page_icon="🌐",
    layout="wide"
)

#%% Main title and Intro
st.markdown("<h1 style='text-align: center;'>Ties That Bind: A Visual Exploration of Human Connection</h1>", unsafe_allow_html=True)

st.markdown("""
This project explores how people connect with each other in everyday life. It uses data visualizations to show how we communicate, build relationships, and form economic and social communities. The project looks at different ways to interpret Social Connectedness and its impact on global dynamics.  The goal is to make the idea of the power of  human connection clear and relatable for everyone.
""")

st.markdown("### What is SCI data?")
st.markdown("""
Social Connectedness Index (SCI) is a measure of the social connectedness between different geographies. It measures the relative probability of two different individuals each from a specified geography communicating with each other. The data we propose to use is from Facebook Social Connectedness Index [1]. The data consists of a snapshot of all active Facebook users and their friendship networks, and is defined as follows.
""")

# Display SCI formula image centered
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("SCI.png", width=400)

st.markdown("### What SCI can show us?")
st.markdown("""
**Significance of SCI**

SCI may show us how connected people are geographically, however SCI data has broader implications spanning across multiple disciplines. SCI data has been shown to correlate to economic factors and disease outbreaks. Other definitions of SCI implicate relationships to political events, policies, immigration etc. Perhaps by exploring compound relationships to other data can provide valuable insight that may not be obvious with a singular dataset alone.
""")

st.markdown("---")


#%% Tableau Connection


# Set up connection to Tableau
tableau_auth = TSC.PersonalAccessTokenAuth(
    st.secrets["tableau"]["token_name"],
    st.secrets["tableau"]["personal_access_token"],
    st.secrets["tableau"]["site_id"],
)
server = TSC.Server(st.secrets["tableau"]["server_url"], use_server_version=True)

# Specific workbook ID from the URL
TARGET_WORKBOOK_ID = "2526031"
TARGET_VIEW_NAME = "Dashboard 1"

# Get various data from Tableau
@st.cache_data(ttl=600)
def get_dashboard():
    with server.auth.sign_in(tableau_auth):
        workbooks, pagination_item = server.workbooks.get()
        
        target_workbook = None
        for workbook in workbooks:
            if workbook.id == TARGET_WORKBOOK_ID or workbook.name == "SCI":
                target_workbook = workbook
                break
                
        if target_workbook:
            server.workbooks.populate_views(target_workbook)
            
            dashboard_view = None
            for view in target_workbook.views:
                if view.name == TARGET_VIEW_NAME:
                    dashboard_view = view
                    break
            
            if dashboard_view:
                server.views.populate_image(dashboard_view)
                return dashboard_view.image
            
            elif target_workbook.views:
                view_item = target_workbook.views[0]
                server.views.populate_image(view_item)
                return view_item.image
                
        return None

try:
    dashboard_image = get_dashboard()
    
    if dashboard_image:
        st.image(dashboard_image)
    else:
        st.error("Dashboard not found")
        
except Exception as e:
    st.error(f"Error: {str(e)}")

st.subheader("COVID Data")
covid_tableau_html = """
<div class='tableauPlaceholder' id='viz1743210082495' style='position: relative'><noscript><a href='#'><img alt='Daily cases&#47; Month ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6H&#47;6HTWTQ2C9&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='path' value='shared&#47;6HTWTQ2C9' /> <param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6H&#47;6HTWTQ2C9&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>
<script type='text/javascript'>
    var divElement = document.getElementById('viz1743210082495');
    var vizElement = divElement.getElementsByTagName('object')[0];
    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';
    var scriptElement = document.createElement('script');
    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
    vizElement.parentNode.insertBefore(scriptElement, vizElement);
</script>
"""
components.html(covid_tableau_html, height=600)

with st.expander("About SCI"):
    st.write("""
    The Social Connectedness Index (SCI) measures the strength of connectedness between 
    geographic areas as represented by social network friendships.
    """)

    



#%% Message Passing
'''
with st.expander("Message Passing Simulator"):
    st.write("Select a country to see how it plays a role in connecting the world.")
    delta_t = 50
    at = 100
    if "mpi_event" not in st.session_state:
        st.session_state.mpi_event = None
    mpi_placeholder = st.empty()

    if  st.session_state.mpi_event is not None and len(st.session_state.mpi_event['selection']['points']) > 0:
        country =st.session_state.mpi_event['selection']['points'][0]['location']
        st.write("Selected country:", country)
        df = mpi_get_data(country, at=100, ts=256, pp=1.)
        fig = mpi_run_fig(df, at, delta_t)
        mpi_placeholder.plotly_chart(fig, use_container_width=True, key="mpi_mode")

    else:
        mpi = MessagePassing()
        fig = mpi_select_fig(mpi.countries_input)
        st.session_state.mpi_event = mpi_placeholder.plotly_chart(fig, use_container_width=True, on_select=mpi_select_status, key="select_mode")
        if  len(st.session_state.mpi_event['selection']['points']) > 0:
            fig.update_traces(selectedpoints=None)
            st.rerun()


    if st.button('Reset'):
        st.session_state.mpi_event = None
        st.rerun()
'''
#%%