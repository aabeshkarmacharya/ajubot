import re

from coc_scraper import get_buildings, get_troops, match_name, get_cost


def describe_coc_scraper():
    def should_get_buildings():
        to_test = get_buildings

        assert callable(to_test)
        buildings = to_test()

        assert len(buildings) >= 43

        assert "Cannon" in buildings.keys()
        assert buildings["Cannon"] == "https://clashofclans.fandom.com/wiki/Cannon/Home_Village"

        assert "Royal Champion Altar" in buildings.keys()
        assert buildings["Royal Champion Altar"] == "https://clashofclans.fandom.com/wiki/Royal_Champion_Altar"

        assert None not in buildings.keys()
        assert None not in buildings.values()

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'  # domain...
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        for building_name, building_url in buildings.items():
            assert building_name
            assert re.match(regex, building_url) is not None

    def should_be_troops():
        to_test = get_troops

        assert callable(to_test)
        troops = to_test()

        assert len(troops) >= 61

        assert "Barbarian" in troops.keys()
        assert troops["Barbarian"] == "https://clashofclans.fandom.com/wiki/Barbarian"

        assert "Log Launcher" in troops.keys()
        assert troops["Log Launcher"] == "https://clashofclans.fandom.com/wiki/Log_Launcher"

        assert None not in troops.keys()
        assert None not in troops.values()

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'  # domain...
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        for troop_name, troop_url in troops.items():
            assert troop_name
            assert re.match(regex, troop_url) is not None

    def should_match_name():
        to_test = match_name
        assert callable(to_test)

        matched_name = match_name("Barbarian", ["barbie", "Barbed wire", "barbarian", "barbarian king"])
        assert isinstance(matched_name, str)

        assert matched_name == "barbarian"

        matched_name = match_name("Barcher", ["barbie", "Barbed wire", "barbarian", "barbarian king"])

        assert matched_name is None

    def should_get_cost():
        to_test = get_cost
        assert callable(to_test)

        headers, rows = to_test("https://clashofclans.fandom.com/wiki/Town_Hall")
        assert len(headers) >= 7

        for table_header in ['TH Level', 'Hitpoints', 'Build Cost', 'Build Time', 'Experience Gained',
                             'Maximum Number ofBuildings Available*', 'Maximum Number ofTraps Available']:
            assert table_header in headers
