import pandas as pd
import time
import random
import streamlit as st
import tableauserverclient as TSC
import streamlit.components.v1 as components
from src.mpi import MessagePassing, mpi_get_data, mpi_select_status, mpi_run_fig, mpi_select_fig
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from src.sankey_visualization import load_trade_data, display_trade_sankey
from src.trade_scatter import load_trade_sci_data, display_trade_sci_scatter
from src.trade_heatmap import display_trade_sci_heatmap
import pycountry
import traceback
from src.sci_map_explorer import display_sci_map_explorer
from us_mig_sci import render_us_sci_map
from worldmapmigration import render_world_sci_map
st.set_page_config(
    page_title="Ties That Bind",
    page_icon="🌐",
    layout="wide"
)

st.markdown("<h1 style='text-align: center;'>Ties That Bind: A Visual Exploration of Human Connection</h1>", unsafe_allow_html=True)
st.markdown("""
This project explores how people connect with each other in everyday life. It uses data visualizations to show how we communicate, build relationships, and form economic and social communities. The project looks at different ways to interpret Social Connectedness and its impact on global dynamics.  The goal is to make the idea of the power of  human connection clear and relatable for everyone.
""")
st.markdown("### What is SCI data?")
st.markdown("""
Social Connectedness Index (SCI) is a measure of the social connectedness between different geographies. It measures the relative probability of two different individuals each from a specified geography communicating with each other. The data we propose to use is from Facebook Social Connectedness Index [1]. The data consists of a snapshot of all active Facebook users and their friendship networks, and is defined as follows.
""")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("SCI.png", width=400)

st.markdown("### What SCI can show us?")
st.markdown("""
**Significance of SCI**

SCI may show us how connected people are geographically, however SCI data has broader implications spanning across multiple disciplines. SCI data has been shown to correlate to economic factors and disease outbreaks. Other definitions of SCI implicate relationships to political events, policies, immigration etc. Perhaps by exploring compound relationships to other data can provide valuable insight that may not be obvious with a singular dataset alone.
""")
st.markdown("---")

display_sci_map_explorer()


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


st.title("Migration and SCI Visualization")
st.markdown("### What do these visualizations show?")
st.markdown("These visualizations show the relationsip between SCI and migration trends within the US and the world. From these, we can hope to identify ways that SCI and migration positively or negatively correlate.")
st.markdown("### Why is this important?")
st.markdown("We want to explore how SCI and migration are related.")

st.markdown("These are combined visualizations of World/US migration data and social connectedness where we explore the correlation through color representation of low/high sci and migration trends. Do people tend to move places where there are stronger social ties? Where do we see strong social ties but low migration or vice versa and what opportunties for connections, migrations, and more are in such places?")

#bullets

st.markdown("""
    
    **How to read the visualization:**
    *   The color of the countries/states show the correlation between SCI and migration

    *   The color of the countries/states show the correlation between SCI and migration
    *   Refer to legends for color representation
    *   Hover over regions for data information
    
    """)

render_world_sci_map()

st.title("US Migration and SCI Visualization")

st.markdown("This is a combined visualization of United States migration data and social connectedness.")

render_us_sci_map()


st.markdown("### Message Passing Simulator")
st.write("Select a country to see how it plays a role in connecting the world.")
delta_t = 50
at = 100

mpi_col1, mpi_col2, mpi_col3 = st.columns(3)
with mpi_col1:
    pp = st.number_input(label="Passing Probability",value=1.0,min_value=0.0,max_value=1.0,step=0.01,format="%.2f")
with mpi_col2:
    ts = st.number_input(label="Enter Timesteps", value=256, min_value=5,max_value=1000,step=1, )
with mpi_col3:
    at = st.number_input(label="Enter Activation Threshold",value=100,min_value=1,max_value=1000,step=1,)

projection_ops = ['equirectangular',  'orthographic', 'natural earth', 'conic equidistant', 'stereographic']
projection_choice = st.selectbox(
    label="Pick an option",
    options=projection_ops
)

if "mpi_event" not in st.session_state:
    st.session_state.mpi_event = None
mpi_placeholder = st.empty()

if  st.session_state.mpi_event is not None and len(st.session_state.mpi_event['selection']['points']) > 0:
    country =st.session_state.mpi_event['selection']['points'][0]['location']
    st.write("Selected country:", country)
    df = mpi_get_data(country, at=at, ts=ts, pp=pp)
    fig = mpi_run_fig(df, at, delta_t, projection_choice)
    mpi_placeholder.plotly_chart(fig, use_container_width=True, key="mpi_mode")
else:
    mpi = MessagePassing()
    fig = mpi_select_fig(mpi.countries_input, projection_choice)
    st.session_state.mpi_event = mpi_placeholder.plotly_chart(fig, use_container_width=True, on_select=mpi_select_status, key="select_mode")
    if  len(st.session_state.mpi_event['selection']['points']) > 0:
        fig.update_traces(selectedpoints=None)
        st.rerun()

if st.button('Reset'):
    st.session_state.mpi_event = None
    st.rerun()

st.markdown("<h1 style='text-align: center;'>Trade and Social Connectedness Analysis</h1>", unsafe_allow_html=True)

try:
    sv_trade_data, sv_sci_data, sv_country_map = load_trade_data()
except Exception as e:
    st.error(f"Error loading Sankey data: {e}")
    sv_trade_data, sv_sci_data, sv_country_map = pd.DataFrame(), pd.DataFrame(), {}

if not sv_trade_data.empty and not sv_sci_data.empty:
    display_trade_sankey(sv_trade_data, sv_sci_data, sv_country_map)
else:
    st.warning("Could not load data required for the Sankey Diagram.")

try:
    sp_trade_sci_df = load_trade_sci_data()
except Exception as e:
    st.error(f"Error loading combined Trade/SCI data: {e}")
    sp_trade_sci_df = pd.DataFrame()

if not sp_trade_sci_df.empty:
    display_trade_sci_scatter(sp_trade_sci_df)
else:
    st.warning("Could not load data required for the Trade/SCI Scatter Plot.")

if not sp_trade_sci_df.empty:
    display_trade_sci_heatmap(sp_trade_sci_df)
else:
    st.warning("Could not load data required for the Trade/SCI Heatmap.")

# --- SCI World Map Explorer ---


