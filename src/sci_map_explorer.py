import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
import traceback
import plotly.graph_objects as go
import numpy as np

@st.cache_data
def load_country_name_map():
    """Loads country name to code mapping from CSV."""
    try:
        names_df = pd.read_csv("data/country_names.csv")
        names_df.columns = names_df.columns.str.strip()
        code_to_name = pd.Series(names_df.Name.values,index=names_df.Code).to_dict()
        return code_to_name
    except FileNotFoundError:
        st.error("Error: country_names.csv not found in the data directory.")
        return {}
    except Exception as e:
        st.error(f"An error occurred while loading country names: {e}")
        return {}

@st.cache_data
def load_sci_data_for_map():
    """Loads SCI data, converts codes, and adds country names."""
    code_to_name_map = load_country_name_map()
    if not code_to_name_map:
        st.warning("Country name map is empty, names may not display correctly.")

    try:
        df = pd.read_csv("data/SCI.csv")
        df.columns = df.columns.str.strip()

        def get_alpha3(code):
            try:
                return pycountry.countries.get(alpha_2=code).alpha_3
            except (AttributeError, LookupError):
                return None

        df['fr_loc_alpha3'] = df['fr_loc'].apply(get_alpha3)
        df['user_loc_alpha3'] = df['user_loc'].apply(get_alpha3)
        df['fr_loc_alpha2'] = df['fr_loc']
        df['user_loc_alpha2'] = df['user_loc']

        df['user_loc_name'] = df['user_loc_alpha2'].map(code_to_name_map).fillna(df['user_loc_alpha2'])
        df['fr_loc_name'] = df['fr_loc_alpha2'].map(code_to_name_map).fillna(df['fr_loc_alpha2'])

        df_clean = df.dropna(subset=['fr_loc_alpha3']).copy()

        return df_clean
    except FileNotFoundError:
        st.error("Error: SCI.csv not found in the data directory. Please ensure the file exists at 'data/SCI.csv'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading or processing SCI data:")
        st.error(f"Error type: {type(e).__name__}")
        st.error(f"Error details: {e}")
        st.error("Detailed traceback:")
        st.code(traceback.format_exc())
        return pd.DataFrame()

def display_sci_map_explorer():
    """Displays the SCI World Map Explorer section in the Streamlit app."""
    st.markdown("<h2 style='text-align: center;'>SCI World Map Explorer</h2>", unsafe_allow_html=True)
    st.write("Select an origin country to visualize its Social Connectedness Index (SCI) with other countries.")

    code_to_name_map = load_country_name_map()

    sci_map_data = load_sci_data_for_map()

    if not sci_map_data.empty:
        if 'user_loc_name' in sci_map_data.columns:
            sci_map_data['user_loc_name'] = sci_map_data['user_loc_name'].astype(str)
            origin_country_names = sorted(sci_map_data['user_loc_name'].unique())
            default_name = "United States"
            default_index = origin_country_names.index(default_name) if default_name in origin_country_names else 0
        else:
            st.warning("Could not find country names for selection.")
            sci_map_data['user_loc_alpha2'] = sci_map_data['user_loc_alpha2'].astype(str)
            origin_country_names = sorted(sci_map_data['user_loc_alpha2'].unique())
            default_name = "US"
            default_index = origin_country_names.index(default_name) if default_name in origin_country_names else 0
            st.info("Displaying country codes instead of names in dropdown.")

        selected_origin_name_or_code = st.selectbox(
            "Select Origin Country:",
            options=origin_country_names,
            index=default_index
        )

        if 'user_loc_name' in sci_map_data.columns and selected_origin_name_or_code in code_to_name_map.values():
             selected_origin_country_alpha2 = sci_map_data.loc[sci_map_data['user_loc_name'] == selected_origin_name_or_code, 'user_loc_alpha2'].iloc[0]
             display_title_name = selected_origin_name_or_code
        else:
             selected_origin_country_alpha2 = selected_origin_name_or_code
             display_title_name = selected_origin_country_alpha2

        if selected_origin_country_alpha2:
            filtered_data_full = sci_map_data[
                sci_map_data['user_loc_alpha2'] == selected_origin_country_alpha2
            ].copy()

            origin_data = filtered_data_full[filtered_data_full['user_loc_alpha2'] == filtered_data_full['fr_loc_alpha2']].copy()

            filtered_data = filtered_data_full[
                filtered_data_full['user_loc_alpha2'] != filtered_data_full['fr_loc_alpha2']
            ]

            filtered_data['scaled_sci'] = pd.to_numeric(filtered_data['scaled_sci'], errors='coerce')
            filtered_data.dropna(subset=['scaled_sci'], inplace=True)

            # Calculate log of scaled_sci (using log1p for handling potential zeros)
            filtered_data['log_scaled_sci'] = np.log1p(filtered_data['scaled_sci'])

            if not filtered_data.empty:
                try:
                    fig_map = px.choropleth(
                        filtered_data,
                        locations="fr_loc_alpha3",
                        color="log_scaled_sci",
                        hover_name="fr_loc_name",
                        hover_data={
                            "fr_loc_name": True,
                            "scaled_sci": True,
                            "log_scaled_sci": False,
                            "fr_loc_alpha3": False,
                            "fr_loc_alpha2": False,
                        },
                        locationmode='ISO-3',
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title=f"Social Connectedness from {display_title_name}",
                        labels={'log_scaled_sci': 'Log Scaled SCI', 'fr_loc_name': 'Country', 'scaled_sci': 'Scaled SCI'}
                    )

                    if not origin_data.empty and 'user_loc_alpha3' in origin_data.columns and not origin_data['user_loc_alpha3'].isnull().all():
                        fig_map.add_trace(go.Choropleth(
                            locations=origin_data['user_loc_alpha3'],
                            z=[0] * len(origin_data),
                            locationmode='ISO-3',
                            colorscale=[[0, 'black'], [1, 'black']],
                            showscale=False,
                            hoverinfo='skip'
                        ))

                    fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=1000)
                    st.plotly_chart(fig_map, use_container_width=True)
                except Exception as e:
                    st.error(f"An error occurred while generating the map:")
                    st.error(f"Error type: {type(e).__name__}")
                    st.error(f"Error details: {e}")
                    st.error("Detailed traceback for map generation:")
                    st.code(traceback.format_exc())
            else:
                st.info(f"No connection data (excluding self-connection) found for {selected_origin_country_alpha2} to display on the map.")
    else:
        st.warning("Could not load SCI data for the map explorer.") 