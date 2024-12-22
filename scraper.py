import requests, json, sys, time

class Scraper:

    API_BASE_URL = "https://ifsc.results.info"

    headers = {
  'accept': 'application/json',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'cookie': '_verticallife_resultservice_session=zheXgc6%2FjPjG2ebybpMtUVSGf2MGC9PRsY6TIADtdV74TiAm6KU1O2SeiEb4h8C%2BT2mh01k73VytpREwy1%2BDo%2BUR9%2BhVwU2g0Gh%2BqgNsfw%2FafM3ovifIPbU04UEu9n7bIyjgZgLyrtx7ciCm%2F%2FanXK%2BXkZ6482sKp5fvNzPF7JEPNaISsTTLYP5VXZ%2FR4ensulCA8qQfYgagOw6fLSdIPvu0Lvnn%2FCcLVOTWiHYIfOXgY2xhi1q%2F%2BAjrma6NjR02KCs0aDh%2FadRFJY%2FIwI3qafaiUVTI7H5%2BG5uHRyGAv8W%2FW9ohmBiJUUiSxQ%3D%3D--%2FFrvwitJkWGVg%2B9x--xyeTQtV3WYaZ1NAuTLaD5w%3D%3D',
  'pragma': 'no-cache',
  'priority': 'u=1, i',
  'referer': 'https://ifsc.results.info/',
  'sec-ch-ua': '"Brave";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'sec-gpc': '1',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
  'x-csrf-token': 'IGS8KOAFGc5GfBD9EBzxNueSxkBs_VOqGdiHE1AZwtj91HzF-tMOh-JgH_CiO5Z4z9g7juCecEnOVAr8_kiJ2g'
}

    def __init__(self):

        self.data = None

    def get_data(self, period='all') -> None:

        season_info_url = self.API_BASE_URL + '/api/v1'
        seasons = requests.get(season_info_url, headers=self.headers).json()['seasons']
        seasons = {int(season['name']): season for season in seasons}
        
        if period == 'all':
            years = list(seasons.keys())
        elif isinstance(period, int):
            years = [period]
        elif len(period) == 2:
            years = reversed(range(min(period), max(period)+1))
        elif isinstance(period, list) or isinstance(period, tuple):
            years = period
        else:
            raise ValueError(f"Invalid parameter value {period}")
        
        print("Scraping data...\n")
        
        for year in years:
            time.sleep(2)
            print(f"{year}:")
            season = seasons[year]
            league_id = season['leagues'][0]['id'] # pick only World Cup and World Champ data, assumes first entry is always world cups and world championships
            season['leagues'] = 'World Cups and World Championships'
            season['events'] = self.get_season_data(league_id)
        
        self.data = seasons

    def get_season_data(self, league_id: int) -> dict:

        print(f"Scraping...")

        # request event data
        league_info_url = f"{self.API_BASE_URL}/api/v1/season_leagues/{league_id}"
        print(league_info_url)
        events = requests.get(league_info_url,headers=self.headers).json()

        events = events['events']
        
        # get data for each event in season
        event_list = []
        for event in events:
            #event id is its own attribute now
            event_id = event['event_id']

            try:
                print(f" {event['event']}")
                event_data = self.get_event_data(event_id)
            except Exception as e:
                print(e)
                print(f" Could not scrape {event['event']}")
                continue

            event_list.append(event_data)
        
        # append to the season as dict
        event_dict = {}
        locations = [self.get_location(event) for event in event_list]
        counts = dict.fromkeys(locations, 0)
        for event in event_list:
            location = self.get_location(event)

            # check for repeated events in the same location and number them
            if locations.count(location) > 1:
                counts[location] += 1
                location += ' ' + str(counts[location])

            event_dict[location] =  event
        
        return event_dict

    def get_event_data(self, event_id: int) -> dict:
        
        # request category data
        event_info_url = f"{self.API_BASE_URL}/api/v1/events/{event_id}"
        print(event_info_url)
        event = requests.get(event_info_url, headers=self.headers).json()
        
        # scrape data for each category in event
        event['categories'] = []
        event['results'] = {}
        for category in event['d_cats']:
            category_name = category['dcat_name']
            event['categories'].append(category_name)
            print(f"  {category_name}")
            category_results_url = f"{self.API_BASE_URL}{category['full_results_url']}"
            category_results = requests.get(category_results_url, headers=self.headers).json()
            event['results'][category_name] = category_results['ranking']

        del event['d_cats']
        return event

    def get_location(self, event: dict) -> str:
        return ' '.join(event['name'].split('-')[-1].strip().split()[:-2])

    def to_json(self, filename: str='data.json') -> None:

        if not self.data:
            print("No data. Run the get_data(period) method to scrape data.")
            return 
        
        print(f"Saving data to {filename}...")
        with open(filename, 'w+') as f:
            json.dump(self.data, f, indent=4)
        print("Done!")

def usage() -> None:

    print("Usage: 'python scraper.py' to scrape all data.\n       'python scraper.py -p <year>' to scraper a single season.\n       'python scraper.py -p <start_year> <end_year>' to scrape a range of years.")

def main() -> None:

    argv = sys.argv[1:]
    period = 'all'

    if argv:

        if not argv[0][:2] == "-p":
            usage()
            return

        if len(argv) == 2:
            period = int(argv[1])
        elif len(argv) == 3:
            period = [int(year) for year in argv[1:]]
        else:
            usage()
            return

    scraper = Scraper()
    scraper.get_data(period)
    scraper.to_json()

if __name__ == '__main__':

    main()