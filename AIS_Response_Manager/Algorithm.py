import math

def km_to_miles(km):
    return km * 0.621371

def miles_to_km(miles):
    return miles * 1.609344

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

def velocity_vector(speed_knots, heading_deg):
    speed_mps = speed_knots * 0.514444  # knots → m/s
    heading = math.radians(heading_deg)

    vx = speed_mps * math.sin(heading)
    vy = speed_mps * math.cos(heading)

    return vx, vy

def calculate_cpa_tcpa(x1, y1, speed1, heading1, x2, y2, speed2, heading2):
    vx1, vy1 = velocity_vector(speed1, heading1)
    vx2, vy2 = velocity_vector(speed2, heading2)

    rx = x2 - x1
    ry = y2 - y1

    rvx = vx2 - vx1
    rvy = vy2 - vy1

    rv2 = rvx**2 + rvy**2

    if rv2 == 0:
        return None, None

    tcpa = -(rx*rvx + ry*rvy) / rv2

    cpa_x = rx + rvx * tcpa
    cpa_y = ry + rvy * tcpa

    cpa = math.sqrt(cpa_x**2 + cpa_y**2)

    return cpa, tcpa