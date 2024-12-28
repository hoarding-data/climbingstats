# climbingstats
Climbing competition statistics based on data scraped from the IFSC website. Data from the years 2008-2023 because IFSC started reporting results in terms of tops and zones (bonuses) in 2008. So far only stats bouldering world cups and champs are presented. Lead will be added eventually. You can see the rankings here:

https://stanrusak.github.io/climbingstats/

### Data

The data can be found in the `data` folder. `full_data.zip` contains the full data of IFSC World Cup/World Champs events, including boulder, lead, and speed (in JSON format).

`men_2008-2023.csv` and `women_2008-2023.csv` contain corresponding athlete data. `climbingstats.py` has some helpful data structures for events and athletes. See the [Jupyter notebook](https://github.com/stanrusak/climbingstats/blob/main/bouldering.ipynb) for usage. 

### TODO:

- deal with case sensitivity
- disciplines and sex appear to be constant currently so place those in a config instead of having them hardcoded everywhere
- need to add boulder & lead

### Data considerations:

- The combined disciplines are found in data years 2009, 2011, 2018, 2019, and 2021. However in 2009 and 2011 there is no actual event data/athlete scores.

### Bugs
unicode characters. (not really a bug i guess but maybe find better ways to display or something?)

weird scores:
Adam Ondra
2016 Paris LEAD Men
{'category_round_id': 3902, 'round_name': 'Qualification', 'score': '1. [3.46]', 'ascents': []}
Ievgeniia Kazbekova
2016 Villars LEAD Women
{'category_round_id': 3856, 'round_name': 'Qualification', 'score': '0  |  0 [51.00]', 'ascents': []}
Jakob Schubert
2012 Paris LEAD Men
{'category_round_id': 2119, 'round_name': 'Qualification', 'score': '4.183 ', 'ascents': []}