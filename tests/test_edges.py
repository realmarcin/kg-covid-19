import unittest

import pandas as pd
from pandas import np

from kg_covid_19.edges import make_edges, tsv_to_df, has_disconnected_nodes, \
    make_negative_edges, make_positive_edges


class TestEdges(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.small_nodes_file = 'tests/resources/edges/small_graph_nodes.tsv'
        cls.small_edges_file = 'tests/resources/edges/small_graph_edges.tsv'
        cls.edges = tsv_to_df(cls.small_edges_file)
        cls.nodes = tsv_to_df(cls.small_nodes_file)

        # make negative edges for small graph
        cls.num_edges = 5
        cls.ne = make_negative_edges(cls.num_edges, cls.nodes, cls.edges)

        # make positive edges for small graph
        (cls.pe, cls.new_graph_edges) = make_positive_edges(cls.num_edges,
                                                      cls.nodes,
                                                      cls.edges, min_degree = 1)

    def setUp(self) -> None:
        pass

    def test_tsv_to_df(self):
        df = tsv_to_df(self.small_edges_file)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual((21, 5), df.shape)
        self.assertEqual(df['subject'][0], 'g1')

    def test_make_edges(self):
        self.assertTrue(True)

    #
    # positive edge tests
    #
    def test_make_positives_edges_check_pe_instance_type(self):
        self.assertTrue(isinstance(self.pe, pd.DataFrame))

    def test_make_positives_edges_check_new_edges_instance_type(self):
        self.assertTrue(isinstance(self.new_graph_edges, pd.DataFrame))

    def test_make_positive_edges_check_num_edges_returned(self):
        self.assertEqual(self.num_edges, self.pe.shape[0])

    def test_make_positive_edges_check_new_graph_size(self):
        self.assertEqual(self.num_edges,
                         self.edges.shape - self.new_graph_edges.shape[0])

    def test_make_positive_edges_check_column_names(self):
        expected_columns = ['subject', 'edge_label', 'object', 'relation']
        self.assertEqual(len(expected_columns), self.pe.shape[1],
                         "didn't get expected columns in negative edge df")
        self.assertListEqual(expected_columns, list(self.pe.columns))

    def test_make_positive_edges_check_edge_label_column(self):
        expected_edge_label = 'positive_edge'
        self.assertListEqual([expected_edge_label] * self.pe.shape[0],
                             list(self.pe.edge_label),
                             "Edge label column not correct in positive edges")

    def test_make_positive_edges_check_relation_column(self):
        expected_relation = 'positive_edge'
        self.assertListEqual([expected_relation] * self.pe.shape[0],
                             list(self.pe.relation),
                             "Relation column not correct  in positive edges")

    #
    # negative edge tests
    #
    def test_has_disconnected_nodes(self):
        nodes_extra_ids = tsv_to_df('tests/resources/edges/small_graph_nodes_EXTRA_IDS.tsv')
        nodes_missing_ids = tsv_to_df(
            'tests/resources/edges/small_graph_nodes_MISSING_IDS.tsv')
        self.assertTrue(not has_disconnected_nodes(edges_df=self.edges,
                                                   nodes_df=self.nodes))
        with self.assertWarns(Warning):
            self.assertTrue(not has_disconnected_nodes(edges_df=self.edges,
                                                       nodes_df=nodes_missing_ids))
        self.assertTrue(has_disconnected_nodes(edges_df=self.edges,
                                               nodes_df=nodes_extra_ids))

    def test_make_negative_edges_check_instance_type(self):
        self.assertTrue(isinstance(self.pe, pd.DataFrame))

    def test_make_negative_edges_check_num_edges_returned(self):
        self.assertEqual(self.num_edges, self.ne.shape[0])

    def test_make_negative_edges_check_column_names(self):
        expected_columns = ['subject', 'edge_label', 'object', 'relation']
        self.assertEqual(len(expected_columns), self.ne.shape[1],
                         "didn't get expected columns in negative edge df")
        self.assertListEqual(expected_columns, list(self.ne.columns))

    def test_make_negative_edges_check_edge_label_column(self):
        expected_edge_label = 'negative_edge'
        self.assertListEqual([expected_edge_label] * self.ne.shape[0],
                             list(self.ne.edge_label),
                             "Edge label column not correct")

    def test_make_negative_edges_check_relation_column(self):
        expected_relation = 'negative_edge'
        self.assertListEqual([expected_relation] * self.ne.shape[0],
                             list(self.ne.relation),
                             "Relation column not correct")

    def test_make_negative_edges_check_neg_nodes(self):
        unique_node_ids = list(np.unique(self.nodes.id))
        neg_nodes = list(np.unique(np.concatenate((self.ne.subject,
                                                   self.ne.object))))
        self.assertTrue(set(neg_nodes) <= set(unique_node_ids),
                        "Some nodes from negative edges are not in the nodes tsv file")

    def test_make_negative_edges_no_reflexive_edges(self):
        reflexive_es = self.ne.loc[(self.ne['subject'] == self.ne['object'])]
        self.assertEqual(0, reflexive_es.shape[0],
                         "%i edges are reflexive" % reflexive_es.shape[0])

    def test_make_negative_edges_test_repeated_edges(self):
        # make sure we don't create duplicate negative edges
        count_info = self.ne.groupby(['subject', 'object']).size().\
            reset_index().rename(columns={0: 'counts'})
        dup_rows = count_info.loc[count_info.counts > 1]
        dup_rows_str = dup_rows.to_string(index=False, index_names=False)
        self.assertTrue(dup_rows.shape[0] == 0,
                        "Got %i duplicated edges:\n%s" % (dup_rows.shape[0],
                                                          dup_rows_str))

    def test_make_negative_edges_ensure_neg_edges_are_actually_negative(self):
        # make sure our negative edges are actually negative, i.e. not in edges_df
        non_neg_edges = self.ne.merge(self.edges, how='inner',
                                  left_on=['subject', 'object'],
                                  right_on=['subject', 'object'])
        non_neg_edges_str = non_neg_edges.to_string(index=False, index_names=False)
        self.assertTrue(non_neg_edges.shape[0] == 0,
                        "Got %i negative edges that are not actually negative:\n%s" %
                        (non_neg_edges.shape[0], non_neg_edges_str))

    # TODO - test node_types fxn


