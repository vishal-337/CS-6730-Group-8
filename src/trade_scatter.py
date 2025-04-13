import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from scipy import stats

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

def update_dataframe_country_codes(df, code_columns):
    df_copy = df.copy()
    
    for col in code_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(get_country_name)
    
    return df_copy

@st.cache_data
def load_trade_sci_data():
    try:
        print("Attempting to load preprocessed merged data (trade_sci_merged.csv)...")
        merged_df = pd.read_csv(os.path.join('data', 'trade_sci_merged.csv'))
        if not merged_df.empty:
            return merged_df
        else:
            print("Preprocessed file is empty, will try to load raw files.")
    except FileNotFoundError:
        print("Preprocessed data file not found, loading raw data...")
    except Exception as e:
        st.warning(f"Error reading preprocessed file: {e}. Trying raw files.")

    try:
        print("Loading raw trade data (trade.csv)...")
        trade_df = pd.read_csv(os.path.join('data', 'trade.csv'))
        trade_df = trade_df.rename(columns={
            'iso2_o': 'source',
            'iso2_d': 'target',
            'export': 'value'
        })
        trade_df.dropna(subset=['source', 'target', 'value'], inplace=True)

        print("Loading raw SCI data (SCI.csv)...")
        sci_df = pd.read_csv(os.path.join('data', 'SCI.csv'))
        sci_df.columns = sci_df.columns.str.strip()
        sci_df.dropna(subset=['user_loc', 'fr_loc', 'scaled_sci'], inplace=True)

        if 'log_sci' not in sci_df.columns:
            sci_df['scaled_sci'] = sci_df['scaled_sci'].clip(lower=0)
            sci_df['log_sci'] = np.log1p(sci_df['scaled_sci'])

        print("Preparing merged data on the fly...")
        scatter_df = prepare_scatter_data(trade_df, sci_df)
        print(f"Prepared merged data with {len(scatter_df)} rows.")
        return scatter_df

    except FileNotFoundError as e:
        st.error(f"Could not load one or more raw data files: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while processing raw data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def prepare_scatter_data(trade_df, sci_df):
    merged_data = []
    
    for _, trade_row in trade_df.iterrows():
        source = trade_row['source']
        target = trade_row['target']
        trade_value = trade_row['value']
        
        source_upper = str(source).upper()
        target_upper = str(target).upper()
        
        sci_row = sci_df[((sci_df['user_loc'].str.upper() == source_upper) & (sci_df['fr_loc'].str.upper() == target_upper)) |
                          ((sci_df['user_loc'].str.upper() == target_upper) & (sci_df['fr_loc'].str.upper() == source_upper))]
        
        if not sci_row.empty:
            sci_value = sci_row['log_sci'].mean()
            scaled_sci_value = sci_row['scaled_sci'].mean()
            merged_data.append({
                'country_pair': f"{source}-{target}",
                'source': source,
                'target': target,
                'trade_volume': trade_value,
                'log_trade_volume': np.log1p(trade_value),
                'sci': scaled_sci_value,
                'log_sci': sci_value
            })
    
    return pd.DataFrame(merged_data)

def compute_regression(df, x_col, y_col):
    mask = ~df[x_col].isna() & ~df[y_col].isna()
    df_clean = df[mask].copy()
    x_clean = df_clean[x_col].values
    y_clean = df_clean[y_col].values
    
    if len(x_clean) < 2:
        return None, None, None, None, pd.Series([False] * len(df))
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
    y_pred = slope * x_clean + intercept
    residuals = y_clean - y_pred
    std_residuals = np.std(residuals)
    outlier_mask_clean = np.abs(residuals) > 2 * std_residuals
    df_clean['is_outlier'] = outlier_mask_clean
    
    regression_info = {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2,
        'p_value': p_value
    }
    
    outlier_series = pd.Series([False] * len(df), index=df.index)
    outlier_series.loc[df_clean.index] = df_clean['is_outlier']

    return x_clean, y_pred, regression_info, outlier_series

def display_trade_sci_scatter(scatter_df):
    st.markdown("### Correlation Between Social Ties and International Trade")
    st.markdown("""
    This visualization explores the relationship between the strength of social connections (measured by the Facebook Social Connectedness Index - SCI) 
    and the volume of bilateral trade between countries. Each point represents a pair of countries.
    
    **Why is this important?** Understanding this link provides insights into how digital social networks potentially influence economic interactions 
    and globalization patterns. A positive correlation suggests that stronger social ties might facilitate or correlate with higher trade volumes.
    
    **How can this be useful?** Policymakers and economists can use this analysis to understand factors driving trade beyond traditional economic models. 
    Businesses might identify regions with strong social ties as potential markets or partnership opportunities. Points far from the trend line (highlighted in yellow) 
    may indicate unique economic or social circumstances worth further investigation.
    """)
    
    if scatter_df is None or scatter_df.empty:
        st.warning("No data available for the scatter plot.")
        return
    
    try:
        scatter_df_named = update_dataframe_country_codes(scatter_df, ['source', 'target'])
    except Exception as e:
        st.error(f"Error converting country codes to names: {e}")
        scatter_df_named = scatter_df
    
    try:
        scatter_df_named['country_pair'] = scatter_df_named['source'].astype(str) + " - " + scatter_df_named['target'].astype(str)
    except Exception as e:
        st.error(f"Error creating country pair names: {e}")
        scatter_df_named['country_pair'] = "Pair N/A"

    x_col = 'log_sci'
    y_col = 'log_trade_volume'
    
    required_cols = [x_col, y_col, 'source', 'target', 'trade_volume', 'sci']
    if not all(col in scatter_df_named.columns for col in required_cols):
         st.error(f"Required columns for plotting ({', '.join(required_cols)}) are missing.")
         return
         
    x_reg, y_pred, reg_info, outlier_series = compute_regression(scatter_df_named, x_col, y_col)
    
    scatter_df_named['Outlier'] = outlier_series
    scatter_df_named['Color'] = scatter_df_named['Outlier'].apply(lambda x: 'Outlier' if x else 'Normal')

    try:
        fig = px.scatter(
            scatter_df_named, 
            x=x_col, 
            y=y_col,
            hover_name="country_pair",
            hover_data={
                "source": True,
                "target": True,
                "trade_volume": ':,.0f',
                "sci": ':.2f',
                x_col: False,
                y_col: False,
                'Color': False
            },
            color='Color',
            color_discrete_map={'Normal': '#636EFA', 'Outlier': 'yellow'},
            opacity=0.7,
            title="Log Social Connectedness vs. Log Trade Volume"
        )
        
        if x_reg is not None and y_pred is not None and reg_info:
            reg_label = f"Regression (R²={reg_info['r_squared']:.2f})"
            
            reg_df = pd.DataFrame({'x': x_reg, 'y': y_pred}).sort_values(by='x')

            fig.add_trace(
                go.Scatter(
                    x=reg_df['x'], 
                    y=reg_df['y'], 
                    mode='lines', 
                    name=reg_label,
                    line=dict(color='red', width=2)
                )
            )
            
            st.write(f"**Regression Analysis:** Slope={reg_info['slope']:.2f}, R-squared={reg_info['r_squared']:.2f}, p-value={reg_info['p_value']:.3g}")
        
        fig.update_layout(
            xaxis_title="Log Social Connectedness Index (Log SCI)",
            yaxis_title="Log Trade Volume",
            legend_title_text='Point Type',
            height=1000
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Outliers")
        st.markdown("""
        Outliers are country pairs where the actual trade volume significantly deviates from the volume predicted by the general trend based on social connectedness (SCI). 
        Points highlighted in yellow on the chart represent these outliers (more than 2 standard deviations from the regression line). 
        Here are some notable pairs with large deviations:
        """)
        st.markdown("""
        *   **Mexico - United States**: Trade volume is significantly **higher** than predicted by SCI alone. This is likely driven by factors such as the comprehensive USMCA (formerly NAFTA) trade agreement, deep integration of supply chains (especially in manufacturing), extensive geographical proximity along a long border, and strong historical/cultural ties facilitating business.

        *   **Kiribati - Solomon Islands**: Trade volume is significantly **lower** than predicted. Despite both being Pacific island nations, factors contributing to this could include vast maritime distances between them, the small scale of their respective economies, limited direct shipping/transport links, different primary trade partners (often larger economies like Australia, NZ, or China), and potentially less complementary economic structures.

        *   **Canada - United States**: Trade volume is significantly **higher** than predicted. This reflects one of the world's largest bilateral trade relationships, underpinned by the USMCA, the world's longest undefended border facilitating massive cross-border traffic, highly integrated economies (especially in energy and automotive sectors), shared language and cultural similarities, and geographical proximity.

        *   **Equatorial Guinea - Mali**: Trade volume is significantly **lower** than predicted. Contributing factors likely include significant geographical distance between Central and West Africa, Mali's landlocked status creating logistical hurdles, different primary economic drivers (oil for Equatorial Guinea, agriculture/gold for Mali), membership in different regional economic communities (CEMAC vs. ECOWAS), and limited direct transport infrastructure connecting the two nations.

        *   **Japan - United States**: Trade volume is significantly **higher** than predicted, despite the geographical distance. This reflects the massive size and advanced nature of both economies, strong bilateral investment flows, significant trade in high-value goods like automobiles and electronics, and a long-standing political, security, and economic alliance fostering stable trade relations.
        """)
        
    except Exception as e:
        st.error(f"An error occurred while creating the scatter plot: {e}") 