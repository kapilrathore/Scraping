from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

import pandas as pd


def is_beer_entry(table_row):
    row_cells = table_row.findAll("td")
    beer_id = get_beer_id(row_cells[0].text)
    return (len(row_cells) == 8 and beer_id)


def get_beer_id(cell_value):
    r = re.match("^(\d{1,4})\.$", cell_value)
    if r and len(r.groups()) == 1:
        beer_id = r.group(1)
        return int(beer_id)
    else:
        return None


def get_all_beers(html_soup):
    beers_list = []
    all_rows_in_html_page = html_soup.findAll("tr")
    for table_row in all_rows_in_html_page:
        if is_beer_entry(table_row):
            row_cells = table_row.findAll("td")
            beer_entry = {
                "id": get_beer_id(row_cells[0].text),
                "name": row_cells[1].text,
                "brewery_name": row_cells[2].text,
                "brewery_location": row_cells[3].text,
                "style": row_cells[4].text,
                "size": row_cells[5].text,
                "abv": row_cells[6].text,
                "ibu": row_cells[7].text
            }
            beers_list.append(beer_entry)
    return beers_list

html = urlopen("http://craftcans.com/db.php?search=all&sort=beerid&ord=desc&view=text")
html_soup = BeautifulSoup(html, 'html.parser')
beers_list = get_all_beers(html_soup)
print(beers_list)
df = pd.DataFrame(beers_list)
print(df.head(5))

breweries = df[["brewery_location", "brewery_name"]]
breweries = breweries.drop_duplicates().reset_index(drop=True)
breweries["id"] = breweries.index
print(breweries.head(5))

print(breweries.head(5).to_html())

beers = pd.merge(df,
                 breweries,
                 left_on=["brewery_name", "brewery_location"],
                 right_on=["brewery_name", "brewery_location"],
                 sort=True,
                 suffixes=('_beer', '_brewery'))
beers = beers[["abv", "ibu", "id_beer",
               "name", "size", "style", "id_brewery"]]
beers_columns_rename = {
    "id_beer": "id",
    "id_brewery": "brewery_id"
}
beers.rename(inplace=True, columns=beers_columns_rename)
print(beers.head(5))

breweries["city"] = breweries["brewery_location"].apply(
    lambda location: location.split(",")[0])
breweries["state"] = breweries["brewery_location"].apply(
    lambda location: location.split(",")[1])
breweries = breweries[["brewery_name", "city", "state", "id"]]
breweries.rename(inplace=True, columns={"brewery_name": "name"})
print(breweries.head(5))

print(breweries.head(5).to_html())


def string_pct_to_float(value):
    stripped_pct = str(value).strip('%')
    try:
        return float(stripped_pct)/100
    except ValueError:
        return None

beers["abv"] = beers["abv"].apply(string_pct_to_float)

print(beers.head(5))

for possible_value in set(beers["size"].tolist()):
    print(possible_value)


def extract_ounces(value):
    stripped = value.strip("oz")
    match = re.match("(\d{1,2}\.*\d*)", value)
    if match:
        return float(match.group(0))
    else:
        return None

beers["ounces"] = beers["size"].apply(extract_ounces)
del beers["size"]
print(beers.head(5))

print(beers.head(5).to_html())

beers.to_csv("./data/beers.csv")
breweries.to_csv("./data/breweries.csv")

print(beers.head(10))
print(breweries.head(10))