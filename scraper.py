import requests, json, sys, time
import ifsc_api as ifsc

class Scraper:

    def __init__(self):

        self.data = None

    def get_data(self, period='all') -> None:
        """
        Highest level. request from https://ifsc.results.info/api/v1
        """
        seasons = ifsc.fetch_seasons()
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
        
        self.data = {}
        for year in years:
            print(f"{year}:")
            season = seasons[year]
            league_id = season['leagues'][0]['id'] # pick only World Cup and World Champ data, assumes first entry is always world cups and world championships
            season['leagues'] = 'World Cups and World Championships' #this doesn't get used
            season['events'] = self.get_season_data(league_id)
            self.data[year] = season
            self.to_json(year)

    def get_season_data(self, league_id: int) -> dict:

        print(f"Scraping...")

        # request event data for requeseted league
        events = ifsc.fetch_league_events(league_id)
        
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
        event = ifsc.fetch_event_details(event_id)
        
        # scrape data for each category in event
        event['categories'] = []
        event['results'] = {}
        for category in event['d_cats']:
            category_name = category['dcat_name']
            event['categories'].append(category_name)
            print(f"  {category_name}")
            category_results = ifsc.fetch_category_results(category['full_results_url'])
            event['results'][category_name] = category_results['ranking']

        #TODO delete "dcats" also? or was this one getting deleted because of duplication?
        del event['d_cats']
        return event

    def get_location(self, event: dict) -> str:
        return ' '.join(event['name'].split('-')[-1].strip().split()[:-2])

    def to_json(self, year: int) -> None:

        if not self.data or year not in self.data:
            print(f"No data for {year}. Run the get_data(period) method to scrape data.")
            return 
        
        filename = f"data_{year}.json"
        print(f"Saving data for {year} to {filename}...")
        with open(filename, 'w+') as f:
            json.dump(self.data[year], f, indent=4)
        print("Done!")

def usage() -> None:

    print("Usage: 'python scraper.py' to scrape all data.\n       'python scraper.py -p <year>' to scrape a single season.\n       'python scraper.py -p <start_year> <end_year>' to scrape a range of years.")

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

if __name__ == '__main__':

    main()
