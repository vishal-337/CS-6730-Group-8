
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# State abbreviations
state_abbrev = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
    'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
    'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon',
    'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia',
    'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}
full_to_abbrev = {v: k for k, v in state_abbrev.items()}

@st.cache_data
def load_data():
    df = pd.read_csv('/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/migration_with_sci.tsv', sep='\t')  # Adjust path as needed
    df = df[df['Origin'] != df['Destination']]
    df = df.dropna(subset=['Migration #', 'state_to_state_sci'])
    return df

def render_us_sci_map():
    df = load_data()

    selected_state = st.selectbox("Select a state", sorted(df['Origin'].unique()))

    state_data = df[df['Origin'] == selected_state].copy()
    sci_median = state_data['state_to_state_sci'].median()
    migration_median = state_data['Migration #'].median()

    def categorize_correlation(row):
        if row['state_to_state_sci'] >= sci_median and row['Migration #'] >= migration_median:
            return 'High SCI, High Migration'
        elif row['state_to_state_sci'] >= sci_median:
            return 'High SCI, Low Migration'
        elif row['Migration #'] >= migration_median:
            return 'Low SCI, High Migration'
        else:
            return 'Low SCI, Low Migration'

    state_data['correlation_category'] = state_data.apply(categorize_correlation, axis=1)

    category_mapping = {
        'High SCI, High Migration': 0,
        'High SCI, Low Migration': 0.33,
        'Low SCI, High Migration': 0.66,
        'Low SCI, Low Migration': 1
    }
    state_data['color_value'] = state_data['correlation_category'].map(category_mapping)
    state_data['state_abbrev'] = state_data['Destination'].map(full_to_abbrev)

    # Plot
    fig = px.choropleth(
        state_data,
        locations='state_abbrev',
        locationmode="USA-states",
        scope="usa",
        color='color_value',
        color_continuous_scale=[
            [0, '#0d0887'],
            [0.33, '#7201a8'],
            [0.66, '#bd3786'],
            [1, '#ed7953']
        ],
        range_color=[0, 1],
        hover_name='Destination',
        hover_data={
            'Migration #': True,
            'state_to_state_sci': True,
            'correlation_category': True
        }
    )

    # Highlight origin
    fig.add_trace(
        go.Choropleth(
            locations=[full_to_abbrev[selected_state]],
            z=[1],
            locationmode="USA-states",
            colorscale=[[0, 'red'], [1, 'red']],
            showscale=False,
            hoverinfo='text',
            text=selected_state
        )
    )

    fig.update_layout(
        title_text=f"SCI vs. Migration from {selected_state}",
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
            landcolor='rgb(242, 242, 242)'
        ),
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Inline Legend
    st.markdown("""
    <div style='display: flex; gap: 20px; flex-wrap: wrap; margin-top: 20px;'>
        <div style='display: flex; align-items: center;'>
            <div style='width: 20px; height: 20px; background-color: #0d0887; margin-right: 8px;'></div>
            High SCI, High Migration
        </div>
        <div style='display: flex; align-items: center;'>
            <div style='width: 20px; height: 20px; background-color: #7201a8; margin-right: 8px;'></div>
            High SCI, Low Migration
        </div>
        <div style='display: flex; align-items: center;'>
            <div style='width: 20px; height: 20px; background-color: #bd3786; margin-right: 8px;'></div>
            Low SCI, High Migration
        </div>
        <div style='display: flex; align-items: center;'>
            <div style='width: 20px; height: 20px; background-color: #ed7953; margin-right: 8px;'></div>
            Low SCI, Low Migration
        </div>
    </div>
    """, unsafe_allow_html=True)




