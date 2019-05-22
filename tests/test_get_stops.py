import unittest

import core
from core.main import get_compute_graph, get_nb_stops


class TestCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.stops = [
            ['Montreuil', 'Nation', 'République', 'Boulbi', 'Sèvres'],
            ['Etoile', 'Place de clichy', 'Barbès', 'Nation', 'Butte aux Cailles', 'Montparnasse'],
            ['Clignancourt', 'Barbès', 'République', 'Montparnasse'],
        ]
        cls.graph = get_compute_graph(cls.stops)

    def test_nb_stops_reached(self):
        expected_nb_stop = 4
        nb_stops = get_nb_stops('Etoile', 'Montparnasse', self.graph)
        self.assertEqual(nb_stops, expected_nb_stop)

    def test_nb_stops_dummy(self):
        expected_nb_stop = 0
        nb_stops = get_nb_stops('Etoile', 'Etoile', self.graph)
        self.assertEqual(nb_stops, expected_nb_stop)

    def test_nb_stops_unreachable(self):
        self.assertRaises(
            core.exceptions.UnreachableStation,
            get_nb_stops,
            'Place de clichy',
            'Etoile',
            self.graph,
        )
