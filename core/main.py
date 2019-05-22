import argparse
import logging
import math
import xml.etree.ElementTree as ET
import zipfile
from copy import deepcopy
from os import listdir
from os.path import isfile, join

import graphviz
import networkx as nx
import tqdm

from core.exceptions import UnreachableStation

ZIP_PATH = './journey-planner-timetables.zip'
UNZIPED_FOLDER = './journey-planner-timetables'
VIZ_FILEPATH = './journey-planner-graph'


def get_xml_files(source_dir, target_dir, skip_file_processing=False):
    if not skip_file_processing:
        zip_ref = zipfile.ZipFile(source_dir, 'r')
        zip_ref.extractall(target_dir)
        zip_ref.close()
        logging.info('Unzipped done.')
    else:
        logging.info('Unzipped skipped.')
    xml_files = [
        join(UNZIPED_FOLDER, f)
        for f in listdir(UNZIPED_FOLDER)
        if isfile(join(UNZIPED_FOLDER, f)) and 'xml' in f
    ]
    return xml_files


def get_stops_from_tree(tree):
    stops = []
    for parent in tree.getiterator():
        if 'CommonName' in parent.tag:
            stops.append(parent.text)
    return stops


def get_all_stops(xml_files, sample_files=None):
    all_stops = []
    if sample_files:
        xml_files = xml_files[:int(sample_files)]

    for xml_file in tqdm.tqdm(xml_files):
        tree = ET.parse(xml_file)
        stops = get_stops_from_tree(tree)
        all_stops.append(stops)
    return all_stops


def get_compute_graph(stops):
    # weights default to 1
    compute_graph = nx.DiGraph()
    for stops in stops:
        compute_graph.add_weighted_edges_from(zip(stops[:-1], stops[1:], [1] * len(stops)))
    return compute_graph


def get_viz_graph(stops, file_path, render_graph=True):
    viz_graph = graphviz.Digraph()
    for stops in stops:
        for edge in zip(stops[:-1], stops[1:]):
            viz_graph.edge(*edge)
    if render_graph:
        viz_graph.render(file_path)
    return viz_graph


def get_nb_stops(departure, arrival, graph):

    visited = {
        departure: 0
    }
    cont = True

    while cont:

        visited_previous = deepcopy(visited)
        for (station_visited, nb_stops) in visited_previous.items():

            station_candidates = graph.neighbors(station_visited)
            nb_stops_candidates = nb_stops + 1  # TODO incr by station_candidate's weight
            for station_candidate in station_candidates:
                visited[station_candidate] = min(visited.get(station_candidate, math.inf), nb_stops_candidates)

        visited_length_current = len(visited)
        visited_length_previous = len(visited_previous)

        if arrival in visited.keys():
            nb_stops = visited[arrival]
            logging.info(
                'Station %s can be reached from station: %s in %s stop',
                departure,
                arrival,
                nb_stops,
            )
            return nb_stops
        cont = visited_length_previous != visited_length_current
        if not cont:
            logging.error(
                'Station %s cant be reached from station: %s',
                departure,
                arrival,
            )
            raise UnreachableStation


def main(skip_file_processing, sample_files, render_graph):
    xml_files = get_xml_files(ZIP_PATH, UNZIPED_FOLDER, skip_file_processing=skip_file_processing)
    stops_list = get_all_stops(xml_files, sample_files)
    get_viz_graph(stops_list, VIZ_FILEPATH, render_graph=render_graph)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'render_graph',
        help='1 to generate graph viz, 0 otherwise. Warning this takes time.',
    )
    parser.add_argument(
        '--sample_files',
        default=None,
        help='Set to process limited number of xml files',
    )
    parser.add_argument(
        '--skip_file_processing', action='store_true', help='Use if xml files have been extracted already',
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main(args.skip_file_processing, args.sample_files, args.render_graph)
