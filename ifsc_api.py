import requests

#TODO: category_rounds has individual events i think? 
#try "/api/v1/category_rounds/8514/results" which is 2024 innsbruck mens lead qualification

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

def fetch_seasons():
    """Fetch all seasons."""
    season_info_url = f"{API_BASE_URL}/api/v1"
    response = requests.get(season_info_url, headers=headers)
    response.raise_for_status()
    return response.json()['seasons']

def fetch_league_events(league_id):
    """Fetch events for a specific league."""
    league_info_url = f"{API_BASE_URL}/api/v1/season_leagues/{league_id}"
    response = requests.get(league_info_url, headers=headers)
    response.raise_for_status()
    return response.json()['events']

def fetch_event_details(event_id):
    """Fetch details for a specific event."""
    event_info_url = f"{API_BASE_URL}/api/v1/events/{event_id}"
    response = requests.get(event_info_url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_category_results(full_results_url):
    """Fetch results for a specific category."""
    category_results_url = f"{API_BASE_URL}{full_results_url}"
    response = requests.get(category_results_url, headers=headers)
    response.raise_for_status()
    return response.json()['ranking']