import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

from .Athlete import *

class AthleteDict(dict):
    """ Dictionary storing athlete objects."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @staticmethod
    def from_list(athlete_list):
        
        if not isinstance(athlete_list[0], Athlete):
            raise Exception("Input must be a list of Athlete objects")
        
        result = AthleteDict()
        for athlete in athlete_list:
            
            result[athlete.name] = athlete
        
        return result

    def get_athletes_by_sex(self, sex='All'):
        """ Separate by sex """
        
        men = []
        women = []
        
        for athlete in self.values():
            if athlete.sex == 'M':
                men.append(athlete)
            elif athlete.sex == "W":
                women.append(athlete)
            else:
                raise Exception(f"Unrecognized sex {athlete.sex}")
        
        men = AthleteDict.from_list(men)
        women = AthleteDict.from_list(women)
        
        result = {"Men": men, "Women": women}
        
        s = sex.capitalize()
        if s == "All":
            return result
        elif s == "M" or s == "Men":
            return result["Men"]
        elif s == "W" or s == "Women":
            return result["Women"]
        else:
            raise Exception(f"Unknown sex {sex}")
    
    def get_stats(self, sex):
    
        #TODO can you check results for [None]?
        athletes = self.get_athletes_by_sex()[sex]
        
        df = pd.DataFrame()
        for athlete in athletes.values():
            df = pd.concat([df,athlete.datarow()], ignore_index=True)
        
        df["top_percentage"] = df["tops"]/df["boulders_attempted"]
        df["ranking_per_event_B"] = np.round(df["ranking_B"]/df["events_B"],2)
        
        if all(df["height"].isna()):
            df.drop(columns="height", inplace=True)
        
        return df.sort_values("ranking_B", ascending=False).reset_index(drop=True)
    
    def get_heights(self, filename='data/heights.json'):

        heights = pd.read_json(filename, orient='split')

        for name, athlete in self.items():

            if any(heights["name"].str.contains(name, regex=False)):
                row = heights[heights.name.str.contains(name)].iloc[0]
                athlete.age = row.age
                athlete.height = row.height
            else:
                athlete.height = np.nan
