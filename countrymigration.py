import pandas as pd
import pycountry

# Step 1: Load the data
filePath = "/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/migrationexcelcountries.xlsx"
#df = pd.read_excel("/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/migrationexcelcountries.xlsx", header=None)  # Update with your filename
df = pd.read_excel(filePath, skiprows=3)  # Update with your filename

print(df.columns.tolist())
print(df.head())

# Step 2: Extract a set of all country names (for validation)
valid_countries = set(country.name for country in pycountry.countries)

country_name_replacements = {
    "United States of America": "United States",
    "Russian Federation": "Russia",
    "Czechia": "Czech Republic",
    "Côte d'Ivoire": "Ivory Coast",
    
    "Republic of Korea": "Korea, Republic of",
    "Democratic People's Republic of Korea": "North Korea",
    "Iran (Islamic Republic of)": "Iran",
    "Venezuela (Bolivarian Republic of)": "Venezuela, Bolivarian Republic of",
    "Bolivia (Plurinational State of)": "Bolivia, Plurinational State of",
    "Lao People's Democratic Republic": "Laos",
    "Brunei Darussalam": "Brunei",
    "Micronesia (Federated States of)": "Micronesia",
    "Republic of Moldova": "Moldova",
    "The former Yugoslav Republic of Macedonia": "North Macedonia",
    "China, Hong Kong SAR": "Hong Kong",
    "China, Macao SAR": "Macau",
    "State of Palestine": "Palestine, State of",
}
print("Valid countries extracted from pycountry:")
print(valid_countries)

def clean_country_name(name):
    if isinstance(name, str):
        name_clean = name.replace("*", "").strip()
        return country_name_replacements.get(name_clean, name_clean)
    return name


def is_valid_country(name):
    cleaned = clean_country_name(name)
    return cleaned in valid_countries

df_filtered = df[
    df["Region, development group, country or area of destination"].apply(is_valid_country) &
    df["Region, development group, country or area of origin"].apply(is_valid_country)
]

df_filtered["Region, development group, country or area of destination"] = df_filtered["Region, development group, country or area of destination"].apply(clean_country_name)
df_filtered["Region, development group, country or area of origin"] = df_filtered["Region, development group, country or area of origin"].apply(clean_country_name)
print(len(df_filtered))
print(df_filtered.columns.tolist())
a = 2024
year_cols = [col for col in df_filtered.columns if(col == 2024) or col in [
    "Index",
    "Region, development group, country or area of destination",
    "Coverage",
    "Data type",
    "Location code of destination",
    "Region, development group, country or area of origin",
    "Location code of origin"
]]

df_clean = df_filtered[year_cols]
print(len(df_clean.columns))
df_clean.columns = [
    "Index", "Origin", "Unknown1", "DataType", "OriginCode",
    "Destination", "DestinationCode",
    "2024"
]


df_clean.to_csv("migration_data_countries_only.csv", index=False, header=True)
