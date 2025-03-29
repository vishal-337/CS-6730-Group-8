#%%



import pandas as pd
import random
random.seed(786)

import pandas as pd
import random
import pandas as pd
import gspread
import time
from gspread.utils import rowcol_to_a1, a1_to_rowcol
from oauth2client.service_account import ServiceAccountCredentials
import json


class MessagePassing:
    def __init__(self):
        url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRid61-SbR59I_PjTO3VRYlIWcibSGbe71jVa8EVthBii4uiJS-NvziYfZlyD5BbwV2lPvMRv0Xy8sR/pub?gid=1949310392&output=csv'
        self.countries_input = pd.read_csv(url).iloc[0].tolist()
        self.df = pd.read_csv(url)
        self.activations = []


    def get_timestep_activations(self, selected_country, ts, pp, at):
        countries_input = self.countries_input
        df = self.df
        scaled_sci_map = {(row['user_loc'], row['fr_loc']): row['log_sci'] for _, row in df.iterrows()}
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






