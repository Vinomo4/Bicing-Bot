import pandas as pd
import networkx as nx
import haversine
from haversine import haversine
import collections as cl
import geopy
from geopy import Nominatim
import staticmap
from staticmap import StaticMap, CircleMarker, Line
# -------------------------------------------

Pandas = cl.namedtuple('Pandas', 'lat lon')


# Function that returns the max/min latitude and max/min longitude.
def bbox(G):
    max_lat = min_lat = max_lon = min_lon = 0
    for station in G.nodes:
        if station.lat > max_lat:
            max_lat = station.lat
        if station.lat < min_lat or min_lat == 0:
            min_lat = station.lat
        if station.lon > max_lon:
            max_lon = station.lon
        if station.lon < min_lon or min_lon == 0:
            min_lon = station.lon
    return max_lat, min_lat, max_lon, min_lon


# Function that locates every station in its respective quadrant.
def locate_on_quad(G, num_cols, num_rows, max_lat, min_lon, dist):
    bcn_matrix = [[[] for i in range(num_cols)]for i in range(num_rows)]
    for station in G.nodes:
        i = int(haversine((max_lat, min_lon), (station.lat, min_lon))//dist)
        j = int(haversine((max_lat, min_lon), (max_lat, station.lon))//dist)
        bcn_matrix[i][j].append(station)
    return bcn_matrix


# Given two cells, checks all the possible
# connections between the stations on that cells.
def adjacent(G, bcn_matrix, i, j, k, l, dist):
    for st_A in bcn_matrix[i][j]:
        for st_B in bcn_matrix[k][l]:
            d_AB = haversine([st_A.lat, st_A.lon], [st_B.lat, st_B.lon])
            if d_AB <= dist and st_A != st_B:
                G.add_edge(st_A, st_B, weight=d_AB/10)
    return G


def create_graph(dist):
    # First, we import all the bicing stations info, in panda format.
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']
                                       ['stations'], index='station_id')

    dist /= 1000  # Convert distance (given in m) to km.
    G = nx.Graph()
    for station in bicing.itertuples():
        G.add_node(station)

    if dist == 0:
        return G

    max_lat, min_lat, max_lon, min_lon = bbox(G)

    # We determine the number of rows and columns,
    num_rows = int(haversine((max_lat, min_lon),
                             (min_lat, min_lon)) // dist) + 1
    num_cols = int(haversine((max_lat, min_lon),
                             (max_lat, max_lon)) // dist) + 1

    # Function that locates every station in its respective quadrant.
    bcn_matrix = locate_on_quad(G, num_cols, num_rows, max_lat, min_lon, dist)

    # In this loop, we check all the possible connections between stations.
    for i in range(num_rows):
        for j in range(num_cols):
            G = adjacent(G, bcn_matrix, i, j, i, j, dist)
            if i > 0:
                G = adjacent(G, bcn_matrix, i, j, i-1, j, dist)
            if i > 0 and j + 1 < num_cols:
                G = adjacent(G, bcn_matrix, i, j, i-1, j+1, dist)
            if j + 1 < num_cols:
                G = adjacent(G, bcn_matrix, i, j, i, j+1, dist)
            if i + 1 < num_rows and j + 1 < num_cols:
                G = adjacent(G, bcn_matrix, i, j, i+1, j+1, dist)
    return G


# Returns the number of nodes in the current graph.
# Prec: A previous created graph, in nx.graph format, must be provided.
def nodes(G):
    return G.number_of_nodes()


# Returns the number of edges in the current graph.
# Prec: A previous created graph, in nx.graph format, must be provided.
def edges(G):
    return G.number_of_edges()


# Returns the number of conencted components in the current graph.
# Prec: A previous created graph, in nx.graph format, must be provided.
def components(G):
    return nx.number_connected_components(G)


# Returns a .png file, locating all the bicing
# stations and connections between them.
# Prec: A previous created graph, in nx.graph format, must be provided.
def plotgraph(G, name_file):
    map = StaticMap(750, 750)
    for station in G.edges:
        coord1, coord2 = station[0], station[1]
        line = Line([[coord1.lon, coord1.lat],
                    [coord2.lon, coord2.lat]], '#0000FFBB', 2)
        map.add_line(line)

    for station in G.nodes:
        marker = CircleMarker([station.lon, station.lat], 'red', 4)
        marker_outline = CircleMarker([station.lon, station.lat], 'black', 8)
        map.add_marker(marker_outline)
        map.add_marker(marker)
    image = map.render()
    image.save(name_file)


# #### Route-Start #####
# Transforms two given locations in their respective coordinates.
def addressesTOcoordinates(addresses):
    try:
        geolocator = Nominatim(user_agent="bicing_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return ((location1.latitude, location1.longitude),
                (location2.latitude, location2.longitude))
    except:
        return None


# Generates the fastest route between to given addresses.
def route(G, name_file, addresses):
    coord_origin, coord_destination = addressesTOcoordinates(addresses)
    coord_origin = Pandas(lat=coord_origin[0], lon=coord_origin[1])
    coord_destination = Pandas(lat=coord_destination[0],
                               lon=coord_destination[1])
    radius = haversine(coord_origin, coord_destination)
    G.add_nodes_from([coord_origin, coord_destination])
    for node in G.nodes:
        dist_O = haversine(coord_origin, (node.lat, node.lon))
        dist_D = haversine(coord_destination, (node.lat, node.lon))
        if dist_O <= radius:
            G.add_edge(coord_origin, node, weight=dist_O/4)
        if dist_D <= radius:
            G.add_edge(coord_destination, node, weight=dist_D/4)
    fastest_path = nx.dijkstra_path(G, coord_origin, coord_destination)
    G.remove_nodes_from([coord_origin, coord_destination])
    Route = nx.Graph()
    # When we modify the graph in order to be plotted, we also compute
    # the average time of the route.
    time = 0
    for i in range(len(fastest_path)-1):
        a, b = ((fastest_path[i].lat, fastest_path[i].lon),
                (fastest_path[i+1].lat, fastest_path[i+1].lon))
        if i == 0 or i == len(fastest_path)-1:
            time += haversine(a, b)/4
        else:
            time += haversine(a, b)/10
        Route.add_edge(fastest_path[i], fastest_path[i+1])
    plotgraph(Route, name_file)
    return int(time*60)
# #### Route-End #####


# Auxiliar function to obtain the index of station in our graph.
def index_graph_stations(G):
    list = []
    for node in G.nodes():
        list.append(node.Index)
    return list


def distribute(G, requiredBikes, requiredDocks):
    url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
    bikes = pd.DataFrame.from_records(pd.read_json(url_status)['data']
                                      ['stations'], index='station_id')
    G_Di = nx.DiGraph()
    G_Di.add_node('TOP')  # The green node
    demand = 0
    for st in bikes.itertuples():
        idx = st.Index
        if idx not in index_graph_stations(G):
            continue
        stridx = str(idx)
        # The blue (s), black (g) and red (t) nodes of the graph
        s_idx, g_idx, t_idx = 's'+stridx, 'g'+stridx, 't'+stridx
        G_Di.add_node(g_idx)
        G_Di.add_node(s_idx)
        G_Di.add_node(t_idx)

        b, d = st.num_bikes_available, st.num_docks_available
        req_bikes = max(0, requiredBikes - b)
        req_docks = max(0, requiredDocks - d)

        G_Di.add_edge('TOP', s_idx)
        G_Di.add_edge(t_idx, 'TOP')
        G_Di.add_edge(s_idx, g_idx)
        G_Di.add_edge(g_idx, t_idx)

        if req_bikes > 0:
            demand += req_bikes
            G_Di.nodes[t_idx]['demand'] = req_bikes
            G_Di.edges[s_idx, g_idx]['capacity'] = 0

        elif req_docks > 0:
            demand -= req_docks
            G_Di.nodes[s_idx]['demand'] = -req_docks
            G_Di.edges[g_idx, t_idx]['capacity'] = 0
    G_Di.nodes['TOP']['demand'] = -demand
    # Selects the established edges in our graph
    # and introduces them onto the directed.
    for edge in G.edges():
        node1 = edge[0]
        node2 = edge[1]
        id1 = node1.Index
        id2 = node2.Index
        dist = G[node1][node2]['weight']*10
        G_Di.add_edge('g'+str(id1), 'g'+str(id2),
                      cost=int(1000*dist), weight=dist)
        G_Di.add_edge('g'+str(id2), 'g'+str(id1),
                      cost=int(1000*dist), weight=dist)
    err = False

    try:
        flowCost, flowDict = nx.network_simplex(G_Di, weight='cost')

    except nx.NetworkXUnfeasible:
        err = True
        return err, 0, 0
        # Error = No solution could be found for the parameters given"

    # The format error has been eliminated, because the graph provided to the
    # function is directed.

    if not err:

        total_cost = 0
        initial = True
        for src in flowDict:
            if src[0] != 'g':
                continue
            idx_src = int(src[1:])
            for dst, b in flowDict[src].items():
                if dst[0] == 'g' and b > 0:
                    idx_dst = int(dst[1:])
                    total_cost += G_Di.edges[src, dst]['weight']
                    # The cost is the distance traveled * num of bikes.
                    cost = (G_Di.edges[src, dst]['weight'] *
                            b, idx_src, idx_dst)
                    if initial:
                        initial = False
                        Biggest_move = cost
                    elif cost[0] > Biggest_move[0]:
                        Biggest_move = cost
        if total_cost == 0:
            return err, total_cost, 0
        return err, total_cost, Biggest_move
