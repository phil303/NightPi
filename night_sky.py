import csv
import math
from enum import Enum
from datetime import datetime

from parse_hipparcos import VISIBLE_STAR_PATH

J2000 = datetime(year=2000, month=1, day=1, hour=12)
JDAY_IN_SECONDs = 3600 * 24

MILLBRAE = (37.5985, 237.612)
HEMI = Enum('Hemisphere', ('northern', 'southern'))

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

def _range_lat(lat):
    MIN = -90
    MAX = 90

    start_lat = lat - 90
    end_lat = lat + 90

    if start_lat < MIN:
        start_lat = MIN + lat

    if end_lat > MAX:
        end_lat = MAX - lat

    hemi = HEMI.southern
    if lat > 0:
        hemi = HEMI.northern

    return [start_lat, end_lat, hemi]

def _in_ra_range(ra, _range):
    # to account for ranges like [210, 30], which we represent as [210, 390],
    # simply add 360 to our right ascension
    start, end = _range
    return start < ra < end or start < ra + 360 < end

def _in_dec_range(dec, _range):
    # handle the "carry over" from going past 90 degrees
    if _range[2] == HEMI.northern:
        return _range[0] < dec < 90 or _range[1] < dec < 90
    else:
        return -90 < dec < _range[1] or _range[0] < dec < -90

def current_night_sky(lat, lng):
    """ Find all visible stars in the sky above.

    Given any latitude and longitude and assuming we only want stars at the
    current moment for that location, this will find all visible stars (visual
    magnitude 7.0 and below) in the night sky.

    :param lat: float between -90 and 90
    :param lng: float between 0 and 360 going east
        In other words, -122.42 degs west would become 237.58 (360 - 122.42)
    """
    lmst = local_sidereal_time(lng)

    range_ra = [lmst - 90, lmst + 90]
    range_dec = _range_lat(lat)

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
