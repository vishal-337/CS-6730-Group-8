import pandas as pd
import os
import pycountry

def get_iso2(iso3_code):
    """Safely converts an ISO 3166-1 alpha-3 code to alpha-2."""
    try:
        country = pycountry.countries.get(alpha_3=iso3_code)
        return country.alpha_2 if country else None
    except (LookupError, AttributeError):
        # Handle cases where the code is invalid or not found
        # print(f"Warning: Could not find ISO2 code for {iso3_code}") # Optional warning
        return None

def aggregate_trade_data(input_csv_path, output_csv_path):
    """
    Reads a trade data CSV, converts ISO3 to ISO2 codes, aggregates exports
    by origin (iso2_o) and destination (iso2_d), and writes the result to a new CSV.

    Args:
        input_csv_path (str): Path to the input CSV file.
        output_csv_path (str): Path for the output aggregated CSV file.
    """
    try:
        if not os.path.exists(input_csv_path):
            print(f"Error: Input file not found at {input_csv_path}")
            return

        df = pd.read_csv(input_csv_path)

        required_columns = ['iso3_o', 'iso3_d', 'export']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: Input CSV must contain columns: {', '.join(required_columns)}")
            return

        # Convert ISO3 codes to ISO2
        print("Converting ISO3 codes to ISO2...")
        df['iso2_o'] = df['iso3_o'].apply(get_iso2)
        df['iso2_d'] = df['iso3_d'].apply(get_iso2)

        # Drop rows where conversion failed for either origin or destination
        original_rows = len(df)
        df.dropna(subset=['iso2_o', 'iso2_d'], inplace=True)
        dropped_rows = original_rows - len(df)
        if dropped_rows > 0:
            print(f"Dropped {dropped_rows} rows due to failed ISO code conversion.")

        if df.empty:
            print("Error: No valid data remaining after ISO code conversion.")
            return

        # Group by origin (iso2_o) and destination (iso2_d), sum the export values
        print("Aggregating exports by ISO2 codes...")
        aggregated_df = df.groupby(['iso2_o', 'iso2_d'], as_index=False)['export'].sum()

        output_dir = os.path.dirname(output_csv_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        aggregated_df.to_csv(output_csv_path, index=False)
        print(f"Aggregated data successfully written to {output_csv_path}")

    except pd.errors.EmptyDataError:
        print(f"Error: Input file {input_csv_path} is empty.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_path, 'data', 'trade data.csv')
    # Update output filename to reflect ISO2 aggregation
    output_file = os.path.join(base_path, 'data', 'aggregated_trade_data_iso2.csv')

    aggregate_trade_data(input_file, output_file)
