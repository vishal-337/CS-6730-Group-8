import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

@st.cache_data
def load_trade_data():
    country_code_to_name = {}
    trade_df = pd.DataFrame()
    sci_df = pd.DataFrame()
    try:
        print("Loading country names...")
        country_names_df = pd.read_csv(
            os.path.join('data', 'country_names.csv'),
            dtype={'Code': str}
        )
        country_names_df.dropna(subset=['Code', 'Name'], inplace=True)

        print("Creating country code map...")
        temp_map = {}
        for _, row in country_names_df.iterrows():
            code = str(row['Code']).strip()
            name = str(row['Name']).strip()
            if code:
                temp_map[code] = name
        country_code_to_name = temp_map
        print(f"Created map with {len(country_code_to_name)} entries.")

        def get_country_name(code):
            if not code or pd.isna(code):
                return "Unknown"
            code_str = str(code).strip().upper()
            return country_code_to_name.get(code_str, code_str)

        print("Loading trade data...")
        trade_df = pd.read_csv(os.path.join('data', 'trade.csv'))
        trade_df = trade_df.rename(columns={
            'iso2_o': 'source',
            'iso2_d': 'target',
            'export': 'value'
        })

        trade_df.dropna(subset=['source', 'target', 'value'], inplace=True)
        trade_df = trade_df[trade_df['value'] > 0]
        trade_df['source'] = trade_df['source'].astype(str).str.upper()
        trade_df['target'] = trade_df['target'].astype(str).str.upper()

        print("Adding country names to trade data...")
        trade_df['source_name'] = trade_df['source'].apply(get_country_name)
        trade_df['target_name'] = trade_df['target'].apply(get_country_name)

        print("Loading SCI data...")
        sci_df = pd.read_csv(os.path.join('data', 'SCI.csv'))
        sci_df.columns = sci_df.columns.str.strip()

        sci_df.dropna(subset=['user_loc', 'fr_loc', 'scaled_sci'], inplace=True)
        sci_df['user_loc'] = sci_df['user_loc'].astype(str).str.upper()
        sci_df['fr_loc'] = sci_df['fr_loc'].astype(str).str.upper()

        print("Adding country names to SCI data...")
        sci_df['user_loc_name'] = sci_df['user_loc'].apply(get_country_name)
        sci_df['fr_loc_name'] = sci_df['fr_loc'].apply(get_country_name)

        if 'log_sci' not in sci_df.columns:
            print("Calculating log_sci...")
            sci_df['scaled_sci'] = sci_df['scaled_sci'].clip(lower=0)
            sci_df['log_sci'] = np.log1p(sci_df['scaled_sci'])

        if trade_df.empty:
            st.error("Trade data is empty after cleaning")
        if sci_df.empty:
            st.error("SCI data is empty after cleaning")

        print("Data loading and preprocessing complete.")
        return trade_df, sci_df, country_code_to_name

    except FileNotFoundError as e:
        st.error(f"Could not load data files: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), {}
    except Exception as e:
        st.error(f"Error processing data files: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), {}

@st.cache_data
def prepare_sankey_data(selected_country, trade_df, sci_df, country_code_to_name):
    print(f"Preparing Sankey for: {selected_country}")
    country_code_to_name_upper = {str(k).upper(): v for k, v in country_code_to_name.items()}

    def get_name_from_map(code):
        code_str = str(code).strip().upper()
        return country_code_to_name_upper.get(code_str, code_str)

    selected_country_str = str(selected_country).upper()

    imports_df = trade_df[trade_df['target'] == selected_country_str].nlargest(15, 'value')
    exports_df = trade_df[trade_df['source'] == selected_country_str].nlargest(15, 'value')

    print(f"Found {len(imports_df)} imports and {len(exports_df)} exports for {selected_country_str}")

    if imports_df.empty and exports_df.empty:
        print(f"No import or export data for {selected_country_str}")
        return [], [], [], [], [], [], [], [], []

    import_countries = list(imports_df['source'].unique())
    export_countries = list(exports_df['target'].unique())

    selected_country_name = get_name_from_map(selected_country_str)
    import_country_names = [get_name_from_map(c) for c in import_countries]
    export_country_names = [get_name_from_map(c) for c in export_countries]

    nodes = import_countries + [selected_country_str] + export_countries
    node_labels = import_country_names + [selected_country_name] + export_country_names

    num_imports = len(import_countries)
    num_exports = len(export_countries)
    selected_idx = num_imports

    node_x = [0.01] * num_imports + [0.5] + [0.99] * num_exports
    node_y = [(i + 0.5) / num_imports if num_imports > 0 else 0.5 for i in range(num_imports)] + \
             [0.5] + \
             [(i + 0.5) / num_exports if num_exports > 0 else 0.5 for i in range(num_exports)]

    node_colors = ['lightgray'] * num_imports + ['#1f77b4'] + ['lightgray'] * num_exports

    import_indices = {str(code).upper(): i for i, code in enumerate(import_countries)}
    export_indices = {str(code).upper(): i + num_imports + 1 for i, code in enumerate(export_countries)}

    sources = []
    targets = []
    values = []
    link_colors = []
    hover_texts = []

    min_log_sci = sci_df['log_sci'].min() if not sci_df.empty else 0
    max_log_sci = sci_df['log_sci'].max() if not sci_df.empty else 1
    range_log_sci = max_log_sci - min_log_sci
    if range_log_sci <= 0: range_log_sci = 1

    def get_sci_data(c1, c2):
        c1_upper = str(c1).upper()
        c2_upper = str(c2).upper()
        sci_row = sci_df[((sci_df['user_loc'] == c1_upper) & (sci_df['fr_loc'] == c2_upper)) |
                         ((sci_df['user_loc'] == c2_upper) & (sci_df['fr_loc'] == c1_upper))]
        sci_value = sci_row['log_sci'].mean() if not sci_row.empty else min_log_sci
        normalized_sci = max(0, min(1, (sci_value - min_log_sci) / range_log_sci))
        red_val = int(255 * normalized_sci)
        blue_val = int(255 * (1 - normalized_sci))
        color = f'rgba({red_val}, 0, {blue_val}, 0.6)'
        return sci_value, color

    for i, row in imports_df.iterrows():
        source_code = str(row['source']).upper()
        source_name = get_name_from_map(source_code)
        target_name = selected_country_name
        value = row['value']

        if source_code not in import_indices: continue

        sci_value, color = get_sci_data(source_code, selected_country_str)

        sources.append(import_indices[source_code])
        targets.append(selected_idx)
        values.append(value ** 0.5)
        link_colors.append(color)
        hover_texts.append(f"Import from {source_name}<br>Value: {row['value']:,.0f}<br>SCI (log): {sci_value:.2f}")

    for _, row in exports_df.iterrows():
        target_code = str(row['target']).upper()
        source_name = selected_country_name
        target_name = get_name_from_map(target_code)
        value = row['value']

        if target_code not in export_indices: continue

        sci_value, color = get_sci_data(selected_country_str, target_code)

        sources.append(selected_idx)
        targets.append(export_indices[target_code])
        values.append(value ** 0.5)
        link_colors.append(color)
        hover_texts.append(f"Export to {target_name}<br>Value: {row['value']:,.0f}<br>SCI (log): {sci_value:.2f}")

    print("Sankey data preparation finished.")
    return node_labels, node_colors, node_x, node_y, sources, targets, values, link_colors, hover_texts

def display_trade_sankey(trade_df_sankey, sci_df_sankey, country_code_to_name_map):
    st.markdown("### Top Trade Flows & Social Connectedness")

    # Add explanatory text
    st.markdown("""
    This Sankey diagram visualizes the top 15 import sources and top 15 export destinations 
    for the selected country, based on trade value. It helps us quickly understand the 
    primary trade relationships of a nation.
    
    **Why is this important?** By overlaying trade data with the Social Connectedness Index (SCI), 
    represented by the color of the links, we can explore potential correlations between 
    economic ties and social relationships on a global scale. Do stronger social connections 
    often accompany higher trade volumes, or are there significant trade partnerships where 
    social ties are relatively weaker? This visualization provides a starting point for 
    exploring these questions.
    
    **How to read the visualization:**
    *   **Columns:** Countries providing imports are on the left, the selected country is in the 
        center, and countries receiving exports are on the right.
    *   **Nodes:** Each rectangle represents a country. The central blue node is the country 
        you selected.
    *   **Links:** The bands flowing between countries represent trade flows (imports flowing 
        into the center, exports flowing out).
    *   **Link Width:** The thickness of each link is proportional to the *square root* of the 
        trade value. Using the square root helps make smaller, yet significant, trade flows 
        more visible alongside very large ones.
    *   **Link Color:** The color of the link indicates the strength of the Social Connectedness 
        Index (SCI) between the connected countries, ranging from **Blue (Low SCI)** to 
        **Red (High SCI)**, as shown in the legend below.
    """)
    st.markdown("---") # Add a separator line

    if trade_df_sankey.empty or sci_df_sankey.empty:
        st.error("Failed to load the required data files for Sankey visualization.")
        return

    countries_sankey = sorted(list(set(trade_df_sankey['source'].astype(str).str.upper().unique()) | \
                                   set(trade_df_sankey['target'].astype(str).str.upper().unique())))

    dropdown_name_map = {code: country_code_to_name_map.get(code.upper(), code) for code in countries_sankey}

    country_options = [(code, dropdown_name_map.get(code, code)) for code in countries_sankey]
    country_options.sort(key=lambda x: str(x[1]))

    selected_country_code = st.selectbox(
        "Select a country to visualize its Top 15 Imports & Exports:",
        options=[code for code, _ in country_options],
        format_func=lambda code: dropdown_name_map.get(code, code),
        key="sankey_country"
    )

    node_labels, node_colors, node_x, node_y, sources, targets, values, link_colors, hover_texts = prepare_sankey_data(
        selected_country_code, trade_df_sankey, sci_df_sankey, country_code_to_name_map
    )

    if not node_labels:
        st.warning(f"No trade data to display for {dropdown_name_map.get(selected_country_code, selected_country_code)}.")
    else:
        selected_country_name = dropdown_name_map.get(str(selected_country_code).upper(), selected_country_code)

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color=node_colors,
                x=node_x,
                y=node_y
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

        fig_sankey.update_layout(
            title_text=f"Top 15 Imports & Exports for {selected_country_name}",
            font_size=10,
            height=800,
        )

        st.plotly_chart(fig_sankey, use_container_width=True)

        # Add the new HTML/CSS color bar legend
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin-top: 15px; font-size: 0.9em;">
          <span style="margin-right: 10px; color: blue;">Low SCI</span>
          <div style="width: 250px; height: 15px; background: linear-gradient(to right, blue, purple, red); border-radius: 5px;"></div>
          <span style="margin-left: 10px; color: red;">High SCI</span>
        </div>
        <div style="text-align: center; font-size: 0.8em; color: grey; margin-top: 5px;">
        </div>
        """, unsafe_allow_html=True) 