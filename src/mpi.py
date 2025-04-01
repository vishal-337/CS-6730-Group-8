#%%



import pandas as pd
import random
random.seed(786)
import plotly.express as px
import pandas as pd
import random
import pandas as pd
import gspread
import time
from gspread.utils import rowcol_to_a1, a1_to_rowcol
from oauth2client.service_account import ServiceAccountCredentials
import json
import streamlit as st

class MessagePassing:
    def __init__(self,mode='log_sci'):
        url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRid61-SbR59I_PjTO3VRYlIWcibSGbe71jVa8EVthBii4uiJS-NvziYfZlyD5BbwV2lPvMRv0Xy8sR/pub?gid=284046834&output=csv'
        self.df = pd.read_csv(url)
        self.countries_input = self.df['user_loc'].unique().tolist()
        self.activations = []

        if mode != 'log_sci':
            self.mode = 'scaled_sci'
        else:
            self.mode = 'log_sci'
        self.max = self.df[self.mode].max()


    def get_timestep_activations(self, selected_country, ts, pp, at):
        countries_input = self.countries_input
        df = self.df
        scaled_sci_map = {(row['user_loc'], row['fr_loc']): row[self.mode]/self.max for _, row in df.iterrows()}
        act_map = {country: 0 for country in countries_input}
        if selected_country in act_map:
            act_map[selected_country] = at
        results = []
        for _ in range(ts):
            new_act_map = act_map.copy()

            for c1 in countries_input:
                if act_map[c1] >= at:
                    continue
                for c2 in countries_input:
                    if c1 == c2 or act_map[c2] < at:
                        continue
                    if random.random() <= pp:
                        scaled_sci = scaled_sci_map.get((c1, c2), 0)
                        if random.random() <= scaled_sci:
                            new_act_map[c1] += 1

            act_map = new_act_map
            result = [min(100 * act_map[c] / at, 100) for c in countries_input]
            results.append(result)

        self.activations = results



@st.cache_data
def mpi_get_data(country, at = 100,ts = 256,pp = 1.):
    mpi = MessagePassing()
    mpi.get_timestep_activations(country, ts, pp, at)
    
    countries = mpi.countries_input
    time_steps = [i for i in range(ts)]
    values = mpi.activations

    records = []
    for i, year in enumerate(time_steps):
        for j, country_code in enumerate(countries):
            row_dict = {
                'country': country_code, 
                'value': min(values[i][j],at),
                'timestep': year
            }
            records.append(row_dict)


    return pd.DataFrame(records)

def mpi_select_status():
    pass

def mpi_run_fig(df, at, delta_t):
    fig = px.choropleth(
            df,
            locations="country",
            locationmode="country names",
            color="value",
            color_continuous_scale="Viridis",
            range_color=(0, at),
            hover_name="country",
            animation_frame="timestep",
            title="Message Passing Choropleth"
        )

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = delta_t
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = delta_t
    return fig

def mpi_select_fig(countries_input):
    fig = px.choropleth(
            locations=countries_input,
            color = [0.5 for _ in range(len(countries_input))],
            locationmode="country names",
            color_continuous_scale="Viridis",
            hover_name=countries_input,
            title="Message Passing Choropleth"
        )
    return fig

#%%

if __name__ == "__main__":
    mpi = MessagePassing()
    mpi.get_timestep_activations("Canada", 100, 1., 100)
    
    import matplotlib.pyplot as plt
    import numpy as np

    arr = np.array(mpi.df['log_sci'].tolist())
    print(arr.mean())
    print(arr.min())
    print(arr.max())
    plt.hist(arr, bins=100)
    plt.show()
    plt.hist(arr/arr.mean(), bins=100)
    plt.show()
    plt.hist(arr/arr.max(), bins=100)
    plt.show()







# %%
