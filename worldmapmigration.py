import pandas as pd
import plotly.express as px
import pycountry
import streamlit as st

@st.cache_data
def load_data():
    ##copy your path to this file, migration_with_sci_countries.csv
    df = pd.read_csv('/Users/hamadeid/Desktop/datavis/clean-repo/data/migration_with_sci_countries.csv')
    df = df.rename(columns={
        'Origin_ISO': 'origin_iso',
        'Destination_ISO': 'dest_iso',
        '2024': 'migration',
        'scaled_sci': 'sci'
    })

    def iso2_to_iso3(iso2):
        try:
            return pycountry.countries.get(alpha_2=iso2).alpha_3
        except:
            return None

    df['origin_iso3'] = df['origin_iso'].apply(iso2_to_iso3)
    df['dest_iso3'] = df['dest_iso'].apply(iso2_to_iso3)

    return df

def render_world_sci_map():
    df = load_data()

    st.markdown("### Global SCI vs Migration Map")
    st.markdown("This is a combined visualization of World migration data and social connectedness.")

    country_options = {
        iso3: name
        for iso3, name in df[['origin_iso3', 'Origin']].dropna().drop_duplicates().values
        if iso3 is not None
    }

    selected_iso = st.selectbox(
        "Select a country",
        options=list(country_options.keys()),
        format_func=lambda x: country_options.get(x, "Unknown")
    )

    if not selected_iso:
        st.info("Please select a country to display the map.")
        return

    filtered = df[df['origin_iso3'] == selected_iso].copy()

    if filtered.empty:
        st.warning("No data found for selected country.")
        return

    sci_median = filtered['sci'].median()
    migration_median = filtered['migration'].median()

    def classify(row):
        if row['sci'] >= sci_median and row['migration'] >= migration_median:
            return "High SCI, High Migration"
        elif row['sci'] >= sci_median:
            return "High SCI, Low Migration"
        elif row['migration'] >= migration_median:
            return "Low SCI, High Migration"
        else:
            return "Low SCI, Low Migration"

    filtered['category'] = filtered.apply(classify, axis=1)
    category_colors = {
        "High SCI, High Migration": "#0d0887",
        "High SCI, Low Migration": "#7201a8",
        "Low SCI, High Migration": "#bd3786",
        "Low SCI, Low Migration": "#ed7953",
        "Origin Country": "red"
    }
    filtered['color'] = filtered['category'].map(category_colors)

    origin_row = {
        'dest_iso3': selected_iso,
        'Destination': filtered.iloc[0]['Origin'],
        'category': 'Origin Country',
        'color': 'red'
    }
    filtered = pd.concat([filtered, pd.DataFrame([origin_row])], ignore_index=True)

    category_counts = filtered['category'].value_counts().to_dict()
    counts_text = " | ".join([f"{cat}: {count} countries" for cat, count in list(category_counts.items())[:-1]])

    fig = px.choropleth(
        filtered,
        locations='dest_iso3',
        color='category',
        hover_name='Destination',
        color_discrete_map=category_colors,
        title=f"SCI vs Migration from {filtered.iloc[0]['Origin']}",
        projection='natural earth',
        locationmode='ISO-3',
        hover_data={
            'migration': True,
            'sci': True,
            'dest_iso3': True
        }
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='black',
        plot_bgcolor='black',
        title_font_color='white',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""
    <div style="text-align: center; color: white;">
        <h3>Viewing SCI and migration from: {filtered.iloc[0]['Origin']}</h3>
        <p>{counts_text}</p>
    </div>
    """, unsafe_allow_html=True)
