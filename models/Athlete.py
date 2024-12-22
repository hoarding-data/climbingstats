import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

class Athlete:
    """ Object storing athlete data."""
    
    RANKING = [0, 1000, 805, 690, 610, 545, 495, 455, 415, 380, 350, 325, 300, 280, 260, 240, 220, 205, 185, 170, 155, 145, 130, 120, 105, 95, 84, 73, 63, 56, 48, 42, 37, 33, 30, 27, 24, 21, 19, 17, 15, 14, 13, 12, 11, 11, 10, 9, 9, 8, 8, 7, 7, 7, 6, 6, 6, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1]
    
    def __init__(self, name, sex, country, ifsc_id):
        
        self.name = name
        self.sex = sex[0].capitalize()
        self.country = country
        self.id = ifsc_id
        self.height = np.nan
        
        self.events = {"BOULDER": 0, "LEAD": 0}
        self._ranking_points = {"BOULDER": 0, "LEAD": 0}
        
        self._gold = {"BOULDER": 0, "LEAD": 0}
        self._silver = {"BOULDER": 0, "LEAD": 0}
        self._bronze = {"BOULDER": 0, "LEAD": 0}
        
        self._semis_B = 0
        self._finals_B = 0

        self._top_array = np.zeros(4, dtype=np.int64)
        self._rounds_B = 0
        self._boulders_attempted = 0
        
        self._maxtops = 0
        self._maxzones = 0
        
    def __repr__(self):
        
        printout = self.name + '\n' + str(self._ranking_points)
        printout += f'  Boulder: {self._gold["BOULDER"]} gold, {self._silver["BOULDER"]} silver, {self._bronze["BOULDER"]} bronze'
        
        return printout
    
    @property
    def url(self):
        return f"https://www.ifsc-climbing.org/index.php?option=com_ifsc&task=athlete.display&id={self.id}"

    def _update_boulder(self, entry):
        
        self.events["BOULDER"] += 1
        
        if entry["rank"] == 1:
            self._gold["BOULDER"] += 1
        elif entry["rank"] == 2:
            self._silver["BOULDER"] += 1
        elif entry["rank"] == 3:
            self._bronze["BOULDER"] += 1
        
        self._ranking_points["BOULDER"] += entry['points']
        
        score = np.zeros(4, dtype=np.int32)
        i = entry.index.get_loc("country") + 1
        for stage in entry.index[i:-3]:
            
            if entry[stage]:
                
                self._rounds_B += 1
                if stage == "Semi-final":
                    self._semis_B += 1
                elif stage == "Final" :
                    self._finals_B += 1
                self._boulders_attempted += 5 if stage == "Qualification" else 4

            score += Athlete.parse_tops(entry[stage])
            
        self._top_array += score
    
    def datarow(self):

        return pd.DataFrame({
            "name": [self.name],
            "country": [self.country],
            "id": [self.id],
            "height": [self.height],
            "ranking_B": [self._ranking_points["BOULDER"]],
            "events_B": [self.events["BOULDER"]],
            "rounds_B": [self._rounds_B],
            "semis_B": [self._semis_B],
            "finals_B": [self._finals_B],
            "gold_B":[self._gold["BOULDER"]],
            "silver_B": [self._silver["BOULDER"]],
            "bronze_B": [self._bronze["BOULDER"]],
            "tops": [self._top_array[0]],
            "zones": [self._top_array[1]],
            "top_attempts": [self._top_array[2]],
            "zone_attempts": [self._top_array[3]],
            "boulders_attempted": [self._boulders_attempted],
        })
    
    @property
    def data(self):
        return self.datarow()

    @staticmethod
    def parse_tops(item, none_to_zeros=True):
        
        if item is np.nan or item is None or item == "DNS":
            return np.zeros(4,dtype=np.int32) if none_to_zeros else None
        
        score = item.split()
        
        if len(score) == 3:
            
            tops = int(score[0][0])
            zones = int(score[0][2])
            top_attempts = int(score[1])
            zone_attempts = int(score[2])
            
        elif len(score) == 2:
            tops, zones = score
            tops, top_attempts = tops.split('t')
            zones, zone_attempts = zones.split('b')
            tops, zones = int(tops), int(zones)
            top_attempts = int(top_attempts) if top_attempts else 0
            zone_attempts = int(zone_attempts) if zone_attempts else 0
        else:
            raise ValueError(f"Unrecognizable score {item}")
        
        return np.array([tops, zones, top_attempts, zone_attempts])
