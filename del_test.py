#%%

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from src.mpi import MessagePassing
import pandas as pd

@st.cache_data
def get_data(country, at = 100,ts = 256,pp = 1.):
    mpi = MessagePassing()
    mpi.get_timestep_activations(country, ts, pp, at)
    
    countries = mpi.countries_input
    time_steps = [i for i in range(ts)]
    values = mpi.activations

    print(np.array(values).shape)
    print(np.array(values).sum())

    records = []
    for i, year in enumerate(time_steps):
        for j, country_code in enumerate(countries):
            row_dict = {
                'country': country_code, 
                'value': values[i][j],
                'timestep': year
            }
            records.append(row_dict)


    return pd.DataFrame(records)

def select_status():
    pass
    # print("Selected status")
    



#%%

delta_t = 50


if "mpi_event" not in st.session_state:
    st.session_state.mpi_event = None

mpi_col1, mpi_col2, mpi_col3 = st.columns(3)

with mpi_col1:
    pp = st.number_input(
        label="Passing Probability", 
        value=1.0,           
        min_value=0.0,       
        max_value=1.0,   
        step=0.01,             
        format="%.2f"        
    )

with mpi_col2:
    ts = st.number_input(
        label="Enter Timesteps", 
        value=256,          
        min_value=5,      
        max_value=1000,    
        step=1,            
    )


with mpi_col3:
    at = st.number_input(
        label="Enter Activation Threshold", 
        value=100,           
        min_value=1,       
        max_value=1000,       
        step=1,            
    )



mpi_placeholder = st.empty()

if  st.session_state.mpi_event is not None and len(st.session_state.mpi_event['selection']['points']) > 0:
    country =st.session_state.mpi_event['selection']['points'][0]['location']
    st.write("Selected country:", country)
    df = get_data(country, at=at, ts=ts, pp=pp)
    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color="value",
        color_continuous_scale="Viridis",
        range_color=(0, 100),
        hover_name="country",
        animation_frame="timestep",
        title="Message Passing Choropleth"
    )

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = delta_t
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = delta_t
    mpi_placeholder.plotly_chart(fig, use_container_width=True, key="mpi_mode")

else:
    mpi = MessagePassing()
    fig = px.choropleth(
        locations=mpi.countries_input,
        color = [0.5 for _ in range(len(mpi.countries_input))],
        locationmode="country names",
        color_continuous_scale="Viridis",
        hover_name=mpi.countries_input,
        title="Message Passing Choropleth"
    )
    st.session_state.mpi_event = mpi_placeholder.plotly_chart(fig, use_container_width=True, on_select=select_status, key="select_mode")
    if  len(st.session_state.mpi_event['selection']['points']) > 0:
        fig.update_traces(selectedpoints=None)
        st.rerun()


if st.button('Reset'):
    st.session_state.mpi_event = None
    st.rerun()



# %%
