import os

from flask import Flask, request
from flask_cors import CORS

from nycmesh_ospf_explorer.graph import OSPFGraph

app = Flask(__name__)
CORS(app)


if "FLASK_ENV" in os.environ:
    graph = OSPFGraph()


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

    graph.update_if_needed()
    if not graph.contains_router(router_id):
        return str(f"Couldn't find router with ID: {router_id}"), 404

    return {
        **graph.get_neighbors_dict(router_id, neighbor_depth),
        "updated": int(graph.last_updated.timestamp()),
    }
