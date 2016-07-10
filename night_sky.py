import math
from datetime import datetime

from parse_hipparcos import VISIBLE_STAR_PATH

J2000 = datetime(year=2000, month=1, day=1, hour=12)
JDAY_IN_SECONDs = 3600 * 24
JCENTURY_IN_DAYS = 36525
DEG_PER_HOUR = 15

def greenwich_sidereal_time():
    # algorithm for calculating GMST from:
    # http://www2.arnes.si/~gljsentvid10/sidereal.htm
    utc_now = datetime.utcnow()
    seconds_since_J2000 = (utc_now - J2000).total_seconds()
    days_since_J2000 = seconds_since_J2000 / JDAY_IN_SECONDs
    return 280.46061837 + 360.98564736629 * days_since_J2000

def local_sidereal_time(local_lng_eastward):
    # website for sanity check
    # http://www.jgiesen.de/astro/astroJS/siderealClock/
    gmst = greenwich_sidereal_time() % 360      # degrees
    lmst = (gmst + local_lng_eastward) % 360     # degrees
    return lmst / 15

def current_night_sky():
    with open(VISIBLE_STAR_PATH) as f:
        pass
