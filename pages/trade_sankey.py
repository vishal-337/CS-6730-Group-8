import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(page_title="Trade & Social Connectedness Visualization", layout="wide")

@st.cache_data
def load_data():
    try:
        trade_df = pd.read_csv(os.path.join('data', 'trade.csv'))
        
        trade_df = trade_df.rename(columns={
            'iso2_o': 'source',
            'iso2_d': 'target',
            'export': 'value'
        })
        
        sci_df = pd.read_csv(os.path.join('data', 'SCI.csv'))
        
        sci_df.columns = sci_df.columns.str.strip()
        
        if 'log_sci' not in sci_df.columns:
            sci_df['log_sci'] = np.log(sci_df['scaled_sci'] + 1)
        
        return trade_df, sci_df
    except FileNotFoundError as e:
        st.error(f"Could not load data files: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

trade_df, sci_df = load_data()

st.title("Trade Flows & Social Connectedness")


if trade_df.empty or sci_df.empty:
    st.error("Failed to load the required data files. Please check if 'data/trade.csv' and 'data/SCI.csv' exist.")
    st.stop()


countries = sorted(list(set(trade_df['source'].unique()) | set(trade_df['target'].unique())))

selected_country = st.selectbox("Select a country to visualize trade relationships:", countries)

@st.cache_data
def prepare_sankey_data(selected_country, trade_df, sci_df, min_trade_value=None):
    country_trade = trade_df[(trade_df['source'] == selected_country) | 
                             (trade_df['target'] == selected_country)].copy()
    
    if min_trade_value:
        country_trade = country_trade[country_trade['value'] >= min_trade_value]
    
    all_countries = list(set(country_trade['source'].unique()) | set(country_trade['target'].unique()))
    
    nodes_dict = {country: i for i, country in enumerate(all_countries)}
    
    node_labels = all_countries
    node_colors = ['blue' if country == selected_country else 'gray' for country in all_countries]
    
    sources = []
    targets = []
    values = []
    link_colors = []
    hover_texts = []
    
    for _, row in country_trade.iterrows():
        source = row['source']
        target = row['target']
        value = row['value']
        
        sci_row = sci_df[((sci_df['user_loc'] == source) & (sci_df['fr_loc'] == target)) | 
                          ((sci_df['user_loc'] == target) & (sci_df['fr_loc'] == source))]
        
        sci_value = sci_row['log_sci'].mean() if not sci_row.empty else 0
        
        sources.append(nodes_dict[source])
        targets.append(nodes_dict[target])
        values.append(value)
        
        normalized_sci = min(max((sci_value - sci_df['log_sci'].min()) / 
                                (sci_df['log_sci'].max() - sci_df['log_sci'].min()), 0), 1)
        
        link_colors.append(f'rgba({int(255 * normalized_sci)}, {int(100 * (1-normalized_sci))}, {int(255 * (1-normalized_sci))}, 0.7)')
        
        hover_texts.append(f"Trade: {source} → {target}<br>Value: {value:,.0f}<br>SCI: {sci_value:.2f}")
    
    return node_labels, node_colors, sources, targets, values, link_colors, hover_texts

min_trade_value = st.slider("Minimum trade value to display:", 
                           min_value=0, 
                           max_value=int(trade_df['value'].max()/1000), 
                           value=int(trade_df['value'].max()/10000), 
                           step=1000)

node_labels, node_colors, sources, targets, values, link_colors, hover_texts = prepare_sankey_data(
    selected_country, trade_df, sci_df, min_trade_value
)

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=node_labels,
        color=node_colors
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color=link_colors,
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts
    )
)])

fig.update_layout(
    title_text=f"Trade Flows for {selected_country} (Colored by Social Connectedness)",
    font_size=12,
    height=800,
)

st.plotly_chart(fig, use_container_width=True)

st.write("""
- **Blue**: Lower SCI
- **Purple**: Medium SCI
- **Red**: Higher SCI

""")


