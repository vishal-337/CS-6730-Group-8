#%%
import pandas as pd

# Replace 'your_file.xlsx' with the actual filename
df = pd.read_excel("/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/State_to_State_Migration.xlsx", engine='openpyxl', header=4)

# Preview the data
#print(df.head())
##print the columns
#print(df.columns)
#print the 8th row untruncated
#pd.set_option('display.max_columns', None)  # Show all columns
#pd.set_option('display.max_rows', None)  # Show all rows
#print(df.iloc[7])
#print all the columns in row index 3
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_rows', None)  # Show all rows
print(df.iloc[3])

#%%
import pandas as pd

# Load the Excel file
file_path = '/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/State_to_State_Migration.xlsx'  # replace with your file path
df = pd.read_excel(file_path, skiprows=2)
print(df.columns.tolist())

# Get list of state names from the columns (everything after the 5th column)
states = df.columns[6:-4]  # assuming the last 3 columns are non-states like totals/foreign/etc.
#rows, need to skip first 3 rows
#rows = df.iloc[3:, 0].tolist()  # Get the first column (state names) from the 4th row onwards

# Initialize empty list to hold cleaned rows
migration_data = []

# Iterate through each origin state (row) and destination state (column)
# need to skip first 3 rows

for _, row in df.iterrows():
    origin = row['FIPS Code']  # State name column
    for destination in states:
        migration_number = row[destination]
        # Skip NaNs and non-numeric values
        if pd.notna(migration_number):
            migration_data.append([origin, destination, int(migration_number)])

# Create cleaned DataFrame
cleaned_df = pd.DataFrame(migration_data, columns=['Origin', 'Destination', 'Migration #'])

# Optional: sort alphabetically
cleaned_df = cleaned_df.sort_values(by=['Origin', 'Destination'])

# Save as TSV
cleaned_df.to_csv('state_to_state_migration_cleaned.tsv', sep='\t', index=False)

print("Migration data has been saved to 'state_to_state_migration_cleaned.tsv'")



#%%
import pandas as pd

# Load your TSV file
df = pd.read_csv("/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/county_county.tsv", sep="\t")

# State FIPS to state name dictionary
state_fips_map = {
    "01": "ALABAMA", "02": "ALASKA", "04": "ARIZONA", "05": "ARKANSAS",
    "06": "CALIFORNIA", "08": "COLORADO", "09": "CONNECTICUT", "10": "DELAWARE",
    "11": "DISTRICT OF COLUMBIA", "12": "FLORIDA", "13": "GEORGIA", "15": "HAWAII",
    "16": "IDAHO", "17": "ILLINOIS", "18": "INDIANA", "19": "IOWA", "20": "KANSAS",
    "21": "KENTUCKY", "22": "LOUISIANA", "23": "MAINE", "24": "MARYLAND",
    "25": "MASSACHUSETTS", "26": "MICHIGAN", "27": "MINNESOTA", "28": "MISSISSIPPI",
    "29": "MISSOURI", "30": "MONTANA", "31": "NEBRASKA", "32": "NEVADA",
    "33": "NEW HAMPSHIRE", "34": "NEW JERSEY", "35": "NEW MEXICO", "36": "NEW YORK",
    "37": "NORTH CAROLINA", "38": "NORTH DAKOTA", "39": "OHIO", "40": "OKLAHOMA",
    "41": "OREGON", "42": "PENNSYLVANIA", "44": "RHODE ISLAND",
    "45": "SOUTH CAROLINA", "46": "SOUTH DAKOTA", "47": "TENNESSEE", "48": "TEXAS",
    "49": "UTAH", "50": "VERMONT", "51": "VIRGINIA", "53": "WASHINGTON",
    "54": "WEST VIRGINIA", "55": "WISCONSIN", "56": "WYOMING"
}

# Get state FIPS code from first 2 digits of user_loc (make sure it's a string and pad with zeros)
df["user_loc"] = df["user_loc"].astype(str).str.zfill(5)
df["user_state_fips"] = df["user_loc"].str[:2]
df["user_state"] = df["user_state_fips"].map(state_fips_map)

# Preview result
print(df.head())

# Optional: Save to new TSV
df.to_csv("sci_with_user_states.tsv", sep="\t", index=False)

#%%
import pandas as pd

# Load the TSV with county-to-county SCI data
df = pd.read_csv("sci_with_user_states.tsv", sep="\t")

# Ensure all FIPS codes are 5-digit strings
df["user_loc"] = df["user_loc"].astype(str).str.zfill(5)
df["fr_loc"] = df["fr_loc"].astype(str).str.zfill(5)

# Define state FIPS → state name
state_fips_map = {
    "01": "ALABAMA", "02": "ALASKA", "04": "ARIZONA", "05": "ARKANSAS",
    "06": "CALIFORNIA", "08": "COLORADO", "09": "CONNECTICUT", "10": "DELAWARE",
    "11": "DISTRICT OF COLUMBIA", "12": "FLORIDA", "13": "GEORGIA", "15": "HAWAII",
    "16": "IDAHO", "17": "ILLINOIS", "18": "INDIANA", "19": "IOWA", "20": "KANSAS",
    "21": "KENTUCKY", "22": "LOUISIANA", "23": "MAINE", "24": "MARYLAND",
    "25": "MASSACHUSETTS", "26": "MICHIGAN", "27": "MINNESOTA", "28": "MISSISSIPPI",
    "29": "MISSOURI", "30": "MONTANA", "31": "NEBRASKA", "32": "NEVADA",
    "33": "NEW HAMPSHIRE", "34": "NEW JERSEY", "35": "NEW MEXICO", "36": "NEW YORK",
    "37": "NORTH CAROLINA", "38": "NORTH DAKOTA", "39": "OHIO", "40": "OKLAHOMA",
    "41": "OREGON", "42": "PENNSYLVANIA", "44": "RHODE ISLAND",
    "45": "SOUTH CAROLINA", "46": "SOUTH DAKOTA", "47": "TENNESSEE", "48": "TEXAS",
    "49": "UTAH", "50": "VERMONT", "51": "VIRGINIA", "53": "WASHINGTON",
    "54": "WEST VIRGINIA", "55": "WISCONSIN", "56": "WYOMING"
}

# Add state columns for both origin and destination counties
df["user_state"] = df["user_loc"].str[:2].map(state_fips_map)
df["fr_state"] = df["fr_loc"].str[:2].map(state_fips_map)

county_to_state_avg = df.groupby(["user_loc", "fr_state"])["scaled_sci"].mean().reset_index(name="county_to_state_sci")

state_to_state_avg = county_to_state_avg.copy()
state_to_state_avg["user_state"] = state_to_state_avg["user_loc"].str[:2].map(state_fips_map)

final_state_sci = state_to_state_avg.groupby(["user_state", "fr_state"])["county_to_state_sci"].mean().reset_index(name="state_to_state_sci")

# Preview result
print(final_state_sci.head())

# Optional: Save to file
final_state_sci.to_csv("state_to_state_sci.tsv", sep="\t", index=False)


#%%
import pandas as pd

# Load your SCI file again (with FIPS padded)
df = pd.read_csv("sci_with_user_states.tsv", sep="\t")
df["user_loc"] = df["user_loc"].astype(str).str.zfill(5)
df["fr_loc"] = df["fr_loc"].astype(str).str.zfill(5)

# Map of state FIPS to names
state_fips_map = {
    "01": "ALABAMA", "02": "ALASKA", "04": "ARIZONA", "05": "ARKANSAS",
    "06": "CALIFORNIA", "08": "COLORADO", "09": "CONNECTICUT", "10": "DELAWARE",
    "11": "DISTRICT OF COLUMBIA", "12": "FLORIDA", "13": "GEORGIA", "15": "HAWAII",
    "16": "IDAHO", "17": "ILLINOIS", "18": "INDIANA", "19": "IOWA", "20": "KANSAS",
    "21": "KENTUCKY", "22": "LOUISIANA", "23": "MAINE", "24": "MARYLAND",
    "25": "MASSACHUSETTS", "26": "MICHIGAN", "27": "MINNESOTA", "28": "MISSISSIPPI",
    "29": "MISSOURI", "30": "MONTANA", "31": "NEBRASKA", "32": "NEVADA",
    "33": "NEW HAMPSHIRE", "34": "NEW JERSEY", "35": "NEW MEXICO", "36": "NEW YORK",
    "37": "NORTH CAROLINA", "38": "NORTH DAKOTA", "39": "OHIO", "40": "OKLAHOMA",
    "41": "OREGON", "42": "PENNSYLVANIA", "44": "RHODE ISLAND",
    "45": "SOUTH CAROLINA", "46": "SOUTH DAKOTA", "47": "TENNESSEE", "48": "TEXAS",
    "49": "UTAH", "50": "VERMONT", "51": "VIRGINIA", "53": "WASHINGTON",
    "54": "WEST VIRGINIA", "55": "WISCONSIN", "56": "WYOMING"
}

# Add user_state and fr_state columns
df["user_state"] = df["user_loc"].str[:2].map(state_fips_map)
df["fr_state"] = df["fr_loc"].str[:2].map(state_fips_map)

# Group by state-to-state and average all county-to-county SCI values
state_to_state_avg_simple = df.groupby(["user_state", "fr_state"])["scaled_sci"].mean().reset_index(name="state_to_state_sci")

# Preview results
print(state_to_state_avg_simple.head())

# Save to file if needed
state_to_state_avg_simple.to_csv("state_to_state_sci_simple1.tsv", sep="\t", index=False)


#%%
import pandas as pd

# Load migration data
migration_df = pd.read_csv('state_to_state_migration_cleaned.tsv', sep='\t')

# Load SCI data
sci_df = pd.read_csv('state_to_state_sci.tsv', sep='\t')  # change filename if needed

# Standardize state names to uppercase for matching
migration_df['Origin_upper'] = migration_df['Origin'].str.upper().str.strip()
migration_df['Destination_upper'] = migration_df['Destination'].str.upper().str.strip()
sci_df['user_state'] = sci_df['user_state'].str.strip()
sci_df['fr_state'] = sci_df['fr_state'].str.strip()

# Merge on uppercase names
merged_df = pd.merge(
    migration_df,
    sci_df,
    left_on=['Origin_upper', 'Destination_upper'],
    right_on=['user_state', 'fr_state'],
    how='inner'  # or 'left' if you want to keep all migration rows
)

# Drop helper columns and keep desired output
final_df = merged_df[['Origin', 'Destination', 'Migration #', 'state_to_state_sci']]

# Save to TSV
final_df.to_csv('migration_with_sci.tsv', sep='\t', index=False)

print("Merged file saved as 'migration_with_sci.tsv'")


# %%
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv('migration_with_sci.tsv', sep='\t')

# Clean any whitespace issues
df['Origin'] = df['Origin'].str.strip().str.upper()

# State name to code (needed for choropleth)
state_to_code = {
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
    'DISTRICT OF COLUMBIA': 'DC', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
    # Add more as needed
}

df['state_code'] = df['Origin'].map(state_to_code)

# Aggregate total outbound migration per state
agg = df.groupby('state_code').agg({
    'Migration #': 'sum',
    'state_to_state_sci': 'mean'  # optional, for future maps
}).reset_index()
fig = px.choropleth(
    agg,
    locations='state_code',
    locationmode="USA-states",
    color='Migration #',
    color_continuous_scale="Reds",
    scope="usa",
    labels={'Migration #': 'Total Outbound Migration'},
    title="Outbound Migration Volume by State"
)
fig.show()


