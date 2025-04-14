import pandas as pd
import pycountry

filePath = "/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/countries-countries-fb-social-connectedness-index-october-2021 (3).tsv"

df1 = pd.read_csv(filePath, sep="\t")

print(df1.columns.tolist())
print(df1.head())

df = pd.read_csv("/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/migration_data_countries_only.csv")
print(df.columns.tolist())

def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_2
    except LookupError:
        return None
df["Origin_ISO"] = df["Origin"].apply(get_country_code)
df["Destination_ISO"] = df["Destination"].apply(get_country_code)

dfMain = df.merge(df1, left_on=["Origin_ISO", "Destination_ISO"], right_on=["user_loc", "fr_loc"], how="left")
dfMain.to_csv("migration_with_sci_countries.csv", index=False)