import datetime
import json
import math
import time
import os

import networkx
import networkx as nx
import pytest

from nycmesh_ospf_explorer.graph import OSPFGraph


def load_ospf_dict(graph_fname: str):
    path = os.path.join(os.path.dirname(__file__), f"sample_graphs/{graph_fname}")
    with open(path, "r") as f:
        ospf_dict = json.load(f)
        ospf_dict["updated"] = math.floor(time.time())
        return ospf_dict


TEST_FOUR_NODE_GRAPH = load_ospf_dict("four_node_graph.json")
TEST_THREE_NODE_GRAPH_WITH_METADATA = load_ospf_dict("three_node_graph_with_metadata.json")
TEST_NINE_NODE_GRAPH = load_ospf_dict("nine_node_graph.json")
TEST_NINE_NODE_GRAPH_WITH_ASYMMETRIC_COSTS = load_ospf_dict(
    "nine_node_graph_with_asymmetric_costs.json"
)


def test_initialization():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    assert len(graph._graph.edges) == 8
    assert len(graph._graph.nodes) == 4

    assert graph._graph.out_degree("10.69.0.1") == 1
    assert graph._graph.out_degree("10.69.0.2") == 2
    assert graph._graph.out_degree("10.69.0.3") == 3
    assert graph._graph.out_degree("10.70.0.4") == 2

    assert list(graph._graph.out_edges("10.69.0.1"))[0] == ("10.69.0.1", "10.69.0.2")
    assert list(graph._graph.out_edges("10.69.0.2"))[0] == ("10.69.0.2", "10.69.0.1")
    assert list(graph._graph.out_edges("10.69.0.2"))[1] == ("10.69.0.2", "10.69.0.3")
    assert list(graph._graph.out_edges("10.69.0.3"))[0] == ("10.69.0.3", "10.69.0.2")
    assert list(graph._graph.out_edges("10.69.0.3"))[1] == ("10.69.0.3", "10.70.0.4")
    assert list(graph._graph.out_edges("10.69.0.3"))[2] == ("10.69.0.3", "10.70.0.4")
    assert list(graph._graph.out_edges("10.70.0.4"))[0] == ("10.70.0.4", "10.69.0.3")
    assert list(graph._graph.out_edges("10.70.0.4"))[1] == ("10.70.0.4", "10.69.0.3")

    assert graph._graph.get_edge_data("10.69.0.1", "10.69.0.2")[0]["weight"] == 10
    assert graph._graph.get_edge_data("10.69.0.2", "10.69.0.1")[0]["weight"] == 10
    assert graph._graph.get_edge_data("10.69.0.2", "10.69.0.3")[0]["weight"] == 100
    assert graph._graph.get_edge_data("10.69.0.3", "10.69.0.2")[0]["weight"] == 100
    assert graph._graph.get_edge_data("10.69.0.3", "10.70.0.4")[0]["weight"] == 10
    assert graph._graph.get_edge_data("10.69.0.3", "10.70.0.4")[1]["weight"] == 100

    assert graph._graph.get_edge_data("10.70.0.4", "10.69.0.3")[0]["weight"] == 10
    assert graph._graph.get_edge_data("10.70.0.4", "10.69.0.3")[1]["weight"] == 100


def test_metadata():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_THREE_NODE_GRAPH_WITH_METADATA)

    assert len(graph._graph.edges) == 4
    assert len(graph._graph.nodes) == 3

    assert graph._graph.out_degree("10.69.0.1") == 2
    assert graph._graph.out_degree("10.69.0.2") == 1
    assert graph._graph.out_degree("10.69.0.3") == 1

    assert list(graph._graph.out_edges("10.69.0.1"))[0] == ("10.69.0.1", "10.69.0.2")
    assert list(graph._graph.out_edges("10.69.0.1"))[1] == ("10.69.0.1", "10.69.0.3")
    assert list(graph._graph.out_edges("10.69.0.2"))[0] == ("10.69.0.2", "10.69.0.1")
    assert list(graph._graph.out_edges("10.69.0.3"))[0] == ("10.69.0.3", "10.69.0.1")

    assert graph._graph.get_edge_data("10.69.0.1", "10.69.0.2")[0]["weight"] == 10
    assert graph._graph.get_edge_data("10.69.0.1", "10.69.0.3")[0]["weight"] == 10
    assert graph._graph.get_edge_data("10.69.0.2", "10.69.0.1")[0]["weight"] == 10
    assert graph._graph.get_edge_data("10.69.0.3", "10.69.0.1")[0]["weight"] == 10

    assert graph._graph.nodes["10.69.0.1"]["networks"] == {
        "stubnet": [{"id": "10.69.4.98/32", "metric": 0}],
        "external": [
            {"id": "0.0.0.0/0", "metric": 1},
            {"id": "10.70.251.60/30", "metric2": 10},
            {
                "id": "199.170.132.64/26",
                "metric": 20,
                "via": "10.70.89.131",
            },
        ],
        "router": [
            {"id": "10.69.0.2", "metric": 10},
            {"id": "10.69.0.3", "metric": 10},
        ],
    }
    assert graph._graph.nodes["10.69.0.2"]["networks"] == {
        "router": [{"id": "10.69.0.1", "metric": 10}]
    }
    assert "network" not in graph._graph.nodes["10.69.0.1"]["networks"]
    assert "network" not in graph._graph.nodes["10.69.0.2"]["networks"]

    assert graph.get_networks_for_node("10.69.0.1") == graph._graph.nodes["10.69.0.1"]["networks"]
    assert graph.get_networks_for_node("10.69.0.2") == graph._graph.nodes["10.69.0.2"]["networks"]


def test_contains_node():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    assert graph.contains_router("10.69.0.1") == True
    assert graph.contains_router("10.69.0.2") == True
    assert graph.contains_router("10.69.0.3") == True
    assert graph.contains_router("10.70.0.4") == True

    assert graph.contains_router("10.69.0.5") == False
    assert graph.contains_router("zzz") == False


def test_get_edges():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_NINE_NODE_GRAPH_WITH_ASYMMETRIC_COSTS)

    assert graph.get_edges_for_node_pair("10.69.0.1", "10.69.0.2") == [
        {"from": "10.69.0.1", "to": "10.69.0.2", "weight": 10}
    ]

    assert graph.get_edges_for_node_pair("10.69.0.2", "10.69.0.1") == [
        {"from": "10.69.0.2", "to": "10.69.0.1", "weight": 10}
    ]

    assert graph.get_edges_for_node_pair("10.69.0.1", "10.69.0.5") == [
        {"from": "10.69.0.1", "to": "10.69.0.5", "weight": 10},
        {"from": "10.69.0.1", "to": "10.69.0.5", "weight": 100},
    ]

    assert graph.get_edges_for_node_pair("10.69.0.5", "10.69.0.1") == [
        {"from": "10.69.0.5", "to": "10.69.0.1", "weight": 10},
        {"from": "10.69.0.5", "to": "10.69.0.1", "weight": 100},
    ]

    assert graph.get_edges_for_node_pair("10.69.0.3", "10.69.0.2") == [
        {"from": "10.69.0.3", "to": "10.69.0.2", "weight": 100}
    ]

    assert graph.get_edges_for_node_pair("10.69.0.2", "10.69.0.3") == [
        {"from": "10.69.0.2", "to": "10.69.0.3", "weight": 5}
    ]

    assert graph.get_edges_for_node_pair("10.69.0.3", "10.69.0.7") == []

    assert graph.get_edges_for_node_pair("10.69.0.7", "10.69.0.3") == []


def test_get_neighbors_simple():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    neighbors_subgraph: networkx.MultiDiGraph = graph._get_neighbors_subgraph(
        "10.69.0.1", neighbor_depth=1
    )

    assert len(neighbors_subgraph.nodes) == 2
    assert len(neighbors_subgraph.edges) == 2

    assert neighbors_subgraph.out_degree("10.69.0.1") == 1
    assert neighbors_subgraph.out_degree("10.69.0.2") == 1

    assert list(neighbors_subgraph.out_edges("10.69.0.1"))[0] == (
        "10.69.0.1",
        "10.69.0.2",
    )
    assert list(neighbors_subgraph.out_edges("10.69.0.2"))[0] == (
        "10.69.0.2",
        "10.69.0.1",
    )


def test_get_neighbors_base_case():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    neighbors_subgraph: networkx.MultiDiGraph = graph._get_neighbors_subgraph(
        "10.69.0.1", neighbor_depth=0
    )

    assert len(neighbors_subgraph.nodes) == 1
    assert len(neighbors_subgraph.edges) == 0

    assert neighbors_subgraph.out_degree("10.69.0.1") == 0


def test_get_neighbors_deeper():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    neighbors_subgraph: networkx.MultiDiGraph = graph._get_neighbors_subgraph(
        "10.69.0.1", neighbor_depth=2
    )

    assert len(neighbors_subgraph.nodes) == 3
    assert len(neighbors_subgraph.edges) == 4

    assert neighbors_subgraph.out_degree("10.69.0.1") == 1
    assert neighbors_subgraph.out_degree("10.69.0.2") == 2
    assert neighbors_subgraph.out_degree("10.69.0.3") == 1

    assert list(neighbors_subgraph.out_edges("10.69.0.1"))[0] == (
        "10.69.0.1",
        "10.69.0.2",
    )
    assert list(neighbors_subgraph.out_edges("10.69.0.2"))[0] == (
        "10.69.0.2",
        "10.69.0.1",
    )
    assert list(neighbors_subgraph.out_edges("10.69.0.2"))[1] == (
        "10.69.0.2",
        "10.69.0.3",
    )
    assert list(neighbors_subgraph.out_edges("10.69.0.3"))[0] == (
        "10.69.0.3",
        "10.69.0.2",
    )


def test_get_neighbors_spread_from_center():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    neighbors_subgraph: networkx.MultiDiGraph = graph._get_neighbors_subgraph(
        "10.69.0.2", neighbor_depth=1
    )

    assert len(neighbors_subgraph.nodes) == 3
    assert len(neighbors_subgraph.edges) == 4

    assert neighbors_subgraph.out_degree("10.69.0.1") == 1
    assert neighbors_subgraph.out_degree("10.69.0.2") == 2
    assert neighbors_subgraph.out_degree("10.69.0.3") == 1

    assert list(neighbors_subgraph.out_edges("10.69.0.1"))[0] == (
        "10.69.0.1",
        "10.69.0.2",
    )
    assert list(neighbors_subgraph.out_edges("10.69.0.2"))[0] == (
        "10.69.0.2",
        "10.69.0.1",
    )
    assert list(neighbors_subgraph.out_edges("10.69.0.2"))[1] == (
        "10.69.0.2",
        "10.69.0.3",
    )
    assert list(neighbors_subgraph.out_edges("10.69.0.3"))[0] == (
        "10.69.0.3",
        "10.69.0.2",
    )


def test_convert_full_subgraph_to_json():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    assert graph._convert_subgraph_to_json(graph._graph) == {
        "nodes": [
            {
                "id": "10.69.0.1",
                "nn": "1",
                "nn_int": 1,
                "networks": {"router": [{"id": "10.69.0.2", "metric": 10}]},
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.1", None), ("10.69.0.2", 10)],
                    "return": [("10.69.0.2", None), ("10.69.0.1", 10)],
                },
                "missing_edges": 0,
            },
            {
                "id": "10.69.0.2",
                "nn": "2",
                "nn_int": 2,
                "networks": {
                    "router": [
                        {"id": "10.69.0.1", "metric": 10},
                        {"id": "10.69.0.3", "metric": 100},
                    ],
                    "external": [
                        {"id": "0.0.0.0/0", "metric": 1},
                    ],
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.2", None)],
                    "return": [("10.69.0.2", None)],
                },
                "missing_edges": 0,
            },
            {
                "id": "10.69.0.3",
                "nn": "3",
                "nn_int": 3,
                "networks": {
                    "router": [
                        {"id": "10.69.0.2", "metric": 100},
                        {"id": "10.70.0.4", "metric": 10},
                        {"id": "10.70.0.4", "metric": 100},
                    ]
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.3", None), ("10.69.0.2", 100)],
                    "return": [("10.69.0.2", None), ("10.69.0.3", 100)],
                },
                "missing_edges": 0,
            },
            {
                "id": "10.70.0.4",
                "nn": None,
                "nn_int": None,
                "networks": {
                    "router": [
                        {"id": "10.69.0.3", "metric": 10},
                        {"id": "10.69.0.3", "metric": 100},
                    ],
                    "external": [{"id": "0.0.0.0/0", "metric": 10000}],
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.70.0.4", None), ("10.69.0.3", 10), ("10.69.0.2", 100)],
                    "return": [("10.69.0.2", None), ("10.69.0.3", 100), ("10.70.0.4", 10)],
                },
                "missing_edges": 0,
            },
        ],
        "edges": [
            {"from": "10.69.0.1", "to": "10.69.0.2", "weight": 10},
            {"from": "10.69.0.2", "to": "10.69.0.1", "weight": 10},
            {"from": "10.69.0.2", "to": "10.69.0.3", "weight": 100},
            {"from": "10.69.0.3", "to": "10.69.0.2", "weight": 100},
            {"from": "10.69.0.3", "to": "10.70.0.4", "weight": 10},
            {"from": "10.69.0.3", "to": "10.70.0.4", "weight": 100},
            {"from": "10.70.0.4", "to": "10.69.0.3", "weight": 10},
            {"from": "10.70.0.4", "to": "10.69.0.3", "weight": 100},
        ],
    }


def test_convert_partial_subgraph_to_json():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    assert graph._convert_subgraph_to_json(graph._graph.subgraph(["10.69.0.2", "10.69.0.3"])) == {
        "nodes": [
            {
                "id": "10.69.0.2",
                "nn": "2",
                "nn_int": 2,
                "networks": {
                    "router": [
                        {"id": "10.69.0.1", "metric": 10},
                        {"id": "10.69.0.3", "metric": 100},
                    ],
                    "external": [
                        {"id": "0.0.0.0/0", "metric": 1},
                    ],
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.2", None)],
                    "return": [("10.69.0.2", None)],
                },
                "missing_edges": 1,
            },
            {
                "id": "10.69.0.3",
                "nn": "3",
                "nn_int": 3,
                "networks": {
                    "router": [
                        {"id": "10.69.0.2", "metric": 100},
                        {"id": "10.70.0.4", "metric": 10},
                        {"id": "10.70.0.4", "metric": 100},
                    ]
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.3", None), ("10.69.0.2", 100)],
                    "return": [("10.69.0.2", None), ("10.69.0.3", 100)],
                },
                "missing_edges": 2,
            },
        ],
        "edges": [
            {"from": "10.69.0.2", "to": "10.69.0.3", "weight": 100},
            {"from": "10.69.0.3", "to": "10.69.0.2", "weight": 100},
        ],
    }


def test_get_neighbors_dict():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    assert graph.get_neighbors_dict("10.69.0.1") == {
        "nodes": [
            {
                "id": "10.69.0.1",
                "nn": "1",
                "nn_int": 1,
                "networks": {"router": [{"id": "10.69.0.2", "metric": 10}]},
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.1", None), ("10.69.0.2", 10)],
                    "return": [("10.69.0.2", None), ("10.69.0.1", 10)],
                },
                "missing_edges": 0,
                "in_neighbor_set": True,
            },
            {
                "id": "10.69.0.2",
                "nn": "2",
                "nn_int": 2,
                "networks": {
                    "router": [
                        {"id": "10.69.0.1", "metric": 10},
                        {"id": "10.69.0.3", "metric": 100},
                    ],
                    "external": [
                        {"id": "0.0.0.0/0", "metric": 1},
                    ],
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.2", None)],
                    "return": [("10.69.0.2", None)],
                },
                "missing_edges": 1,
                "in_neighbor_set": True,
            },
        ],
        "edges": [
            {"from": "10.69.0.1", "to": "10.69.0.2", "weight": 10},
            {"from": "10.69.0.2", "to": "10.69.0.1", "weight": 10},
        ],
    }


def test_get_neighbors_with_egress_path():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    assert graph.get_neighbors_dict("10.70.0.4", include_egress=True) == {
        "nodes": [
            {
                "id": "10.69.0.2",
                "nn": "2",
                "nn_int": 2,
                "networks": {
                    "router": [
                        {"id": "10.69.0.1", "metric": 10},
                        {"id": "10.69.0.3", "metric": 100},
                    ],
                    "external": [
                        {"id": "0.0.0.0/0", "metric": 1},
                    ],
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.2", None)],
                    "return": [("10.69.0.2", None)],
                },
                "missing_edges": 1,
                "in_neighbor_set": False,
            },
            {
                "id": "10.69.0.3",
                "nn": "3",
                "nn_int": 3,
                "networks": {
                    "router": [
                        {"id": "10.69.0.2", "metric": 100},
                        {"id": "10.70.0.4", "metric": 10},
                        {"id": "10.70.0.4", "metric": 100},
                    ],
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.69.0.3", None), ("10.69.0.2", 100)],
                    "return": [("10.69.0.2", None), ("10.69.0.3", 100)],
                },
                "missing_edges": 0,
                "in_neighbor_set": True,
            },
            {
                "id": "10.70.0.4",
                "nn": None,
                "nn_int": None,
                "networks": {
                    "router": [
                        {"id": "10.69.0.3", "metric": 10},
                        {"id": "10.69.0.3", "metric": 100},
                    ],
                    "external": [{"id": "0.0.0.0/0", "metric": 10000}],
                },
                "exit_network_cost": 1,
                "exit_paths": {
                    "outbound": [("10.70.0.4", None), ("10.69.0.3", 10), ("10.69.0.2", 100)],
                    "return": [("10.69.0.2", None), ("10.69.0.3", 100), ("10.70.0.4", 10)],
                },
                "missing_edges": 0,
                "in_neighbor_set": True,
            },
        ],
        "edges": [
            {"from": "10.69.0.2", "to": "10.69.0.3", "weight": 100},
            {"from": "10.69.0.3", "to": "10.69.0.2", "weight": 100},
            {"from": "10.69.0.3", "to": "10.70.0.4", "weight": 10},
            {"from": "10.69.0.3", "to": "10.70.0.4", "weight": 100},
            {"from": "10.70.0.4", "to": "10.69.0.3", "weight": 10},
            {"from": "10.70.0.4", "to": "10.69.0.3", "weight": 100},
        ],
    }


def test_multiple_exits():
    graph = OSPFGraph(load_data=False)
    graph.update_link_data(TEST_NINE_NODE_GRAPH)

    output = graph._convert_subgraph_to_json(graph._graph)
    exit_paths = {node["id"]: node["exit_paths"]["outbound"] for node in output["nodes"]}
    assert exit_paths == {
        "10.69.0.1": [("10.69.0.1", None), ("10.69.0.2", 10)],
        "10.69.0.2": [("10.69.0.2", None)],
        "10.69.0.3": [("10.69.0.3", None), ("10.69.0.2", 100)],
        "10.69.0.4": [("10.69.0.4", None), ("10.69.0.3", 10), ("10.69.0.2", 100)],
        "10.69.0.5": [("10.69.0.5", None), ("10.69.0.1", 10), ("10.69.0.2", 10)],
        "10.69.0.6": [("10.69.0.6", None), ("10.69.0.7", 10), ("10.69.0.8", 10)],
        "10.69.0.7": [("10.69.0.7", None), ("10.69.0.8", 10)],
        "10.69.0.8": [("10.69.0.8", None)],
        "10.69.0.9": [("10.69.0.9", None), ("10.69.0.1", 10), ("10.69.0.2", 10)],
    }

    egress_forest = graph._compute_egress_forest(graph._graph)
    assert nx.is_forest(egress_forest)
    exit_tree_node_2 = egress_forest.subgraph(
        nx.node_connected_component(egress_forest.to_undirected(), "10.69.0.2")
    )
    assert len(exit_tree_node_2.nodes) == 6 + 1  # Extra node for exit placeholder
    assert len(exit_tree_node_2.edges) == 5 + 1  # Extra edge for exit placeholder

    for node in exit_tree_node_2:
        if node == "10.69.0.2_0.0.0.0/0":
            assert exit_tree_node_2.out_degree(node) == 0
        else:
            assert exit_tree_node_2.out_degree(node) == 1

    assert list(exit_tree_node_2.out_edges("10.69.0.1"))[0] == (
        "10.69.0.1",
        "10.69.0.2",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.2"))[0] == (
        "10.69.0.2",
        "10.69.0.2_0.0.0.0/0",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.3"))[0] == (
        "10.69.0.3",
        "10.69.0.2",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.4"))[0] == (
        "10.69.0.4",
        "10.69.0.3",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.5"))[0] == (
        "10.69.0.5",
        "10.69.0.1",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.9"))[0] == (
        "10.69.0.9",
        "10.69.0.1",
    )

    exit_tree_node_8 = egress_forest.subgraph(
        nx.node_connected_component(egress_forest.to_undirected(), "10.69.0.8")
    )
    assert len(exit_tree_node_8.nodes) == 3 + 1  # Extra node for exit placeholder
    assert len(exit_tree_node_8.edges) == 2 + 1  # Extra edge for exit placeholder

    assert exit_tree_node_8.out_degree("10.69.0.6") == 1
    assert exit_tree_node_8.out_degree("10.69.0.7") == 1
    assert exit_tree_node_8.out_degree("10.69.0.8") == 1
    assert exit_tree_node_8.out_degree("10.69.0.8_0.0.0.0/0") == 0

    assert list(exit_tree_node_8.out_edges("10.69.0.6"))[0] == (
        "10.69.0.6",
        "10.69.0.7",
    )
    assert list(exit_tree_node_8.out_edges("10.69.0.7"))[0] == (
        "10.69.0.7",
        "10.69.0.8",
    )
    assert list(exit_tree_node_8.out_edges("10.69.0.8"))[0] == (
        "10.69.0.8",
        "10.69.0.8_0.0.0.0/0",
    )


def test_asymmetric():
    graph = OSPFGraph(load_data=False)
    graph.update_link_data(TEST_NINE_NODE_GRAPH_WITH_ASYMMETRIC_COSTS)

    output = graph._convert_subgraph_to_json(graph._graph)
    outbound_paths = {node["id"]: node["exit_paths"]["outbound"] for node in output["nodes"]}
    assert outbound_paths == {
        "10.69.0.1": [("10.69.0.1", None), ("10.69.0.2", 10)],
        "10.69.0.2": [("10.69.0.2", None)],
        "10.69.0.3": [("10.69.0.3", None), ("10.69.0.5", 5), ("10.69.0.1", 10), ("10.69.0.2", 10)],
        "10.69.0.4": [
            ("10.69.0.4", None),
            ("10.69.0.3", 10),
            ("10.69.0.5", 5),
            ("10.69.0.1", 10),
            ("10.69.0.2", 10),
        ],
        "10.69.0.5": [("10.69.0.5", None), ("10.69.0.1", 10), ("10.69.0.2", 10)],
        "10.69.0.6": [("10.69.0.6", None), ("10.69.0.7", 10), ("10.69.0.8", 10)],
        "10.69.0.7": [("10.69.0.7", None), ("10.69.0.8", 10)],
        "10.69.0.8": [("10.69.0.8", None)],
        "10.69.0.9": [("10.69.0.9", None), ("10.69.0.1", 10), ("10.69.0.2", 10)],
    }

    return_paths = {node["id"]: node["exit_paths"]["return"] for node in output["nodes"]}
    assert return_paths == {
        "10.69.0.1": [("10.69.0.2", None), ("10.69.0.1", 10)],
        "10.69.0.2": [("10.69.0.2", None)],
        "10.69.0.3": [("10.69.0.2", None), ("10.69.0.3", 5)],
        "10.69.0.4": [
            ("10.69.0.2", None),
            ("10.69.0.6", 100),
            ("10.69.0.7", 10),
            ("10.69.0.4", 10),
        ],
        "10.69.0.5": [("10.69.0.2", None), ("10.69.0.3", 5), ("10.69.0.5", 5)],
        "10.69.0.6": [("10.69.0.8", None), ("10.69.0.7", 10), ("10.69.0.6", 10)],
        "10.69.0.7": [("10.69.0.8", None), ("10.69.0.7", 10)],
        "10.69.0.8": [("10.69.0.8", None)],
        "10.69.0.9": [("10.69.0.2", None), ("10.69.0.1", 10), ("10.69.0.9", 10)],
    }
    assert return_paths == graph._egress_return_paths

    egress_forest = graph._compute_egress_forest(graph._graph)
    assert nx.is_forest(egress_forest)
    exit_tree_node_2 = egress_forest.subgraph(
        nx.node_connected_component(egress_forest.to_undirected(), "10.69.0.2")
    )
    assert len(exit_tree_node_2.nodes) == 6 + 1  # Extra node for exit placeholder
    assert len(exit_tree_node_2.edges) == 5 + 1  # Extra edge for exit placeholder

    for node in exit_tree_node_2:
        if node == "10.69.0.2_0.0.0.0/0":
            assert exit_tree_node_2.out_degree(node) == 0
        else:
            assert exit_tree_node_2.out_degree(node) == 1

    assert list(exit_tree_node_2.out_edges("10.69.0.1"))[0] == (
        "10.69.0.1",
        "10.69.0.2",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.2"))[0] == (
        "10.69.0.2",
        "10.69.0.2_0.0.0.0/0",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.3"))[0] == (
        "10.69.0.3",
        "10.69.0.5",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.4"))[0] == (
        "10.69.0.4",
        "10.69.0.3",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.5"))[0] == (
        "10.69.0.5",
        "10.69.0.1",
    )
    assert list(exit_tree_node_2.out_edges("10.69.0.9"))[0] == (
        "10.69.0.9",
        "10.69.0.1",
    )

    exit_tree_node_8 = egress_forest.subgraph(
        nx.node_connected_component(egress_forest.to_undirected(), "10.69.0.8")
    )
    assert len(exit_tree_node_8.nodes) == 3 + 1  # Extra node for exit placeholder
    assert len(exit_tree_node_8.edges) == 2 + 1  # Extra edge for exit placeholder

    assert exit_tree_node_8.out_degree("10.69.0.6") == 1
    assert exit_tree_node_8.out_degree("10.69.0.7") == 1
    assert exit_tree_node_8.out_degree("10.69.0.8") == 1
    assert exit_tree_node_8.out_degree("10.69.0.8_0.0.0.0/0") == 0

    assert list(exit_tree_node_8.out_edges("10.69.0.6"))[0] == (
        "10.69.0.6",
        "10.69.0.7",
    )
    assert list(exit_tree_node_8.out_edges("10.69.0.7"))[0] == (
        "10.69.0.7",
        "10.69.0.8",
    )
    assert list(exit_tree_node_8.out_edges("10.69.0.8"))[0] == (
        "10.69.0.8",
        "10.69.0.8_0.0.0.0/0",
    )
