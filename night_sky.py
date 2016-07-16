import csv
from math import pi, radians, degrees, asin, acos, sin, cos
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

    ha = (lst - ra) % CIRCLE_RADS
    altitude = asin(sin(dec) * sin(lat) + cos(dec) * cos(lat) * cos(ha))
    azimuth = acos(
       (sin(dec) - sin(altitude) * sin(lat)) / (cos(altitude) * cos(lat))
    )
    if sin(ha) > 0:
        azimuth = CIRCLE_RADS - azimuth

    return degrees(altitude), degrees(azimuth)


def fetch_stars():
    with open(VISIBLE_STAR_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ra = float(row['ra_deg'])
                dec = float(row['dec_deg'])
            except ValueError:
                continue
            yield (row, ra, dec)


def current_night_sky(location):
    """ Find all visible stars in the sky above.

    Given any location (lat, lng) and assuming we only want stars at the
    current moment, this will find all visible stars (visual magnitude 6.5 and
    below) in the night sky.

    :param location: lat/lng tuple
        - lat: float between -90 and 90
        - lng: float between 0 and 360 going east. In other words, -122.42 degs
               west would become 237.58 (or 360 - 122.42)
    """
    return stars_in_viewport(location, 0, 180, 0, 90)


def stars_in_viewport(location, fov_azimuth, az_range, fov_altitude, alt_range):
    """ Find all visible stars through a given viewport.

    Given a location (lat, lng), field of view angles, and assuming we only
    want stars at the current moment, this will find all visible stars (visual
    magnitude 6.5 and below) that fit into that viewport.

    :param location: lat/lng tuple
        - lat: float between -90 and 90
        - lng: float between 0 and 360 going east. In other words, -122.42 degs
               west would become 237.58 (or 360 - 122.42)
    :param fov_azimuth: the angle the observer is looking at along the azimuth,
        a float between 0 and 360.
    :param az_range: the fov angle visible to the observer, both to the left
        and right of his azimuth angle. A float.
    :param fov_altitude: the angle the observer is looking at along the
        altitude, a float between 0 and 90.
    :param alt_range: the fov angle visible to the observer, both above and
        below his altitude angle. A float.
    """

    lat, lng = location
    lst = local_sidereal_time(lng)
    visible = []

    for star, ra, dec in fetch_stars():
        star_altitude, star_azimuth = get_horizontal_coords((ra, dec), (lst, lat))

        if abs(fov_altitude - star_altitude) < alt_range and star_altitude > 0:
            # we need to handle both the general case and the "exceeding 90
            # degrees altitude" case, where we need to check the azimuths on
            # the other side of the circle since those become valid
            if (abs(fov_azimuth - star_azimuth) < az_range or
                (fov_altitude + star_altitude > 90 and
                 abs((fov_azimuth + 180) % 360 - star_azimuth) < az_range)
               ):
                visible.append(star)

    return visible

def star_data(hip_id, location):
    lat, lng = location
    lst = local_sidereal_time(lng)
    for s, ra, dec in fetch_stars():
        if s['hip_id'] == hip_id:
            return (s, get_horizontal_coords((ra, dec), (lst, lat)))
