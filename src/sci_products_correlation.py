
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

def get_sci_trade_correlation_plot():
    st.markdown("### Correlation of Specific Product Trade Flows & Social Connectedness")

    # Add explanatory text
    st.markdown("""
    This Horizontal Dot Plot visualizes the what products traded between countries have the highest correlation to scocial connectedness
    
    **Why is this important?** By overlaying trade data with the Social Connectedness Index (SCI), 
    represented by the color of the links, we can explore potential correlations between 
    economic ties and social relationships on a global scale. Do stronger social connections 
    often accompany higher trade volumes, or are there significant trade partnerships where 
    social ties are relatively weaker? This visualization provides a starting point for 
    exploring these questions.
    
    **How to read the visualization:**
    *   **X-Axis:** The correlation of the export values the product to SCI values
    *   **Y-Axis:** Name of each Product.
    """)
    st.markdown("---")

    limit = 18
    data_path = os.path.join('data', 'correlation_by_product.csv')
    df = pd.read_csv(data_path)
    df = df.nlargest(limit, 'correlation')

    # Build the scatter trace
    trace = go.Scatter(
        x=df['correlation'],
        y=df['product'],
        mode='markers',
        marker=dict(size=6),
        hovertemplate='%{y}<br>Correlation: %{x:.3f}<extra></extra>'
    )
    
    fig = go.Figure(data=[trace])

    fig.update_xaxes(
        title_text='Correlation Coefficient',
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        zeroline=True,
        zerolinewidth=2,
        dtick=0.05,               
        minor=dict(
            showgrid=True,
            dtick=0.025,          
            gridwidth=0.5,
            gridcolor='lightgray'
        ),
    )

    fig.update_yaxes(
        title_text='Product',
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        tickmode='linear',
        dtick=1,
        automargin=True,
        categoryorder='total ascending',
    )

    fig.update_layout(
        title='Products vs. SCI Correlation',
        height=limit * 30,
        margin=dict(l=200, r=50, t=50, b=50),
        plot_bgcolor='white'
    )


    st.plotly_chart(fig, use_container_width=True)
