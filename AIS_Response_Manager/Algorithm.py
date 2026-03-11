import math

def km_to_lat_deg(km):
    return km / 111.0

def km_to_lon_deg(km, lat):
    return km / (111.0 * math.cos(math.radians(lat)))

def bearing_deg(lat1, lon1, lat2, lon2):
    # convert to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    dLon = math.radians(lon2 - lon1)

    x = math.sin(dLon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2) -
         math.sin(lat1) * math.cos(lat2) * math.cos(dLon))

    bearing = math.degrees(math.atan2(x, y))

    # normalize to 0–360
    return (bearing + 360) % 360

# https://www.geeksforgeeks.org/dsa/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
# ----------------------------------------------------------------------------------------------------
# Python 3 program for the
# haversine formula
def haversine(lat1, lon1, lat2, lon2):
    
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0

    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0

    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) + 
         pow(math.sin(dLon / 2), 2) * 
             math.cos(lat1) * math.cos(lat2));
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return rad * c

def ConvertToX_Y(lat1, lon1, lat2, lon2, debug=False):
    aardstraal = 6371000
    X1 = math.pi * lat1/180
    Y1 = math.pi * lon1/180
    X2 = math.pi * lat2/180
    Y2 = math.pi * lon2/180
    DeltaPhi = X1 - X2
    DeltaL = Y1 - Y2
    average = (X1 + X2) / 2
    Y = DeltaPhi * aardstraal
    X = DeltaL * aardstraal * math.cos(average)
    distance = math.sqrt(X*X+Y*Y)
    mesurements = (X, Y, distance)
    if(debug):
        print(f"X = {X}")
        print(f"Y = {Y}")
        print(f"Afstand = {distance}")
        print(f"return value: {mesurements}")
    
    return mesurements


    

