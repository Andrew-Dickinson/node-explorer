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
        self._egress_return_paths = self._compute_egress_return_paths()

    def _drop_no_metadata_nodes(self):
        nodes_to_drop = [node for node in self._graph.nodes if node not in self.routers]
        for node in nodes_to_drop:
            self._graph.remove_node(node)

        if nodes_to_drop:
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
        graph_with_exit_placeholders = graph_with_exit_placeholders.reverse()

        paths = nx.algorithms.multi_source_dijkstra_path(
            graph_with_exit_placeholders, exit_placeholders
        )

        egress_forest = nx.DiGraph()
        for node_id, egress_path in paths.items():
            if len(egress_path) > 1:
                egress_forest.add_edge(
                    node_id,
                    egress_path[-2],
                    weight=min(
                        edge[1]["weight"]
                        for edge in graph_with_exit_placeholders[egress_path[-2]][node_id].items()
                    ),
                )

        return egress_forest

    def _compute_egress_return_paths(self) -> Dict[str, List[str]]:
        nodes_with_exit = [
            node[0]
            for node in self._graph.nodes.data()
            if any(
                network["id"] == "0.0.0.0/0"
                for network in node[1].get("networks", {}).get("external", [])
            )
        ]

        shortest_paths_by_exit_node = {
            exit_node: nx.algorithms.single_source_dijkstra_path(self._graph, exit_node)
            for exit_node in nodes_with_exit
        }

        egreess_return_paths = {}
        for node in self._graph:
            egress_path = self.get_exit_path_for_node(node)
            exit_node_used = egress_path[-2][0]  # -1 is the exit placeholder, -2 is exit node
            egress_return_path = shortest_paths_by_exit_node[exit_node_used][node]
            egress_return_path_with_costs = [(egress_return_path[0], None)] + [
                (node2, min(edge["weight"] for edge in self._graph[node1][node2].values()))
                for node1, node2 in zip(egress_return_path, egress_return_path[1:])
            ]
            egreess_return_paths[node] = egress_return_path_with_costs

        return egreess_return_paths

    def _get_neighbors_subgraph(self, router_id: str, neighbor_depth: int = 1) -> nx.MultiDiGraph:
        neighbor_set = self._get_neighbors_set(router_id, neighbor_depth)
        return self._graph.subgraph(neighbor_set).copy()

    def _get_neighbors_set(self, router_id: str, neighbor_depth: int = 1) -> Set:
        node_set = {router_id}
        for i in range(neighbor_depth):
            new_nodes = set({})
            for already_neighbor_node in node_set:
                for node in self._graph.neighbors(already_neighbor_node):
                    new_nodes.add(node)

            node_set = node_set.union(new_nodes)

        return node_set

    def _convert_subgraph_to_json(
        self, subgraph: nx.MultiDiGraph, neighbor_set: Set = None
    ) -> dict:
        output = {"nodes": [], "edges": []}

        for node_id in subgraph.nodes:
            node = subgraph.nodes[node_id]

            exit_path = self.get_exit_path_for_node(node_id)
            return_path = self._egress_return_paths[node_id]

            output_node = {
                "id": node_id,
                "nn": None,
                "nn_int": None,
                "networks": node["networks"],
                "exit_network_cost": exit_path[-1][1],
                "exit_paths": {
                    "outbound": exit_path[:-1],
                    "return": return_path,
                },
                "missing_edges": sum(
                    1 for edge in self._graph.out_edges(node_id) if edge not in subgraph.edges
                ),
            }

            try:
                output_node["nn"] = compute_nn_string_from_ip(node_id)
                output_node["nn_int"] = compute_nn_from_ip(node_id)
            except ValueError:
                pass

            if neighbor_set:
                output_node["in_neighbor_set"] = node_id in neighbor_set

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
            current_node = current_path[-1][0]
            out_edges = self._egress_forest[current_node].items()

            if len(out_edges) == 0:
                # If there is nowhere else to go, this must be the exit
                return current_path

            assert len(out_edges) == 1
            next_node, edge_data = out_edges.__iter__().__next__()
            current_path.append((next_node, edge_data["weight"]))

            return recurse_exit_path(current_path)

        return recurse_exit_path([(router_id, None)])

    def get_neighbors_dict(
        self, router_id: str, neighbor_depth: int = 1, include_egress=False
    ) -> dict:
        neighbor_set = self._get_neighbors_set(router_id, neighbor_depth)
        nodes_to_include = neighbor_set

        if include_egress:
            egress_path_nodes_without_exit_placeholder = set(
                node_id for node_id, edge_cost in self.get_exit_path_for_node(router_id)[:-1]
            )
            egress_return_path_nodes = set(
                node_id for node_id, edge_cost in self._egress_return_paths[router_id]
            )
            nodes_to_include = (
                nodes_to_include
                | egress_path_nodes_without_exit_placeholder
                | egress_return_path_nodes
            )

        return self._convert_subgraph_to_json(self._graph.subgraph(nodes_to_include), neighbor_set)
