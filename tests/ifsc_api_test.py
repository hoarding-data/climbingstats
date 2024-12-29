import unittest
import ifsc_api

class TestIfscApi(unittest.TestCase):

    def test_fetch_seasons(self):
        # Call the function
        seasons = ifsc_api.fetch_seasons()

        # Assert the response structure
        self.assertIsInstance(seasons, list)
        for season in seasons:
            self.assertIn("name", season)
            self.assertIn("id", season)

    def test_fetch_league_events(self):
        # prerequisite to this function would be getting a league id for a particular season (test_fetch_seasons)

        league_id = 431 #2024, World Cups and World Championships
        
        # Call the function
        events = ifsc_api.fetch_league_events(league_id)

        # Assert the response structure
        self.assertIsInstance(events, list)
        for event in events:
            self.assertIn("event_id", event)
            self.assertIn("event", event)

    def test_fetch_event_details(self):
        # prerequisite to this function would be getting an event id for a particular season + league
        event_id = 1356 # 2024, World Cups and World Championships, Innsbruck
        
        # Call the function
        event_details = ifsc_api.fetch_event_details(event_id)

        # Assert the response structure
        self.assertIsInstance(event_details, dict)
        self.assertIn("name", event_details)
        self.assertIn("d_cats", event_details)
        self.assertIsInstance(event_details["d_cats"], list)

    def test_fetch_category_results(self):
        # prerequisite to this function would be getting a "full_results_url" for a particular event like "LEAD Men" (which includes all rounds)

        full_results_url = "/api/v1/events/1356/result/1" #2024, World Cups and World Championships, Innsbruck, LEAD Men
        
        # Call the function
        ranking = ifsc_api.fetch_category_results(full_results_url)

        # Assert the response structure
        self.assertIsInstance(ranking, list)
        for rank in ranking:
            self.assertIn("rank", rank)
            self.assertIn("name", rank)

if __name__ == '__main__':
    unittest.main()
