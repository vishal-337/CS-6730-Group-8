import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

@st.cache_data
def load_country_names():
    try:
        country_names_df = pd.read_csv(os.path.join('data', 'country_names.csv'))
        country_code_to_name = dict(zip(country_names_df['Code'], country_names_df['Name']))
        return country_code_to_name
    except Exception as e:
        st.error(f"Error loading country names CSV: {e}")
        return {}

@st.cache_data
def get_country_name(code):
    country_code_to_name = load_country_names()
    if not code or pd.isna(code):
        return "Unknown"
    code = code.upper()
    if code in country_code_to_name:
        return country_code_to_name[code]
    return code

def rename_matrix_indices(matrix):
    matrix_copy = matrix.copy()
    index_mapping = {idx: get_country_name(idx) for idx in matrix_copy.index}
    column_mapping = {col: get_country_name(col) for col in matrix_copy.columns}
    matrix_copy = matrix_copy.rename(index=index_mapping, columns=column_mapping)
    return matrix_copy

@st.cache_data
def load_and_prepare_heatmap_data(trade_sci_df, top_n=50):
    if not isinstance(trade_sci_df, pd.DataFrame) or trade_sci_df.empty:
        st.warning("Invalid or empty data received for heatmap preparation.")
        return None

    required_cols = ['source', 'target', 'trade_volume', 'sci']
    if not all(col in trade_sci_df.columns for col in required_cols):
        st.error(f"Heatmap data is missing required columns: {required_cols}")
        return None

    try:
        trade_matrix = pd.read_csv(os.path.join('data', 'trade_matrix_top50.csv'), index_col=0)
        sci_matrix = pd.read_csv(os.path.join('data', 'sci_matrix_top50.csv'), index_col=0)

        if top_n == 50 and not trade_matrix.empty and not sci_matrix.empty:
             trade_matrix.index = trade_matrix.index.astype(str)
             trade_matrix.columns = trade_matrix.columns.astype(str)
             sci_matrix.index = sci_matrix.index.astype(str)
             sci_matrix.columns = sci_matrix.columns.astype(str)
        else:
             raise FileNotFoundError

    except FileNotFoundError:
        country_trade_totals = trade_sci_df.groupby('source')['trade_volume'].sum()
        top_countries_series = country_trade_totals.nlargest(top_n)
        top_country_codes = top_countries_series.index.astype(str).tolist()

        trade_matrix = pd.DataFrame(0.0, index=top_country_codes, columns=top_country_codes, dtype='float64')
        sci_matrix = pd.DataFrame(0.0, index=top_country_codes, columns=top_country_codes, dtype='float64')

        for _, row in trade_sci_df.iterrows():
            source = str(row['source'])
            target = str(row['target'])
            if source in top_country_codes and target in top_country_codes:
                trade_matrix.at[source, target] = float(row['trade_volume'])
                sci_matrix.at[source, target] = float(row['sci'])

    if trade_matrix.empty or sci_matrix.empty:
        st.warning("Could not create valid trade/SCI matrices.")
        return None

    trade_matrix.replace([np.inf, -np.inf], np.nan, inplace=True)
    sci_matrix.replace([np.inf, -np.inf], np.nan, inplace=True)
    trade_matrix.fillna(0, inplace=True)
    sci_matrix.fillna(0, inplace=True)

    trade_matrix_log = np.log1p(trade_matrix)
    sci_matrix_log = np.log1p(sci_matrix)

    min_trade_log, max_trade_log = trade_matrix_log.min().min(), trade_matrix_log.max().max()
    min_sci_log, max_sci_log = sci_matrix_log.min().min(), sci_matrix_log.max().max()

    trade_range = max_trade_log - min_trade_log
    sci_range = max_sci_log - min_sci_log

    trade_matrix_norm = (trade_matrix_log - min_trade_log) / trade_range if trade_range > 0 else pd.DataFrame(0.0, index=trade_matrix_log.index, columns=trade_matrix_log.columns)
    sci_matrix_norm = (sci_matrix_log - min_sci_log) / sci_range if sci_range > 0 else pd.DataFrame(0.0, index=sci_matrix_log.index, columns=sci_matrix_log.columns)

    correlation_matrix = np.sqrt(trade_matrix_norm * sci_matrix_norm)
    difference_matrix = trade_matrix_norm - sci_matrix_norm

    try:
        trade_matrix_named = rename_matrix_indices(trade_matrix)
        sci_matrix_named = rename_matrix_indices(sci_matrix)
        trade_matrix_norm_named = rename_matrix_indices(trade_matrix_norm)
        sci_matrix_norm_named = rename_matrix_indices(sci_matrix_norm)
        correlation_matrix_named = rename_matrix_indices(correlation_matrix)
        difference_matrix_named = rename_matrix_indices(difference_matrix)
    except Exception as e:
        st.error(f"Error renaming matrix indices: {e}")
        trade_matrix_named, sci_matrix_named = trade_matrix, sci_matrix
        trade_matrix_norm_named, sci_matrix_norm_named = trade_matrix_norm, sci_matrix_norm
        correlation_matrix_named, difference_matrix_named = correlation_matrix, difference_matrix

    country_names = list(trade_matrix_named.index)

    return {
        'trade_matrix': trade_matrix_named,
        'sci_matrix': sci_matrix_named,
        'trade_matrix_norm': trade_matrix_norm_named,
        'sci_matrix_norm': sci_matrix_norm_named,
        'correlation_matrix': correlation_matrix_named,
        'difference_matrix': difference_matrix_named,
        'top_countries': country_names
    }

def display_trade_sci_heatmap(trade_sci_df):
    st.markdown("### Heatmap Analysis: Correlation Between Trade and Social Connectedness")

    if trade_sci_df is None or trade_sci_df.empty:
        st.warning("No data available for heatmap visualization.")
        return

    top_n = 50
    heatmap_data = load_and_prepare_heatmap_data(trade_sci_df, top_n)

    if heatmap_data is None:
        return

    matrix = heatmap_data['correlation_matrix']
    color_scale = "Viridis"
    title = "Correlation Between Trade and Social Connectedness (Normalized Log Values)"
    hover_template = "Countries: %{y}-%{x}<br>Correlation Score: %{z:.2f}<extra></extra>"

    if matrix is None or matrix.empty:
        st.warning("Could not display correlation heatmap.")
        return

    st.write("""
**Visualization Explanation:**

This heatmap visualizes the relationship between international trade volume and the Social Connectedness Index (SCI) for the top 50 countries, ranked by total trade volume. It displays a correlation score for each country pair, indicating how strongly their trade and social connections align. To calculate this score, both trade volume and SCI values are first adjusted using a log transformation to better handle large variations in the data. These adjusted values are then normalized to a standard 0-1 scale. The final score represents the combined strength of these normalized trade and social ties for each country pair, calculated using a geometric mean. A higher score signifies that both trade and SCI are relatively strong for that pair compared to others.

The Y-axis shows the source country (exporter or origin of social connection), and the X-axis shows the target country (importer or destination). The color intensity indicates the correlation score: brighter colors (like yellow) signify a higher correlation, meaning pairs where both normalized trade and SCI tend to be strong relative to other pairs. Darker colors (like purple or blue) indicate a lower score, where at least one of the metrics is weak. You can hover over any cell to see the specific countries and their correlation score. This visualization helps identify where economic ties (trade) and social ties (SCI) align. High correlation (bright cells) often suggests well-established, multifaceted relationships where strong trade and strong social connections go hand-in-hand. Low correlation (dark cells) might highlight interesting cases: strong trade despite weak social ties could indicate trade driven by other factors, while strong social ties with weak trade could point to untapped potential for economic partnership development. It allows for a deeper understanding of how social networks and international trade patterns interact.
""")

    try:
        fig = go.Figure(data=go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=matrix.index,
            colorscale=color_scale,
            hovertemplate=hover_template
        ))

        fig.update_layout(
            title=title,
            height=1000,
            xaxis=dict(title="Target Country"),
            yaxis=dict(title="Source Country", autorange='reversed')
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating heatmap figure: {e}")