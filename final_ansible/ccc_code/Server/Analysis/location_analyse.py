from math import cos, sin, asin, sqrt,pi
from Analysis.parameters import all_coordinates

EARTH_REDIUS = 6378.137

all_coordinates ={
    #longtitude,latitude,radius(km)
    'australia':[133.1389,-29.1425,2081],
    'melbourne':[144.9631,-37.8136,100],
    'sydney':[151.2128,-33.8813,100],
    'brisbane':[153.1024,-27.5394,100],
    'adelaide':[138.6444,-34.9328,100],
    'perth':[115.8808,-32.0379,100],
    #'':[]

}
all_city = ['australia','melbourne', 'sydney','brisbane','adelaide','perth']


'''
calculate the distance
'''
def rad(d):
    return d * pi / 180.0
def get_distance( lat1, lon1, lat2, lon2):# 经度1，纬度1，经度2，纬度2 
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = radLat1 - radLat2
    b = rad(lon1) - rad(lon2)
    s = 2 * asin(sqrt(pow(sin(a / 2), 2) + cos(radLat1) * cos(radLat2) * pow(sin(b / 2), 2)))
    s = s * EARTH_REDIUS
    return s


'''
return the city's name by using the coordinate
'''
def get_location(coordinate):
    #coordinate is str
    coordinate_list =coordinate[1:-1].split(',')
    try:
        lo_coordinate1 = float(coordinate_list[0]) #lo
        la_coordinate1 = float(coordinate_list[1]) #la
    except:
        return None

    for each in all_coordinates:
        lo_coordinate2 = float(all_coordinates[each][0])
        la_coordinate2 = float(all_coordinates[each][1])
        distance  = get_distance(la_coordinate1,lo_coordinate1,la_coordinate2,lo_coordinate2)
        if distance <= all_coordinates[each][2]:
            city_name = each

    return city_name

'''
return the city's name by using the coordinate
'''
def get_location_long_la(long,la):
    #coordinate is str
    city_name = ''
    lo_coordinate1 = long #lo
    la_coordinate1 = la #la
    for each in all_coordinates:
        lo_coordinate2 = float(all_coordinates[each][0])
        la_coordinate2 = float(all_coordinates[each][1])
        distance  = get_distance(la_coordinate1,lo_coordinate1,la_coordinate2,lo_coordinate2)
        if distance <= all_coordinates[each][2]:
            city_name = each

    return city_name
