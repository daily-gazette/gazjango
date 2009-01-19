import math

# is this logically data that should therefore belong in the database? yes.
# would doing this with models require a lot less ugliness? yes.
# is it a model in the database? no.
# why not? because (a) it won't change often
#                  (b) it clutters up the admin just that much more for superusers
#                  (c) I already did the reimplementing :p

TRAIN_STATIONS = dict( (a[0], {'id': a[0], 'name': a[1], 'lat': a[2], 'lng': a[3]}) for a in [
    ( 1, "R3: Market East",        "39.952076", "-75.156612"),
    ( 2, "R3: Suburban Station",   "39.95205",  "-75.174664"),
    ( 3, "R3: 30th St",            "39.954833", "-75.183411"),
    ( 4, "R3: University City",    "39.948849", "-75.189646"),
    ( 5, "R3: 49th St",            "39.943731", "-75.21663"),
    ( 6, "R3: Angora",             "39.944753", "-75.238752"),
    ( 7, "R3: Fernwood-Yeadon",    "39.939611", "-75.256358"),
    ( 8, "R3: Lansdowne",          "39.937127", "-75.272065"),
    ( 9, "R3: Gladstone",          "39.932627", "-75.282311"),
    (10, "R3: Clifton Aldan",      "39.926251", "-75.290669"),
    (11, "R3: Primos",             "39.921495", "-75.298727"),
    (12, "R3: Secane",             "39.915464", "-75.310271"),
    (13, "R3: Morton",             "39.908197", "-75.32734"),
    (14, "R3: Swarthmore",         "39.902239", "-75.350654"),
    (15, "R3: Wallingford",        "39.903572", "-75.371747"),
    (16, "R3: Moylan-Rose Valley", "39.904988", "-75.388452"),
    (17, "R3: Media",              "39.913834", "-75.393999"),
    (18, "R3: Elwyn",              "39.905448", "-75.415499"),
])
TRAIN_CHOICES = [(station['id'], station['name']) for station in TRAIN_STATIONS.values()]

def nearest_station(lat, lng):
    point = (float(lat), float(lng))
    return min(TRAIN_STATIONS.values(),
               key=lambda s: distance_squared(point, (float(s['lat']), float(s['lng']))))

# we can't use distance, because things that are real close to a station return NaN,
# which doesn't compare properly
def distance_squared(point1, point2):
    if len(point1) != len(point2):
        raise AttributeError("can't get distance between different-dimensional points")
    return sum((point2[i] - point1[i]) ** 2 for i in range(len(point1)))
