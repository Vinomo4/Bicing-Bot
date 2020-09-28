import pandas as pd
import networkx as nx
import haversine
from haversine import haversine
import geopy
from geopy import Nominatim
import staticmap
from staticmap import StaticMap, CircleMarker, Line, IconMarker
import random
#import pep8
#-------------------------------------------
#Function that returns the max/min latitude and max/min longitude.
def bbox(G):
    max_lat = min_lat = max_lon = min_lon = 0
    for station in G.nodes:
        if station.lat > max_lat: max_lat = station.lat
        if station.lat < min_lat or min_lat == 0: min_lat = station.lat
        if station.lon > max_lon: max_lon = station.lon
        if station.lon < min_lon or min_lon == 0: min_lon = station.lon
    return max_lat,min_lat,max_lon,min_lon

def locate_on_quad(G,num_cols,num_rows,max_lat,min_lon,dist):
    bcn_matrix = [[[] for i in range(num_cols)]for i in range (num_rows)]
    for station in G.nodes:
        i = int(haversine((max_lat,min_lon),(station.lat,min_lon))//dist)
        j = int(haversine((max_lat,min_lon),(max_lat,station.lon))//dist)
        bcn_matrix[i][j].append(station)
    return bcn_matrix

#Given two cells, checks all the possible connections between the stations on that cells.
def adjacent(G,bcn_matrix,i,j,k,l,dist):
    for st_A in bcn_matrix[i][j]:
        for st_B in bcn_matrix[k][l]:
            d_AB = haversine([st_A.lat, st_A.lon], [st_B.lat, st_B.lon])
            if d_AB <= dist and st_A != st_B: G.add_edge(st_A, st_B, weight = d_AB/10)
    return G

def create_graph(dist):
    #First, we import all the bicing stations info, in panda format.
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')

    dist /= 1000 #Convert distance (given in m) to km.
    G = nx.Graph()
    for station in bicing.itertuples():G.add_node(station)

    max_lat,min_lat,max_lon,min_lon = bbox(G)

    #We determine the number of rows and columns,
    num_rows = int(haversine((max_lat,min_lon),(min_lat,min_lon)) // dist) + 1
    num_cols = int(haversine((max_lat,min_lon),(max_lat,max_lon)) // dist) + 1

    #Function that locates every station in its respective quadrant.
    bcn_matrix = locate_on_quad(G,num_cols,num_rows,max_lat,min_lon,dist)

    #In this loop, we check all the possible connections between stations.
    for i in range (num_rows):
        for j in range(num_cols):
            G = adjacent(G,bcn_matrix,i,j,i,j,dist)
            if i > 0: G = adjacent(G,bcn_matrix,i,j,i-1,j,dist)
            if i > 0 and j + 1 < num_cols:  G = adjacent(G,bcn_matrix,i,j,i-1,j+1,dist)
            if j + 1 < num_cols:  G = adjacent(G,bcn_matrix,i,j,i,j+1,dist)
            if i + 1 < num_rows and j + 1 < num_cols: G = adjacent(G,bcn_matrix,i,j,i+1,j+1,dist)
    return G

#Returns the number of nodes in the current graph.
#Prec: A previous created graph, in nx.graph format, must be provided.
def nodes(G):
    return G.number_of_nodes()
#Returns the number of edges in the current graph.
#Prec: A previous created graph, in nx.graph format, must be provided.
def edges(G):
    return G.number_of_edges()

#Returns the number of conencted components in the current graph.
#Prec: A previous created graph, in nx.graph format, must be provided.
def components(G):
    return nx.number_connected_components(G)

#Returns a .png file, locating all the bicing stations and connections between them.
#Prec: A previous created graph, in nx.graph format, must be provided.
def plotgraph(G,name_file):
    map = StaticMap(750,750)
    for station in G.edges:
        coord1, coord2 = station[0], station[1]
        line= Line([[coord1.lon,coord1.lat],[coord2.lon,coord2.lat]],'#0000FFBB',2)
        map.add_line(line)

    for station in G.nodes:
        marker= CircleMarker([station.lon,station.lat],'red',4)
        marker_outline= CircleMarker([station.lon,station.lat],'black',8)
        map.add_marker(marker_outline)
        map.add_marker(marker)
    image = map.render()
    image.save(name_file)

##### Route-Start #####
#Transforms two given locations in their respective coordinates.
def addressesTOcoordinates(addresses):
    try:
        geolocator = Nominatim(user_agent="bicing_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        return None

#Builds a new graph, using as nodes the coordinates of bicing stations present in the current graph(G).
def create_G_Coord(G, coord_origin, coord_destination):
    G_coord = nx.Graph()
    #In this new graph, the weight of the edges is the time needed to go from one node to another.
    for e in G.edges():
        coord1, coord2, dist = (e[0].lat, e[0].lon), (e[1].lat, e[1].lon), G.edges[e[0], e[1]]['weight']
        G_coord.add_edge(coord1, coord2, weight = dist/10)
    #In this loop, all the added edges are done by foot.
    for node in G.nodes(): #adds edges between origin, destination and the stations
        n_coord = (node.lat, node.lon)
        dist_to_og, dist_to_dest = haversine(coord_origin, n_coord), haversine(coord_destination, n_coord)
        G_coord.add_weighted_edges_from([(coord_origin, n_coord, dist_to_og/4), (coord_destination, n_coord, dist_to_dest/4)])
    G_coord.add_edge(coord_origin, coord_destination, weight = (haversine(coord_origin, coord_destination)/4))
    return G_coord

#Generates the fastest route between to given addresses.
def route(G, name_file, addresses):
    coords = addressesTOcoordinates(addresses)
    coord_origin, coord_destination = coords
    G_coord = create_G_Coord(G, coord_origin, coord_destination)
    #Application of djijstra algorithm with the graph correctly weighted.
    fastest_path = nx.dijkstra_path(G_coord, coord_origin, coord_destination)
    #Creation of the map associated to the route.
    map = StaticMap(750,750)
    for i in range(len(fastest_path)-1):
        coord1, coord2 = fastest_path[i], fastest_path[i+1]
        line = Line([[coord1[1],coord1[0]],[coord2[1],coord2[0]]],'#0000FFBB',4)
        map.add_line(line)
        marker= CircleMarker([coord1[1],coord1[0]],'red',6)
        marker_outline= CircleMarker([coord1[1],coord1[0]],'black',8)
        map.add_marker(marker_outline)
        map.add_marker(marker)
    #Intentar coger el icono de internet y no tenerlo guardado como imagen local.
    dest_marker= IconMarker([coord2[1],coord2[0]],'/home/victor/Documentos/AP2/Exercicis/Bicing/Icons/2344292-24.png',24,24)
    map.add_marker(dest_marker)
    image = map.render()
    image.save(name_file)
##### Route-End #####
