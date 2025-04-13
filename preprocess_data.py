import pandas as pd
import numpy as np
import os

print("Starting data preprocessing...")
print("Loading country names mapping...")
try:
    country_names_df = pd.read_csv(os.path.join('data', 'country_names.csv'))
    country_code_to_name = dict(zip(country_names_df['Code'], country_names_df['Name']))
    print(f"Loaded {len(country_code_to_name)} country mappings")
except Exception as e:
    print(f"Error loading country names CSV: {e}")
    country_code_to_name = {}

def get_country_name(code):
    if not code or pd.isna(code):
        return "Unknown"
    code = code.upper()
    if code in country_code_to_name:
        return country_code_to_name[code]
    return code

try:
    print("Loading trade data...")
    trade_df = pd.read_csv(os.path.join('data', 'trade.csv'))
    trade_df = trade_df.rename(columns={
        'iso2_o': 'source',
        'iso2_d': 'target',
        'export': 'value'
    })
    print("Adding country names to trade data...")
    trade_df['source_name'] = trade_df['source'].apply(get_country_name)
    trade_df['target_name'] = trade_df['target'].apply(get_country_name)

    print("Loading SCI data...")
    sci_df = pd.read_csv(os.path.join('data', 'SCI.csv'))
    sci_df.columns = sci_df.columns.str.strip()
    if 'log_sci' not in sci_df.columns:
        print("Calculating log_sci...")
        sci_df['log_sci'] = np.log1p(sci_df['scaled_sci'])
    print("Adding country names to SCI data...")
    sci_df['user_loc_name'] = sci_df['user_loc'].apply(get_country_name)
    sci_df['fr_loc_name'] = sci_df['fr_loc'].apply(get_country_name)

    print("Preprocessing scatter plot data...")
    merged_data = []
    for _, trade_row in trade_df.iterrows():
        source = trade_row['source']
        target = trade_row['target']
        source_name = trade_row['source_name']
        target_name = trade_row['target_name']
        trade_value = trade_row['value']
        sci_row = sci_df[((sci_df['user_loc'] == source) & (sci_df['fr_loc'] == target)) |
                          ((sci_df['user_loc'] == target) & (sci_df['fr_loc'] == source))]
        if not sci_row.empty:
            sci_value = sci_row['log_sci'].mean()
            scaled_sci_value = sci_row['scaled_sci'].mean()
            merged_data.append({
                'country_pair': f"{source_name} - {target_name}",
                'source': source,
                'target': target,
                'source_name': source_name,
                'target_name': target_name,
                'trade_volume': trade_value,
                'log_trade_volume': np.log1p(trade_value),
                'sci': scaled_sci_value,
                'log_sci': sci_value
            })
    scatter_df = pd.DataFrame(merged_data)

    print("Preprocessing heatmap data...")
    country_trade_totals = {}
    country_names = {}
    for _, row in trade_df.iterrows():
        source = row['source']
        target = row['target']
        source_name = row['source_name']
        value = row['value']
        if source not in country_trade_totals:
            country_trade_totals[source] = 0
            country_names[source] = source_name
        if target not in country_trade_totals:
            country_trade_totals[target] = 0
            target_matches = trade_df[trade_df['source'] == target]
            if len(target_matches) > 0:
                country_names[target] = target_matches.iloc[0]['source_name']
            else:
                country_names[target] = get_country_name(target)
        country_trade_totals[source] += value
    top_countries = sorted(country_trade_totals.items(), key=lambda x: x[1], reverse=True)[:50]
    top_country_codes = [country[0] for country in top_countries]
    top_country_names = [country_names.get(code, get_country_name(code)) for code in top_country_codes]

    print(f"Creating matrices for {len(top_country_codes)} top countries...")
    trade_matrix = pd.DataFrame(0.0, index=top_country_codes, columns=top_country_codes, dtype='float64')
    for _, row in trade_df.iterrows():
        source = row['source']
        target = row['target']
        if source in top_country_codes and target in top_country_codes:
            trade_matrix.loc[source, target] = float(row['value'])

    sci_matrix = pd.DataFrame(0.0, index=top_country_codes, columns=top_country_codes, dtype='float64')
    for _, row in sci_df.iterrows():
        source = row['user_loc']
        target = row['fr_loc']
        if source in top_country_codes and target in top_country_codes:
            sci_matrix.loc[source, target] = float(row['scaled_sci'])
    name_mapping = {code: name for code, name in zip(top_country_codes, top_country_names)}

    print("Renaming matrix indices to country names...")
    trade_matrix_named = trade_matrix.rename(index=name_mapping, columns=name_mapping)
    sci_matrix_named = sci_matrix.rename(index=name_mapping, columns=name_mapping)

    print("Saving processed data...")
    scatter_df.to_csv(os.path.join('data', 'trade_sci_merged.csv'), index=False)
    print(f"Saved trade_sci_merged.csv with {len(scatter_df)} rows")
    trade_matrix_named.to_csv(os.path.join('data', 'trade_matrix_top50.csv'))
    print("Saved trade_matrix_top50.csv with country names")
    sci_matrix_named.to_csv(os.path.join('data', 'sci_matrix_top50.csv'))
    print("Saved sci_matrix_top50.csv with country names")

    country_df = pd.DataFrame({
        'country_code': [k for k, v in country_trade_totals.items()],
        'country': [country_names.get(k, get_country_name(k)) for k, v in country_trade_totals.items()],
        'total_trade': [float(v) for k, v in country_trade_totals.items()]
    })
    country_df = country_df.sort_values('total_trade', ascending=False)
    country_df.to_csv(os.path.join('data', 'country_trade_totals.csv'), index=False)
    print("Saved country_trade_totals.csv with country names")

    print("Preprocessing complete!")

except Exception as e:
    import traceback
    print(f"Error during preprocessing: {str(e)}")
    traceback.print_exc()