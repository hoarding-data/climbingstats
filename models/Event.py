import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

from .Athlete import *

class Event:
    """ Object storing event data."""

    def boulder_results(self):
        
        result = {}
        for sex in ["Men", "Women"]:
            
            discipline = self.results["BOULDER " + sex]
            
            stages = {}
            for stage in ["Qualification", "Semi-final", "Final"]:
                if stage not in discipline:
                    continue
                boulders = discipline[stage].apply(lambda x: Athlete.parse_tops(x, none_to_zeros=False)).dropna().to_list()
                boulders = pd.DataFrame(boulders, columns=["tops","zones", "top_attempts","zone_attempts"], index=discipline.name[:len(boulders)])
                stages[stage] = boulders
            
            result[sex] = stages
        
        return result
    
    def lead_results(self):
        
        result = {}
        for sex in ["Men", "Women"]:
            
            discipline = self.results["LEAD " + sex]
            
            stages = {}
            for stage in ["Qualification", "Semi-final", "Final"]:
                if stage not in discipline:
                    continue
                lead_climbs = discipline[stage].apply(lambda x: Athlete.parse_tops(x, none_to_zeros=False)).dropna().to_list()
                lead_climbs = pd.DataFrame(lead_climbs, columns=["tops","zones", "top_attempts","zone_attempts"], index=discipline.name[:len(lead_climbs)])
                stages[stage] = lead_climbs
            
            result[sex] = stages
        
        return result
    
    @staticmethod
    def from_dict(event_dict: dict):
        
        event = Event()
        for key in list(event_dict.keys())[:-1]:
            event.__dict__[key] = event_dict[key]
        
        event.results = {}
        for category in event.categories:

            #TODO: fix boulder and lead format
            if "BOULDER&LEAD" in category: continue;
            print(category)
            if 'BOULDER ' in category:
                event.results[category] = Event._parse_boulder_scores(event_dict['results'][category])
            elif 'LEAD ' in category:
                event.results[category] = Event._parse_lead_scores(event_dict['results'][category])
        
        return event
    
    #Count flashes counts by checking top = true and top_tries = 1
    @staticmethod
    def _count_boulder_flashes(ascents: dict) -> int:
        
        if ascents is np.nan:
            return 0
        
        ascents = pd.json_normalize(ascents)
        return sum((ascents.top == True) & (ascents.top_tries == 1))

    @staticmethod
    def _parse_boulder_rounds(rounds: dict, round_num=3) -> list:
        
        rounds  = pd.json_normalize(rounds)
        flashes = rounds.ascents.apply(Event._count_boulder_flashes)
        flashes = str(flashes.to_list())[1:-1].replace(',','')
        scores = rounds["score"].to_list()
        scores += [None] * (round_num - len(scores))
        starting_group = rounds.loc[0,"starting_group"][-1]  if "starting_group" in rounds.columns else ' '
        
        return scores + [flashes, starting_group]
    
    @staticmethod
    def _parse_boulder_scores(rankings: dict) -> pd.DataFrame:
        
        df = pd.json_normalize(rankings)
        df["name"] = (df["firstname"] + ' ' +  df["lastname"]).str.title()
        #rounds are qualification, semis, finals etc
        round_names = [entry["round_name"].capitalize() for entry in df.loc[0,"rounds"]]
        scores = pd.DataFrame(df.rounds.apply(lambda x: Event._parse_boulder_rounds(x, len(round_names))).to_list(), columns=round_names+["flashes", "starting_group"])
        return pd.concat([df[["rank","name","athlete_id", "country"]], scores], axis=1)
    
    #Count tops by checking top = true
    @staticmethod
    def _count_lead_tops(ascents: dict) -> int:

        if ascents is np.nan:
            return 0
        
        ascents = pd.json_normalize(ascents)
        return sum((ascents.top == True))
    
    @staticmethod
    def _parse_lead_rounds(rounds: dict, round_num=3) -> list:
        
        rounds  = pd.json_normalize(rounds)
        tops = rounds.ascents.apply(Event._count_lead_tops)
        tops = str(tops.to_list())[1:-1].replace(',','')
        scores = rounds["score"].to_list()
        scores += [None] * (round_num - len(scores))
        starting_group = rounds.loc[0,"starting_group"][-1]  if "starting_group" in rounds.columns else ' '
        
        return scores + [tops, starting_group]
    
    @staticmethod
    def _parse_lead_scores(rankings: dict) -> pd.DataFrame:
        
        df = pd.json_normalize(rankings)
        df["name"] = (df["firstname"] + ' ' +  df["lastname"]).str.title()

        #rounds are qualification, semis, finals etc
        round_names = [entry["round_name"].capitalize() for entry in df.loc[0,"rounds"]]

        # print(df)
        scores = pd.DataFrame(df.rounds.apply(lambda x: Event._parse_lead_rounds(x, len(round_names))).to_list(), columns=round_names+["tops", "starting_group"])
        return pd.concat([df[["rank","name","athlete_id", "country"]], scores], axis=1)
    
    @staticmethod
    def _get_ranking(results):
    
        results = results["rank"].fillna(0).astype(int)
        counts = results.value_counts().sort_index().to_dict()
        return results.apply(lambda place: Event._calculate_ranking(place, counts))
    
    @staticmethod
    def _calculate_ranking(place, counts):

        count = counts[place]
        return np.floor(100*sum(Athlete.RANKING[place:place+count])/count)/100
