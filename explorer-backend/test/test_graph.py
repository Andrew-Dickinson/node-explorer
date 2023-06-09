import datetime
import math
import time

import networkx
import networkx as nx
import pytest

from nycmesh_ospf_explorer.graph import OSPFGraph

TEST_FOUR_NODE_GRAPH = {
    "areas": {
        "0.0.0.0": {
            "routers": {
                "10.69.0.1": {"links": {"router": [{"id": "10.69.0.2", "metric": 10}]}},
                "10.69.0.2": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.1", "metric": 10},
                            {"id": "10.69.0.3", "metric": 100},
                        ],
                        "external": [
                            {"id": "0.0.0.0/0", "metric": 1},
                        ],
                    }
                },
                "10.69.0.3": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.2", "metric": 100},
                            {"id": "10.70.0.4", "metric": 10},
                            {"id": "10.70.0.4", "metric": 100},
                        ]
                    }
                },
                "10.70.0.4": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.3", "metric": 10},
                            {"id": "10.69.0.3", "metric": 100},
                        ]
                    },
                },
            },
            "networks": {},
        }
    },
    "updated": math.floor(time.time()),
}

TEST_THREE_NODE_GRAPH_WITH_METADATA = {
    "areas": {
        "0.0.0.0": {
            "routers": {
                "10.69.0.1": {
                    "links": {
                        "router": [{"id": "10.69.0.2", "metric": 10}],
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
                        "network": [{"id": "10.70.76.0/24", "metric": 10}],
                    }
                },
                "10.69.0.2": {"links": {"router": [{"id": "10.69.0.1", "metric": 10}]}},
                "10.69.0.3": {
                    "links": {"network": [{"id": "10.70.76.0/24", "metric": 10}]}
                },
            },
            "networks": {
                "10.70.76.0/24": {
                    "dr": "10.69.0.1",
                    "routers": ["10.69.0.1", "10.69.0.3"],
                }
            },
        }
    },
    "updated": math.floor(time.time()),
}


TEST_NINE_NODE_GRAPH = {
    "areas": {
        "0.0.0.0": {
            "routers": {
                "10.69.0.1": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.2", "metric": 10},
                            {"id": "10.69.0.5", "metric": 10},
                            {"id": "10.69.0.5", "metric": 100},
                            {"id": "10.69.0.9", "metric": 10},
                        ]
                    }
                },
                "10.69.0.2": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.1", "metric": 10},
                            {"id": "10.69.0.3", "metric": 100},
                            {"id": "10.69.0.6", "metric": 100},
                        ],
                        "external": [
                            {"id": "0.0.0.0/0", "metric": 1},
                        ],
                    }
                },
                "10.69.0.3": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.2", "metric": 100},
                            {"id": "10.69.0.4", "metric": 10},
                            {"id": "10.69.0.4", "metric": 100},
                            {"id": "10.69.0.5", "metric": 100},
                        ]
                    }
                },
                "10.69.0.4": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.3", "metric": 10},
                            {"id": "10.69.0.3", "metric": 100},
                            {"id": "10.69.0.7", "metric": 300},
                        ]
                    },
                },
                "10.69.0.5": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.1", "metric": 10},
                            {"id": "10.69.0.1", "metric": 100},
                            {"id": "10.69.0.3", "metric": 100},
                        ]
                    },
                },
                "10.69.0.6": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.2", "metric": 100},
                            {"id": "10.69.0.7", "metric": 10},
                        ]
                    },
                },
                "10.69.0.7": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.6", "metric": 10},
                            {"id": "10.69.0.8", "metric": 10},
                            {"id": "10.69.0.8", "metric": 100},
                        ]
                    },
                },
                "10.69.0.8": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.7", "metric": 10},
                            {"id": "10.69.0.7", "metric": 100},
                        ],
                        "external": [
                            {"id": "0.0.0.0/0", "metric": 1},
                        ],
                    },
                },
                "10.69.0.9": {
                    "links": {
                        "router": [
                            {"id": "10.69.0.1", "metric": 10},
                        ],
                    },
                },
            },
            "networks": {},
        }
    },
    "updated": math.floor(time.time()),
}


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

    assert (
        graph.get_networks_for_node("10.69.0.1")
        == graph._graph.nodes["10.69.0.1"]["networks"]
    )
    assert (
        graph.get_networks_for_node("10.69.0.2")
        == graph._graph.nodes["10.69.0.2"]["networks"]
    )


def test_contains_node():
    graph = OSPFGraph(load_data=False)

    graph.update_link_data(TEST_FOUR_NODE_GRAPH)

    assert graph.contains_router("10.69.0.1") == True
    assert graph.contains_router("10.69.0.2") == True
    assert graph.contains_router("10.69.0.3") == True
    assert graph.contains_router("10.70.0.4") == True

    assert graph.contains_router("10.69.0.5") == False
    assert graph.contains_router("zzz") == False


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
                "exit": False,
                "exit_path": ["10.69.0.1", "10.69.0.2"],
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
                "exit": True,
                "exit_path": ["10.69.0.2"],
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
                "exit": False,
                "exit_path": ["10.69.0.3", "10.69.0.2"],
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
                    ]
                },
                "exit": False,
                "exit_path": ["10.70.0.4", "10.69.0.3", "10.69.0.2"],
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

    assert graph._convert_subgraph_to_json(
        graph._graph.subgraph(["10.69.0.2", "10.69.0.3"])
    ) == {
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
                "exit": True,
                "exit_path": ["10.69.0.2"],
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
                "exit": False,
                "exit_path": ["10.69.0.3", "10.69.0.2"],
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
                "exit": False,
                "exit_path": ["10.69.0.1", "10.69.0.2"],
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
                "exit": True,
                "exit_path": ["10.69.0.2"],
                "missing_edges": 1,
            },
        ],
        "edges": [
            {"from": "10.69.0.1", "to": "10.69.0.2", "weight": 10},
            {"from": "10.69.0.2", "to": "10.69.0.1", "weight": 10},
        ],
    }


def test_multiple_exits():
    graph = OSPFGraph(load_data=False)
    graph.update_link_data(TEST_NINE_NODE_GRAPH)

    output = graph._convert_subgraph_to_json(graph._graph)
    exit_paths = {node["id"]: node["exit_path"] for node in output["nodes"]}
    assert exit_paths == {
        "10.69.0.1": ["10.69.0.1", "10.69.0.2"],
        "10.69.0.2": ["10.69.0.2"],
        "10.69.0.3": ["10.69.0.3", "10.69.0.2"],
        "10.69.0.4": ["10.69.0.4", "10.69.0.3", "10.69.0.2"],
        "10.69.0.5": ["10.69.0.5", "10.69.0.1", "10.69.0.2"],
        "10.69.0.6": ["10.69.0.6", "10.69.0.7", "10.69.0.8"],
        "10.69.0.7": ["10.69.0.7", "10.69.0.8"],
        "10.69.0.8": ["10.69.0.8"],
        "10.69.0.9": ["10.69.0.9", "10.69.0.1", "10.69.0.2"],
    }

    egress_forest = graph._compute_egress_forest()
    assert nx.is_forest(egress_forest)
    exit_tree_node_2 = egress_forest.subgraph(
        nx.node_connected_component(egress_forest.to_undirected(), "10.69.0.2")
    )
    assert len(exit_tree_node_2.nodes) == 6
    assert len(exit_tree_node_2.edges) == 5

    for node in exit_tree_node_2:
        if node == "10.69.0.2":
            assert exit_tree_node_2.out_degree(node) == 0
        else:
            assert exit_tree_node_2.out_degree(node) == 1

    assert list(exit_tree_node_2.out_edges("10.69.0.1"))[0] == (
        "10.69.0.1",
        "10.69.0.2",
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
    assert len(exit_tree_node_8.nodes) == 3
    assert len(exit_tree_node_8.edges) == 2

    assert exit_tree_node_8.out_degree("10.69.0.6") == 1
    assert exit_tree_node_8.out_degree("10.69.0.7") == 1
    assert exit_tree_node_8.out_degree("10.69.0.8") == 0

    assert list(exit_tree_node_8.out_edges("10.69.0.6"))[0] == (
        "10.69.0.6",
        "10.69.0.7",
    )
    assert list(exit_tree_node_8.out_edges("10.69.0.7"))[0] == (
        "10.69.0.7",
        "10.69.0.8",
    )
