import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

from IPython.display import display, HTML
from tqdm.auto import tqdm

import json
import plotly.express as px

from models.EventDict import *

# colors
ifsc_pink = "#e6007e"
ifsc_pink_dark = "#d6006e"
ifsc_blue = "#10bbef"
ifsc_blue_dark = "#10aaef"

# layput tamplate
template = {'margin': dict(l=20, r=20, t=20, b=20)}

def get_event_data(filename='/data/full_data.json', period=(2008,2022)):

    return EventDict.read_json(filename, period=period)

def get_yearly_data(events, period, elite_cutoff=10):
    
    start, end = period
    years = [year for year in range(start,end+1)]
    top_data = pd.DataFrame({"year": years})
    avg_top_perc, elite_top_perc = {"men": [], "women": []}, {"men": [], "women": []}
    
    for year in years:
        
        athletes = events.get_athlete_data(year)
        
        for sex in ["Men", "Women"]:
            
            stats = athletes.get_stats(sex)
            avg_top_perc[sex.lower()].append(stats["top_percentage"].mean())
            elite_top_perc[sex.lower()].append(stats["top_percentage"].sort_values(ascending=False).head(elite_cutoff).mean())
    
    
    for sex in ["men", "women"]:

        top_data[sex+"_avg_top_percentage"] = avg_top_perc[sex]
        top_data[sex+"_elite_top_percentage"] = elite_top_perc[sex]

    return top_data

