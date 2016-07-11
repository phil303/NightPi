import csv
import math
from datetime import datetime

from parse_hipparcos import VISIBLE_STAR_PATH

J2000 = datetime(year=2000, month=1, day=1, hour=12)
JDAY_IN_SECONDs = 3600 * 24

MILLBRAE = (37.5985, 237.612)

def greenwich_sidereal_time():
    """ Returns the greenwich mean sidereal time in degrees.

    Algorithm for calculating GMST from:
    http://www2.arnes.si/~gljsentvid10/sidereal.htm
    """

    utc_now = datetime.utcnow()
    seconds_since_J2000 = (utc_now - J2000).total_seconds()
    days_since_J2000 = seconds_since_J2000 / JDAY_IN_SECONDs
    return (280.46061837 + 360.98564736629 * days_since_J2000) % 360

def local_sidereal_time(local_lng_eastward):
    """ Returns the local mean sidereal time in degrees.

    Website for sanity check:
    http://tycho.usno.navy.mil/sidereal.html
    """
    return (greenwich_sidereal_time() + local_lng_eastward) % 360

def _range_lng(lng):
    MIN = 0
    MAX = 360

    start_lng = lng - 90
    end_lng = lng + 90

    if start_lng < MIN:
        start_lng = MAX + start_lng

    if end_lng > MAX:
        end_lng = end_lng - MAX

    return [start_lng, end_lng]

def _range_lat(lat):
    MIN = -90
    MAX = 90

    start_lat = lat - 90
    end_lat = lat + 90

    if start_lat < MIN:
        start_lat = MIN + lat

    if end_lat > MAX:
        end_lat = MAX - lat

    return [start_lat, end_lat]

def _in_ra_range(coord, _range):
    # handle the case where the range value carried over:
    # ex: 320° +-90° is a range of [230, 50] since 410 exceeds 360 by 50
    if _range[0] > _range[1]:
        return coord > _range[0] or coord < _range[1]

    return _range[0] < coord < _range[1]

def _in_dec_range(coord, _range):
    # TODO
    pass


def current_night_sky(lat, lng):
    lmst = local_sidereal_time(lng)

    range_ra = _range_lng(lng)
    range_dec = _range_lat(lmst)

    in_night_sky = []
    with open(VISIBLE_STAR_PATH) as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                star_ra = float(row['ra_deg'])
                star_dec = float(row['dec_deg'])
            except ValueError:
                continue

            if _in_ra_range(star_ra, range_ra) and _in_dec_range(star_dec, range_dec):
                in_night_sky.append(row)

    return in_night_sky
