import datetime
import os

from flask import Flask, request
from flask_cors import CORS
from nycmesh_ospf_explorer.graph import OSPFGraph

app = Flask(__name__)
CORS(app)

if "FLASK_ENV" in os.environ:
    global_graph = OSPFGraph()
if os.environ.get("DEBUG") == "true":
    from test_graph import (
        TEST_NINE_NODE_GRAPH,
        TEST_NINE_NODE_GRAPH_WITH_ASYMMETRIC_COSTS,
        TEST_REAL_GRAPH_SEP_2023,
    )

    global_graph = OSPFGraph(load_data=False)
    global_graph.update_link_data(TEST_NINE_NODE_GRAPH)
    # graph.update_link_data(TEST_NINE_NODE_GRAPH_WITH_ASYMMETRIC_COSTS)
    # graph.update_link_data(TEST_REAL_GRAPH_SEP_2023)


def validate_nn(nn: str):
    try:
        network_num = int(nn)
    except ValueError as e:
        raise ValueError(f"Invalid network number: {nn}")

    if 0 < network_num > 8192:
        raise ValueError(f"Invalid network number: {nn}")

    return network_num


@app.route("/neighbors/<router_id>", methods=["GET"])
def get_neighbors(router_id):
    neighbor_depth = int(request.args.get("searchDistance", 1))
    include_egress = request.args.get("includeEgress", "false") == "true"

    request_graph = get_request_graph()

    if not request_graph.contains_router(router_id):
        return str(f"Couldn't find router with ID: {router_id}"), 404

    return {
        **request_graph.get_neighbors_dict(router_id, neighbor_depth, include_egress=include_egress),
        "updated": int(request_graph.last_updated.timestamp()),
    }


def get_request_graph():
    request_graph = global_graph
    if request.args.get("timestamp"):
        request_graph = OSPFGraph()
        request_graph.update_from_timestamp(
            datetime.datetime.fromtimestamp(int(request.args.get("timestamp")))
        )
    else:
        request_graph.update_if_needed()

    return request_graph

@app.route("/simulate-outage", methods=["GET"])
def simulate_outage():
    request_graph = get_request_graph()

    nodes_param = request.args.get("nodes", "")
    edges_param = request.args.get("edges", "")

    nodes = nodes_param.split(",") if nodes_param else []
    edges = [edge_str.split("->") for edge_str in edges_param.split(",")] if edges_param else []

    if not nodes and not edges:
        return str("Must provide at least one of: edges, nodes"), 400

    for node in nodes:
        if not request_graph.contains_router(node):
            return str(f"Couldn't find router with ID: {node}"), 400

    for edge in edges:
        for router_id in edge:
            if not request_graph.contains_router(router_id):
                return str(f"Couldn't find router with ID: {router_id}"), 400

        if edge[0] == edge[1]:
            return str(f"Self loops don't exist"), 400

        graph_edges = request_graph.get_edges_for_node_pair(edge[0], edge[1])
        if len(graph_edges) == 0:
            return str(f"Couldn't find edge connecting routers: {edge[0]} & {edge[1]}"), 400

    return {
        **request_graph.simulate_outage(nodes, edges),
        "updated": int(request_graph.last_updated.timestamp()),
    }


@app.route("/edges/<router1_id>/<router2_id>", methods=["GET"])
def get_edges(router1_id, router2_id):
    request_graph = get_request_graph()

    for router_id in [router1_id, router2_id]:
        if not request_graph.contains_router(router_id):
            return str(f"Couldn't find router with ID: {router_id}"), 404

    if router1_id == router2_id:
        return str(f"Self loops don't exist"), 404

    edges = request_graph.get_edges_for_node_pair(router1_id, router2_id)
    if len(edges) == 0:
        return str(f"Couldn't find edge connecting routers: {router1_id} & {router2_id}"), 404

    return {
        "edges": edges,
        "updated": int(request_graph.last_updated.timestamp()),
    }
