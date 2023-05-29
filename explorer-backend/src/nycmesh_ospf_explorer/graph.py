import datetime
import os
from typing import List, Tuple, Set, Dict

import networkx as nx
import requests

from dotenv import load_dotenv

from nycmesh_ospf_explorer.utils import compute_nn_string_from_ip, compute_nn_from_ip

load_dotenv()

API_URL = os.environ.get("API_URL", "http://api.andrew.mesh/api/v1/ospf/linkdb")


class OSPFGraph:
    def __init__(self, load_data=True):
        self.routers = {}
        self.networks = {}
        self.last_updated = datetime.datetime.fromtimestamp(0)

        self._graph = nx.MultiDiGraph()
        self._egress_forest = nx.DiGraph()

        if load_data:
            self.update_link_data()

    def _update_graph(self):
        self._graph = nx.MultiDiGraph()
        for router_id, router in self.routers.items():
            for other_router in router.get("links", {}).get("router", []):
                self._graph.add_edge(router_id, other_router["id"], weight=other_router["metric"])
            is_exit = any(
                link["id"] == "0.0.0.0/0" for link in router.get("links", {}).get("external", [])
            )

            network_connected_routers = []
            for network_link_info in router.get("links", {}).get("network", []):
                network_cidr = network_link_info["id"]
                cost = network_link_info["metric"]
                for other_router_id in self.networks[network_cidr]["routers"]:
                    if other_router_id != router_id:
                        network_connected_routers.append({"id": other_router_id, "metric": cost})
                        self._graph.add_edge(router_id, other_router_id, weight=cost)

            networks = router.get("links").copy()
            if "network" in networks:
                del networks["network"]

            if network_connected_routers:
                networks["router"] = networks.get("router", [])
                networks["router"].extend(network_connected_routers)

            self._graph.add_node(router_id, networks=networks)

        self._drop_no_metadata_nodes()

        # Get only the largest connected component
        largest_connected = max(nx.connected_components(self._graph.to_undirected()), key=len)
        self._graph = self._graph.subgraph(largest_connected).copy()
        self._egress_forest = self._compute_egress_forest()

    def _drop_no_metadata_nodes(self):
        nodes_to_drop = [node for node in self._graph.nodes if node not in self.routers]
        for node in nodes_to_drop:
            self._graph.remove_node(node)

        print(
            f"WARN: Dropped the following nodes {nodes_to_drop} becauase we didn't find router entries for them. "
            f"However, they appeared as links from other nodes. Check OSPF DB consistency."
        )

    def _create_graph_with_exit_placeholders(self) -> Tuple[nx.MultiDiGraph, Set[Tuple[str, dict]]]:
        graph_with_exit_placeholders: nx.MultiDiGraph = self._graph.copy()

        exit_placeholders = set()
        nodes_with_exit = [
            node
            for node in self._graph.nodes.data()
            if any(
                network["id"] == "0.0.0.0/0"
                for network in node[1].get("networks", {}).get("external", [])
            )
        ]

        for node in nodes_with_exit:
            external_costs = {
                link["id"]: link.get("metric") if "metric" in link else link.get("metric2")
                for link in node[1].get("networks", {}).get("external", [])
            }
            direct_exit_cost = external_costs.get("0.0.0.0/0")
            if direct_exit_cost is not None:
                graph_with_exit_placeholders.add_node(node[0] + "_0.0.0.0/0")
                graph_with_exit_placeholders.add_edge(
                    node[0],
                    node[0] + "_0.0.0.0/0",
                    weight=direct_exit_cost,
                )
                graph_with_exit_placeholders.add_edge(
                    node[0] + "_0.0.0.0/0",
                    node[0],
                    weight=direct_exit_cost,
                )
                exit_placeholders.add(node[0] + "_0.0.0.0/0")

        return graph_with_exit_placeholders, exit_placeholders

    def _compute_egress_forest(self) -> nx.DiGraph:
        (
            graph_with_exit_placeholders,
            exit_placeholders,
        ) = self._create_graph_with_exit_placeholders()
        paths = nx.algorithms.multi_source_dijkstra_path(
            graph_with_exit_placeholders, exit_placeholders
        )

        egress_forest = nx.DiGraph(
            (node_id, egress_path[-2])
            for node_id, egress_path in paths.items()
            if len(egress_path) > 1
        )

        return egress_forest

    def _get_neighbors_subgraph(self, router_id: str, neighbor_depth: int = 1) -> nx.MultiDiGraph:
        node_set = {router_id}
        for i in range(neighbor_depth):
            new_nodes = set({})
            for already_neighbor_node in node_set:
                for node in self._graph.neighbors(already_neighbor_node):
                    new_nodes.add(node)

            node_set = node_set.union(new_nodes)

        return self._graph.subgraph(node_set).copy()

    def _convert_subgraph_to_json(self, subgraph: nx.MultiDiGraph) -> dict:
        output = {"nodes": [], "edges": []}

        for node_id in subgraph.nodes:
            node = subgraph.nodes[node_id]
            output_node = {
                "id": node_id,
                "nn": None,
                "nn_int": None,
                "networks": node["networks"],
                "exit_path": self.get_exit_path_for_node(node_id),
                "missing_edges": sum(
                    1 for edge in self._graph.out_edges(node_id) if edge not in subgraph.edges
                ),
            }

            try:
                output_node["nn"] = compute_nn_string_from_ip(node_id)
                output_node["nn_int"] = compute_nn_from_ip(node_id)
            except ValueError:
                pass

            output["nodes"].append(output_node)

        for edge in subgraph.edges:
            output["edges"].append(
                {
                    "from": edge[0],
                    "to": edge[1],
                    "weight": subgraph.get_edge_data(*edge[:2])[edge[2]]["weight"],
                }
            )

        return output

    def update_link_data(self, json_link_data: dict = None):
        if json_link_data is None:
            try:
                json_link_data = requests.get(API_URL).json()
            except requests.exceptions.RequestException:
                raise RuntimeError(
                    f"Error loading graph data from {API_URL}\nDo you have connectivity to that endpoint?"
                )

        self.last_updated = datetime.datetime.fromtimestamp(json_link_data["updated"])
        self.routers = json_link_data["areas"]["0.0.0.0"]["routers"]
        self.networks = json_link_data["areas"]["0.0.0.0"]["networks"]

        self._update_graph()

    def update_if_needed(self, age_limit=datetime.timedelta(minutes=1)):
        if self.last_updated < datetime.datetime.now() - age_limit:
            self.update_link_data()

    def contains_router(self, router_id: str):
        return router_id in self._graph

    def get_networks_for_node(self, router_id: str) -> dict:
        return self._graph.nodes[router_id]["networks"]

    def get_exit_path_for_node(self, router_id: str) -> List[str]:
        def recurse_exit_path(current_path):
            current_node = current_path[-1]
            out_edges = list(self._egress_forest.out_edges(current_node))

            if len(out_edges) == 0:
                # If there is nowhere else to go, this must be the exit
                return current_path

            next_node = out_edges[0][1]
            current_path.append(next_node)

            return recurse_exit_path(current_path)

        return recurse_exit_path([router_id])[:-1]  # Remove the exit placeholder

    def get_neighbors_dict(self, router_id: str, neighbor_depth: int = 1) -> dict:
        return self._convert_subgraph_to_json(
            self._get_neighbors_subgraph(router_id, neighbor_depth)
        )
