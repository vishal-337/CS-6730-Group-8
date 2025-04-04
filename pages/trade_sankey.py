import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(page_title="Trade & Social Connectedness Visualization", layout="wide")

# Load data
@st.cache_data
def load_data():
    try:
        # Load trade.csv - format: iso2_o,iso2_d,export (origin country, destination country, export value)
        trade_df = pd.read_csv(os.path.join('data', 'trade.csv'))
        
        # Rename columns for clarity
        trade_df = trade_df.rename(columns={
            'iso2_o': 'source',
            'iso2_d': 'target',
            'export': 'value'
        })
        
        # Load SCI.csv - format: user_loc,fr_loc,scaled_sci (origin country, destination country, SCI value)
        sci_df = pd.read_csv(os.path.join('data', 'SCI.csv'))
        
        # Clean column names by stripping whitespace
        sci_df.columns = sci_df.columns.str.strip()
        
        # Calculate log_sci column if not present
        if 'log_sci' not in sci_df.columns:
            # Add a small value to avoid log(0)
            sci_df['log_sci'] = np.log(sci_df['scaled_sci'] + 1)
        
        return trade_df, sci_df
    except FileNotFoundError as e:
        st.error(f"Could not load data files: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

trade_df, sci_df = load_data()

# App title and description
st.title("Trade Flows & Social Connectedness")
st.write("""
This visualization shows the relationship between trade flows and social connectedness between countries.
Select a country to see its trade relationships with other countries, with flows colored by Social Connectedness Index.
""")

# Check if data is loaded correctly
if trade_df.empty or sci_df.empty:
    st.error("Failed to load the required data files. Please check if 'data/trade.csv' and 'data/SCI.csv' exist.")
    st.stop()

# Display some data info
with st.expander("View Data Information"):
    st.write("### Trade Data Sample")
    st.dataframe(trade_df.head())
    
    st.write("### SCI Data Sample")
    st.dataframe(sci_df.head())

# Get list of countries for selection
countries = sorted(list(set(trade_df['source'].unique()) | set(trade_df['target'].unique())))

# User input
selected_country = st.selectbox("Select a country to visualize trade relationships:", countries)

# Filter data for selected country
@st.cache_data
def prepare_sankey_data(selected_country, trade_df, sci_df, min_trade_value=None):
    # Filter trade data for selected country (both imports and exports)
    country_trade = trade_df[(trade_df['source'] == selected_country) | 
                             (trade_df['target'] == selected_country)].copy()
    
    if min_trade_value:
        country_trade = country_trade[country_trade['value'] >= min_trade_value]
    
    # Get list of all countries involved
    all_countries = list(set(country_trade['source'].unique()) | set(country_trade['target'].unique()))
    
    # Create node indices dictionary
    nodes_dict = {country: i for i, country in enumerate(all_countries)}
    
    # Prepare node labels and colors
    node_labels = all_countries
    node_colors = ['blue' if country == selected_country else 'gray' for country in all_countries]
    
    # Prepare links
    sources = []
    targets = []
    values = []
    link_colors = []
    hover_texts = []
    
    # For each trade relationship, get the corresponding SCI value
    for _, row in country_trade.iterrows():
        source = row['source']
        target = row['target']
        value = row['value']
        
        # Get SCI value between these countries
        sci_row = sci_df[((sci_df['user_loc'] == source) & (sci_df['fr_loc'] == target)) | 
                          ((sci_df['user_loc'] == target) & (sci_df['fr_loc'] == source))]
        
        sci_value = sci_row['log_sci'].mean() if not sci_row.empty else 0
        
        # Add to our lists
        sources.append(nodes_dict[source])
        targets.append(nodes_dict[target])
        values.append(value)
        
        # Map SCI to a color (from blue for low to red for high)
        # Normalize SCI value across all SCI data
        normalized_sci = min(max((sci_value - sci_df['log_sci'].min()) / 
                                (sci_df['log_sci'].max() - sci_df['log_sci'].min()), 0), 1)
        
        # Generate color based on normalized SCI value
        link_colors.append(f'rgba({int(255 * normalized_sci)}, {int(100 * (1-normalized_sci))}, {int(255 * (1-normalized_sci))}, 0.7)')
        
        # Add hover text with formatted values
        hover_texts.append(f"Trade: {source} → {target}<br>Value: {value:,.0f}<br>SCI: {sci_value:.2f}")
    
    return node_labels, node_colors, sources, targets, values, link_colors, hover_texts

# Option to filter by minimum trade value
min_trade_value = st.slider("Minimum trade value to display:", 
                           min_value=0, 
                           max_value=int(trade_df['value'].max()/1000), 
                           value=int(trade_df['value'].max()/10000), 
                           step=1000)

# Prepare data for Sankey diagram
node_labels, node_colors, sources, targets, values, link_colors, hover_texts = prepare_sankey_data(
    selected_country, trade_df, sci_df, min_trade_value
)

# Create Sankey diagram
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

# Update layout
fig.update_layout(
    title_text=f"Trade Flows for {selected_country} (Colored by Social Connectedness)",
    font_size=12,
    height=800,
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)

# Color legend explanation
st.write("""
### Color Legend
The color of each flow represents the strength of social connectedness between countries:
- **Blue**: Lower social connectedness
- **Purple**: Medium social connectedness
- **Red**: Higher social connectedness

The width of each flow represents the trade volume.
""")

# Insights section
st.subheader("Insights")
st.write("""
This visualization helps identify how social connectedness correlates with trade volume:
- Are countries with stronger social ties also stronger trade partners?
- Do geographical neighbors show both high trade and social connectedness?
- Are there outliers with high trade but low social connectedness or vice versa?
""") 