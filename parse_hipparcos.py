import csv
from collections import OrderedDict

HIPPARCOS_PATH = 'data/hipparcos.dat'
HIPPARCOS_DELIM = '|'
VISIBLE_STAR_MAG = 7.0
VISIBLE_STAR_PATH = 'data/hipparcos_visible.csv'
FIELDS = OrderedDict([
    ['hip_id', 1],
    ['vmag', 5],
    ['spec_type', 76],
    ['dec_deg', 9],
    ['ra_deg', 8],
    ['dec_dms', 4],
    ['ra_hms', 3],
])

def visible_stars():
    visible = []
    with open(HIPPARCOS_PATH) as f:
        for line in f:
            data = [val.strip() for val in line.split(HIPPARCOS_DELIM)]

            try:
                vmag = float(data[5])
            except ValueError:
                continue

            if vmag < VISIBLE_STAR_MAG:
                visible.append(data)

    return visible

def write_visible_stars():
    visible = visible_stars()

    with open(VISIBLE_STAR_PATH, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS.keys())
        writer.writeheader()
        for star in visible:
            writer.writerow({k: star[idx] for k, idx in FIELDS.items()})
