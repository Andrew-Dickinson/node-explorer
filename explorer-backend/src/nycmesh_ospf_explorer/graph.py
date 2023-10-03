import datetime
import os
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx
import requests
from dotenv import load_dotenv
from nycmesh_ospf_explorer.utils import compute_nn_from_ip, compute_nn_string_from_ip

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
        self._egress_forest = self._compute_egress_forest(self._graph)
        self._egress_return_paths = self._compute_egress_return_paths(
            self._graph, self._egress_forest
        )

    def _drop_no_metadata_nodes(self):
        nodes_to_drop = [node for node in self._graph.nodes if node not in self.routers]
        for node in nodes_to_drop:
            self._graph.remove_node(node)

        if nodes_to_drop:
            print(
                f"WARN: Dropped the following nodes {nodes_to_drop} becauase we didn't find router entries for them. "
                f"However, they appeared as links from other nodes. Check OSPF DB consistency."
            )

    @staticmethod
    def _create_graph_with_exit_placeholders_from_graph(
        graph: nx.MultiDiGraph,
    ) -> Tuple[nx.MultiDiGraph, Set[Tuple[str, dict]]]:
        graph_with_exit_placeholders: nx.MultiDiGraph = graph.copy()

        exit_placeholders = set()
        nodes_with_exit = [
            node
            for node in graph.nodes.data()
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

    @staticmethod
    def _compute_egress_forest(graph: nx.MultiDiGraph) -> nx.DiGraph:
        (
            graph_with_exit_placeholders,
            exit_placeholders,
        ) = OSPFGraph._create_graph_with_exit_placeholders_from_graph(graph)
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

    @staticmethod
    def _compute_egress_return_paths(
        graph: nx.MultiDiGraph,
        egress_forest: nx.DiGraph,
    ) -> Dict[str, List[Tuple[str, Optional[int]]]]:
        nodes_with_exit = [
            node[0]
            for node in graph.nodes.data()
            if any(
                network["id"] == "0.0.0.0/0"
                for network in node[1].get("networks", {}).get("external", [])
            )
        ]

        shortest_paths_by_exit_node = {
            exit_node: nx.algorithms.single_source_dijkstra_path(graph, exit_node)
            for exit_node in nodes_with_exit
        }

        egreess_return_paths = {}
        for node in graph:
            egress_path = OSPFGraph._get_exit_path_for_node(egress_forest, node)
            if egress_path is not None:
                exit_node_used = egress_path[-2][0]  # -1 is the exit placeholder, -2 is exit node
                egress_return_path = shortest_paths_by_exit_node[exit_node_used][node]
                egress_return_path_with_costs = [(egress_return_path[0], None)] + [
                    (node2, min(edge["weight"] for edge in graph[node1][node2].values()))
                    for node1, node2 in zip(egress_return_path, egress_return_path[1:])
                ]
                egreess_return_paths[node] = egress_return_path_with_costs
            else:
                egreess_return_paths[node] = None

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
        self,
        subgraph: nx.MultiDiGraph,
        neighbor_set: Set = None,
        include_networks: bool = True,
        whole_graph: nx.MultiDiGraph = None,
        egress_forest: nx.DiGraph = None,
        egress_return_paths: Dict[str, List[Tuple[str, int]]] = None,
    ) -> dict:
        if whole_graph is None:
            whole_graph = self._graph

        if egress_return_paths is None:
            egress_return_paths = self._egress_return_paths

        if egress_forest is None:
            egress_forest = self._egress_forest

        output = {"nodes": [], "edges": []}

        for node_id in subgraph.nodes:
            node = subgraph.nodes[node_id]

            exit_path = self._get_exit_path_for_node(egress_forest, node_id)
            return_path = egress_return_paths[node_id] if node_id in egress_return_paths else None

            output_node = {
                "id": node_id,
                "nn": None,
                "nn_int": None,
                "exit_network_cost": exit_path[-1][1] if exit_path else None,
                "exit_paths": {
                    "outbound": exit_path[:-1] if exit_path else None,
                    "return": return_path,
                },
                "missing_edges": sum(
                    1 for edge in whole_graph.out_edges(node_id) if edge not in subgraph.edges
                ),
            }

            try:
                output_node["nn"] = compute_nn_string_from_ip(node_id)
                output_node["nn_int"] = compute_nn_from_ip(node_id)
            except ValueError:
                pass

            if neighbor_set:
                output_node["in_neighbor_set"] = node_id in neighbor_set

            if include_networks:
                output_node["networks"] = node["networks"]

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
            if os.environ.get("DEBUG") == "true":
                print("In debug mode, skipping update")
                return

            self.update_link_data()

    def contains_router(self, router_id: str):
        return router_id in self._graph

    def get_edges_for_node_pair(self, router1_id: str, router2_id: str):
        try:
            return [
                {"from": router1_id, "to": router2_id, **edge_props}
                for edge_props in self._graph[router1_id][router2_id].values()
            ]
        except KeyError:
            return []

    def get_networks_for_node(self, router_id: str) -> dict:
        return self._graph.nodes[router_id]["networks"]

    @staticmethod
    def _get_exit_path_for_node(egress_forest: nx.DiGraph, router_id: str):
        if not router_id in egress_forest.nodes:
            return None

        def recurse_exit_path(current_path):
            current_node = current_path[-1][0]
            out_edges = egress_forest[current_node].items()

            if len(out_edges) == 0:
                # If there is nowhere else to go, this must be the exit
                return current_path

            assert len(out_edges) == 1
            next_node, edge_data = out_edges.__iter__().__next__()
            current_path.append((next_node, edge_data["weight"]))

            return recurse_exit_path(current_path)

        return recurse_exit_path([(router_id, None)])

    def get_exit_path_for_node(self, router_id: str) -> List[str]:
        return self._get_exit_path_for_node(self._egress_forest, router_id)

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

    @staticmethod
    def _get_upstream_nodes(forest: nx.DiGraph, node) -> Set[str]:
        upstream_nodes = set()
        for n in forest.pred[node]:
            upstream_nodes.add(n)
            upstream_nodes = upstream_nodes.union(OSPFGraph._get_upstream_nodes(forest, n))

        return upstream_nodes

    def _get_graph_without_nodes_and_edges(
        self, nodes: List[str], edges: List[Tuple[str, str]]
    ) -> nx.MultiDiGraph:
        modified_graph: nx.MultiDiGraph = self._graph.copy()

        for edge in edges:
            # Ensure we remove all edges, since there could be more than one for each direction
            for i in range(len(modified_graph[edge[0]][edge[1]])):
                modified_graph.remove_edge(edge[0], edge[1])
            for i in range(len(modified_graph[edge[1]][edge[0]])):
                modified_graph.remove_edge(edge[1], edge[0])

        for node in nodes:
            modified_graph.remove_node(node)

        return modified_graph

    def get_dependent_nodes(
        self, nodes: List[str], edges: List[Tuple[str, str]]
    ) -> Tuple[Set[str], Set[str]]:
        """
        Compute partially and fully dependent nodes of the union of the input node and edge lists

        Input edges are not processed according to the traffic they carry, but rather the pair of
        nodes they connect. That is, the direction of the edges specified doesn't matter, nor does
        the selection of a specific edge when dealing with multi-edge scenarios. All edges directly
        connecting the pair of nodes will be considered, even if only a single edge is provided
        """
        dependent_nodes = set({})
        for node in nodes:
            dependent_nodes = dependent_nodes.union(
                self._get_upstream_nodes(self._egress_forest, node)
            )

        for edge in edges:
            if self._egress_forest.has_edge(edge[0], edge[1]):
                dependent_nodes = dependent_nodes.union(
                    self._get_upstream_nodes(self._egress_forest, edge[0])
                )
            if self._egress_forest.has_edge(edge[1], edge[0]):
                dependent_nodes = dependent_nodes.union(
                    self._get_upstream_nodes(self._egress_forest, edge[1])
                )

        for candidate_dependent_node, egress_return_path in self._egress_return_paths.items():
            egress_path_nodes_only = [egress_node for egress_node, _ in egress_return_path]
            for egress_node in egress_path_nodes_only:
                for dropped_node in nodes:
                    if egress_node == dropped_node and candidate_dependent_node != dropped_node:
                        dependent_nodes.add(candidate_dependent_node)

            for egress_node1, egress_node2 in zip(
                egress_path_nodes_only, egress_path_nodes_only[1:]
            ):
                for dropped_edge in edges:
                    if set(dropped_edge) == {egress_node1, egress_node2}:
                        dependent_nodes.add(candidate_dependent_node)

        new_egress_forest = self._compute_egress_forest(
            self._get_graph_without_nodes_and_edges(nodes, edges)
        )

        partially_dependent_nodes: set[str] = {
            node for node in dependent_nodes if node in new_egress_forest.nodes
        }
        fully_dependent_nodes: set[str] = dependent_nodes.difference(partially_dependent_nodes)

        return partially_dependent_nodes, fully_dependent_nodes

    def simulate_outage(self, nodes: List[str], edges: List[Tuple[str, str]]) -> dict:
        nodes_of_removed_edges = set()
        for edge in edges:
            nodes_of_removed_edges.add(edge[0])
            nodes_of_removed_edges.add(edge[1])

        partially_dependent_nodes, fully_dependent_nodes = self.get_dependent_nodes(nodes, edges)

        # It's not crazy efficient to do this a second time, but it makes the code simpler sooooo...
        modified_graph = self._get_graph_without_nodes_and_edges(nodes, edges)

        modified_egress_forest = self._compute_egress_forest(modified_graph)
        modified_egress_return_paths = self._compute_egress_return_paths(
            modified_graph, modified_egress_forest
        )

        nodes_to_include_egress_paths_for = (
            partially_dependent_nodes | fully_dependent_nodes | nodes_of_removed_edges
        )
        nodes_to_display = nodes_to_include_egress_paths_for.copy()

        # Add in egress path nodes to the nodes_to_display
        for router_id in nodes_to_include_egress_paths_for:
            egress_outbound_path = self._get_exit_path_for_node(modified_egress_forest, router_id)
            try:
                egress_return_path = modified_egress_return_paths[router_id]
            except KeyError:
                egress_return_path = None

            for egress_path_half in [egress_outbound_path, egress_return_path]:
                # If the node is now isolated, there might be no path
                if egress_path_half:
                    nodes_to_display |= set(node_id for node_id, edge_cost in egress_path_half)

        impacted_subgraph = self._convert_subgraph_to_json(
            modified_graph.subgraph(nodes_to_display),
            whole_graph=modified_graph,
            egress_forest=modified_egress_forest,
            egress_return_paths=modified_egress_return_paths,
            include_networks=False,
        )

        all_removed_edges = edges.copy()
        for node in nodes:
            for other_node in set(self._graph[node]):
                if other_node in nodes_to_display:
                    all_removed_edges.append([node, other_node])

        for edge in sorted(list(all_removed_edges)):
            impacted_subgraph["edges"].append({"from": edge[0], "to": edge[1], "weight": None})
            impacted_subgraph["edges"].append({"from": edge[1], "to": edge[0], "weight": None})

        for node in nodes:
            removed_node = {
                "exit_network_cost": None,
                "exit_paths": {"outbound": None, "return": None},
                "id": node,
                "missing_edges": 0,
                "nn": None,
                "nn_int": None,
            }

            try:
                removed_node["nn"] = compute_nn_string_from_ip(node)
                removed_node["nn_int"] = compute_nn_from_ip(node)
            except ValueError:
                pass

            impacted_subgraph["nodes"].append(removed_node)

        return {
            **impacted_subgraph,
            "outage_lists": {
                "removed": sorted(nodes),
                "offline": sorted(list(fully_dependent_nodes - set(nodes))),
                "rerouted": sorted(list(partially_dependent_nodes)),
            },
        }
