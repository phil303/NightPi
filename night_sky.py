import csv
from math import pi, radians, asin, acos, sin, cos
from datetime import datetime

from parse_hipparcos import VISIBLE_STAR_PATH

J2000 = datetime(year=2000, month=1, day=1, hour=12)
JDAY_IN_SECONDS = 3600 * 24
CIRCLE_RADS = 2 * pi

MILLBRAE = (37.5985, 237.612)

def greenwich_sidereal_time():
    """ Returns the greenwich mean sidereal time in degrees.

    Algorithm for calculating GMST from:
    http://www2.arnes.si/~gljsentvid10/sidereal.htm
    """

    utc_now = datetime.utcnow()
    seconds_since_J2000 = (utc_now - J2000).total_seconds()
    days_since_J2000 = seconds_since_J2000 / JDAY_IN_SECONDS
    return (280.46061837 + 360.98564736629 * days_since_J2000) % 360


def local_sidereal_time(local_lng_eastward):
    """ Returns the local mean sidereal time in degrees.

    Website for sanity check:
    http://tycho.usno.navy.mil/sidereal.html
    """
    return (greenwich_sidereal_time() + local_lng_eastward) % 360


def get_horizontal_coords(star_coords, observer_coords):
    # the trig expressions expect radians so convert everything first
    ra, dec = [radians(c) for c in star_coords]
    lst, lat = [radians(c) for c in observer_coords]

    ha = abs(lst - ra) % CIRCLE_RADS
    altitude = asin(sin(dec) * sin(lat) + cos(dec) * cos(lat) * cos(ha))
    azimuth = acos(
       (sin(dec) - sin(altitude) * sin(lat)) / (cos(altitude) * cos(lat))
    )
    return altitude, azimuth


def current_night_sky(lat, lng):
    """ Find all visible stars in the sky above.

    Given any latitude and longitude and assuming we only want stars at the
    current moment for that location, this will find all visible stars (visual
    magnitude 6.5 and below) in the night sky.

    :param lat: float between -90 and 90
    :param lng: float between 0 and 360 going east
        In other words, -122.42 degs west would become 237.58 (360 - 122.42)
    """
    lst = local_sidereal_time(lng)

    in_night_sky = []
    with open(VISIBLE_STAR_PATH) as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                ra = float(row['ra_deg'])
                dec = float(row['dec_deg'])
            except ValueError:
                continue

            altitude, azimuth = get_horizontal_coords((ra, dec), (lst, lat))
            if altitude > 0:
                in_night_sky.append(row)

    return in_night_sky
