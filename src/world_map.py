#%%


import plotly.express as px
import pandas as pd

from streamlit_plotly_events import plotly_events
import streamlit as st


#%%
def create_world_map():
    
    fig = px.choropleth(
        st.session_state.df,
        locations='country',
        locationmode='country names',
        color='value',
        color_continuous_scale='Viridis',
        title='Interactive World Map'
    )
    fig.update_geos(
        showcountries=True,
        countrycolor="black",
        showcoastlines=True,
        coastlinecolor="gray",
        projection_scale=1.2
    )
    fig.update_layout(width=1000, height=600, margin={"r": 0, "t": 50, "l": 0, "b": 0})
    return fig

def create_custom_map(df):
    
    fig = px.choropleth(
        df,
        locations='country',
        locationmode='country names',
        color='value',
        color_continuous_scale='Viridis',
        title='Updated World Map'
    )
    fig.update_geos(
        showcountries=True,
        countrycolor="black",
        showcoastlines=True,
        coastlinecolor="gray",
        projection_scale=1.2
    )
    fig.update_layout(width=1000, height=600, margin={"r": 0, "t": 50, "l": 0, "b": 0})
    return fig

#%%

if __name__ == "__main__":
    data = {
        'country': ['United States', 'Canada', 'Mexico'],
        'value': [100, 200, 300]
    }

    st.markdown("## Clickable Interactive World Map")
    fig = create_world_map()
    
    selected_points = plotly_events(fig, click_event=True)

    map_placeholder = st.empty()

    if selected_points:
        selected_country = selected_points[0].get('location')
        st.write("Selected country:", selected_country)
        
        if selected_country in st.session_state.df['country'].values:
            for timestep in range(100):
                st.session_state.df.loc[st.session_state.df['country'] == selected_country, 'value'] += 1
                updated_fig = create_custom_map(st.session_state.df)
                map_placeholder.plotly_chart(updated_fig, use_container_width=True)
                time.sleep(0.1)
            st.write(f"Simulation complete for {selected_country}.")
        else:
            st.error("Selected country not found in the data.")
    else:
        st.plotly_chart(fig, use_container_width=True)
        st.write("Click on a country to start the simulation.")

# %%

