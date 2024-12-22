from tqdm.auto import tqdm
import json
import re
import pandas as pd
pd.options.mode.chained_assignment = None

from .AthleteDict import *
from .Athlete import *
from .Event import *

class EventDict(dict):
    """ Dictionary storing event objects."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_athlete_data(self, years='all', heights=True):
        
        if years == 'all':
            years = self.keys()
        elif isinstance(years, int):
            years = [years]
        athletes = AthleteDict()
        
        athletes.years = years
        for year in years:
            
            events = self[year]
            for event in events:

                categories = event.results.keys()
                for category in categories:
                    
                    discipline, sex = category.split()
                    if isinstance(event.results[category], str):
                        continue
                        
                    results = event.results[category]
                    results["points"] = Event._get_ranking(results)
                    for athlete in results.iloc:
                        
                        name = athlete["name"]
                        if name not in athletes:
                            athletes[name] = Athlete(name, sex, athlete["country"], athlete["athlete_id"])
                        
                        if discipline == "BOULDER":
                            athletes[name]._update_boulder(athlete)
        
        if heights:
            athletes.get_heights()
        
        return athletes

    def get_athlete_results(self, name: str, drop: bool=True):
        """ Get results for a single athlete """
        
        
        lst = []
        for year in self:
            for event in self[year]:
                
                if not "BOULDER Men" in event.results:
                    continue
                
                for sex in ["Men", "Women"]:
                    results = event.results["BOULDER " + sex]
                    entry = results[results.name == name]
                    entry.insert(0,"year", year)
                    entry.insert(1,"event",event.name)
                    if not entry.empty:
                        lst.append(entry)

        df = pd.concat(lst)
        
        if drop:            
            df = df.drop(columns=["name","athlete_id", "country"])
        
        
        return df.reset_index(drop=True)
        
    @staticmethod
    def read_json(filename, period='all', printout=True, progress=True):

        result = EventDict()

        if period == 'all':
            years = [int(year) for year in data.keys()]
        elif isinstance(period, int):
            progress = False
            years = [period]
        elif len(period) == 2:
            # print(period)
            years = list(reversed(range(min(period), max(period)+1)))
            # print(years)
        else:
            raise ValueError(f"Unsupported value {period} for period.")
        
        if printout:
            print("Importing data...")
        
        with open(filename, 'r') as f:
            data = json.load(f)
            EventDict.normalize_data(data,years)
        
        if printout:
            print("Processing...")
        
        result.years = years
        
        if progress:
            pbar = tqdm(range(len(years)))
        for year in years:
            
            if printout:
                print(f"  {year}")
            
            result[year] = []
            for event in data[str(year)]['events'].values():
                
                if printout:
                    print(f"    {event['name']}")
                result[year].append(Event.from_dict(event))
        
            if progress:
                pbar.update(1)

        return result

    @staticmethod
    def normalize_data(data, years):
        """ 
        API returns different structure of data for different years. This function standardizes some of the inconsistencies.
             - Prior to 2020 boulder results had 'speed_elimination_stages' dict inside which boulder ascent data was. From 2020 there is just an 'ascents' dict,
             - Prior to 2020 lead results also had this and the ascents dict. The scores, particularly qualification, needed to also be parsed to add to the ascents. Also "Top" becomes "TOP"
        """
    
        for year, season_data in data.items():
            if year not in years: continue;
            for event, event_data in season_data['events'].items():    
                for category, rankings in event_data['results'].items():
                    #TODO: fix category to use regex
                    if 'BOULDER ' in category:

                        for athlete_data in rankings:
                            for round_data in athlete_data['rounds']:

                                if 'speed_elimination_stages' in round_data:

                                    try:
                                        if round_data['speed_elimination_stages'] != []:
                                            round_data['ascents'] = round_data['speed_elimination_stages']['ascents']
                                        del round_data['speed_elimination_stages']
                                    except Exception as e:
                                        # print(year, event, category)
                                        # print(round_data)
                                        raise Exception(e)
                    if 'LEAD ' in category:

                        for athlete_data in rankings:
                            #print(athlete_data["firstname"], athlete_data["lastname"])
                            for round_data in athlete_data['rounds']:
                                # {
                                #     "category_round_id": 5504,
                                #     "round_name": "Qualification",
                                #     "score": "17+ 58.  |  Top 1. [15.26]",
                                #     "speed_elimination_stages": []
                                # },
                                # {
                                #     "category_round_id": 5506,
                                #     "round_name": "Final",
                                #     "score": "Top",
                                #     "speed_elimination_stages": []
                                # }
                                #use speed_elimination_stages as proxy to determine what year.
                                if 'speed_elimination_stages' in round_data:

                                    try:
                                        if round_data['speed_elimination_stages'] != []:
                                            round_data['ascents'] = round_data['speed_elimination_stages']['ascents']
                                        del round_data['speed_elimination_stages']
                                    except Exception as e:
                                        # print(year, event, category)
                                        # print(round_data)
                                        raise Exception(e)

                                    
                                    if round_data.get("ascents")==None:
                                        round_data["ascents"] = []

                                    if round_data["round_name"] == "Qualification":
                                        #matches the double qualifier route format
                                        #group 1= q1 score, group 4= rank
                                        #group 5= q2 score, group 8= rank
                                        #group 9= adjusted/total score
                                        double_qualifier_regex_match = re.match(r'(([\d+\+\.]+)|(Top))\s+(\d*)\.*\s*\|\s+ (([\d+\+\.]+)|(Top))\s+(\d*)\.*\s*\[([\d\.]+)\]',round_data["score"])

                                        single_qualifier_regex_match = re.match(r'(([\d+\+\.]+)|(Top))\s+(\d*)\.*\s*\[([\d\.]+)\]',round_data["score"])

                                        just_score_regex_match = re.match(r'(([\d+\+\.]+)|(Top))\s*',round_data["score"])

                                        if double_qualifier_regex_match != None:
                                        
                                            round_data["ascents"].append(
                                                {
                                                    "route_id": None,
                                                    "route_name": "1",
                                                    "top": double_qualifier_regex_match.group(1).upper()=="TOP",
                                                    "plus": double_qualifier_regex_match.group(1)[-1]=="+",
                                                    "rank": double_qualifier_regex_match.group(4),
                                                    "corrective_rank": None,
                                                    "score": double_qualifier_regex_match.group(1).upper()
                                                }
                                            )
                                            round_data["ascents"].append(
                                                {
                                                    "route_id": None,
                                                    "route_name": "2",
                                                    "top": double_qualifier_regex_match.group(5).upper()=="TOP",
                                                    "plus": double_qualifier_regex_match.group(5)[-1]=="+",
                                                    "rank": double_qualifier_regex_match.group(8),
                                                    "corrective_rank": None,
                                                    "score": double_qualifier_regex_match.group(5).upper()
                                                }
                                            )
                                            #extract the combined qualifier score
                                            round_data["score"]=double_qualifier_regex_match.group(9)
                                        elif single_qualifier_regex_match != None:
                                            round_data["ascents"].append(
                                                {
                                                    "route_id": None,
                                                    "route_name": "1",
                                                    "top": single_qualifier_regex_match.group(1).upper()=="TOP",
                                                    "plus": single_qualifier_regex_match.group(1)[-1]=="+",
                                                    "rank": single_qualifier_regex_match.group(4),
                                                    "corrective_rank": None,
                                                    "score": single_qualifier_regex_match.group(1).upper()
                                                }
                                            )
                                            round_data["score"]=single_qualifier_regex_match.group(5)
                                        elif(just_score_regex_match != None):
                                            #because 2012 world championships
                                            round_data["ascents"].append(
                                                {
                                                    "route_id": None,
                                                    "route_name": "1",
                                                    "top": None,
                                                    "plus": None,
                                                    "rank": None,
                                                    "corrective_rank": None,
                                                    "score": round_data["score"].strip().upper()
                                                }
                                            )
                                            round_data["score"] =round_data["score"].strip().upper()
                                        else:
                                            # print(year, event, category)
                                            # print(round_data)
                                            raise Exception("Lead Qualifier regex did  not match please check format")
                                    #else semis or finals only has one score
                                    else:
                                        round_data["ascents"].append(
                                            {
                                            "route_id": None,
                                            #always 1
                                            "route_name": "1",
                                            "top": round_data["score"].upper()=="TOP",
                                            "score": round_data["score"].upper(),
                                            "plus": round_data["score"][-1]=="+",
                                            "restarted": None,
                                            "time_ms": None,
                                            "modified": None,
                                            "status": None
                                            }
                                        )
                                        
