from collections.abc import Iterable
from difflib import get_close_matches
from typing import Sequence, Any, List, Iterator, Sized, Union
from urllib import parse
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
from scrapy import Selector


def get_buildings() -> dict:
    url = 'https://clashofclans.fandom.com/wiki/Buildings'
    response = requests.get(url)
    sel = Selector(text=response.text)
    buildings = {}
    rows = sel.xpath('//table[tbody/tr/th[contains(., "Home Village Buildings")]]/tbody/tr')[1:]
    for row in rows:
        building_type = row.xpath("./td[1]/b/a/text()").get()
        if building_type != "Other Buildings":
            building_elements = row.xpath("./td[2]//a[not(ancestor::b)]")
            for building_element in building_elements:
                building = building_element.xpath("./descendant-or-self::*/text()").get()
                building_link = building_element.xpath("./@href").get()
                buildings[building] = urljoin(url, building_link)
    return buildings


def get_troops():
    url = "https://clashofclans.fandom.com/wiki/Army"
    response = requests.get(url)
    sel = Selector(text=response.text)

    units = {}
    rows = sel.xpath('//table[tbody/tr/th[contains(., "Home Village Army")]]/tbody/tr')[1:]
    for row in rows:
        troops = row.xpath("./td[2]/a/text()").getall()
        troop_links = row.xpath("./td[2]/a/@href").getall()
        for troop, troop_link in zip(troops, troop_links):
            units[troop] = urljoin(url, troop_link)
    return units


def match_name(unit_name: str, values: List[str]):
    close_matches = get_close_matches(unit_name, values)
    matched_key = next(iter(close_matches), None)
    if matched_key:
        return matched_key


def create_table(rows: Sequence[Sequence[Any]]) -> str:
    no_cols = len(max(rows, key=len))
    max_cols = [0] * no_cols
    for row in rows:
        for i, col in enumerate(row):  # type: (int, Any)
            if max_cols[i] < len(col):
                max_cols[i] = len(col)
    table_string = ""
    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            table_string += pad(col, max_cols[j] + 2)
        table_string += "\n"
    return table_string


def to_multi_columns(header: List[str], rows: List[Union[Iterable, Sized]], row_length=120):
    max_combined_length = len("".join(header)) + 2 * len(header)
    for row in rows:
        combined_length = len("".join(row)) + 2 * len(row)
        if combined_length > max_combined_length:
            max_combined_length = combined_length
    number_of_columns = row_length // max_combined_length

    final_headers = header * number_of_columns
    combined_rows = [rows[x:x + number_of_columns] for x in range(0, len(rows), number_of_columns)]
    final_rows = []
    for row in combined_rows:
        final_rows.append([item for group in row for item in group])
    final_rows.insert(0, final_headers)
    final_table = create_table(final_rows)
    return final_table


def chunkify(lst, n):
    """Yield successive n-sized chunkify from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def pad(v: str, length: int):
    pad_amount = length - len(v)
    return v + ' ' * pad_amount


def combine_headers(headers: Iterator, combine_char: str = ">"):
    final_headers = []
    last_header = ""
    for header in headers:
        if header == last_header:
            continue
        final_headers.append(header)
        last_header = header
    return combine_char.join(final_headers)


def get_cost(url):
    response = requests.get(url)
    sel = Selector(text=response.text)

    table = sel.xpath(
        '//table[tbody/tr[1]/th[1][(normalize-space(text())="Level" or normalize-space(text())="TH Level") and not(a) '
        'and not(strong[normalize-space(text())="Town Hall"])] and not(contains(@class, '
        '"mw-collapsible"))]')[
        0].get()
    df = pd.read_html(table)[0]
    df = df.replace(np.nan, 'N/A', regex=True)
    df = df.applymap(str)
    if not isinstance(df.columns[0], str) and isinstance(df.columns[0], Iterable):
        new_columns = []
        for columns in df.columns:
            new_columns.append(combine_headers(columns))
        df.columns = new_columns
    return list(df.columns), df.values.tolist()


def minimize_string(s: str):
    """
    Removes all vowels that is not the first character of word
    :param s:
    :return:
    """
    new_words = []
    for word in s.split():
        new_word = ""
        for c in word:
            if not new_word or c not in "aeiou":
                new_word += c
        new_words.append(new_word)
    return " ".join(new_words)


def get_coc_api_response(token, player_tag):
    response = requests.get(f"https://api.clashofclans.com/v1/players/{parse.quote_plus(player_tag)}", headers={
        "authorization": f"Bearer {token}"
    })
    print(response)
    return response.json()
