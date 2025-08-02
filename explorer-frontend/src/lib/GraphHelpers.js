function computeNodePairId(edge) {
  const nodeIds = [edge.to, edge.from];
  nodeIds.sort();
  return nodeIds.join("->");
}

export function getNodeDetails(graphData, nodeId) {
  for (const node of graphData.nodes) {
    if (node.id === nodeId) return node;
  }

  return null;
}

function computeEdgeCosts(edges) {
  const edgeCosts = {};

  // Collect and organize the edge cost data
  for (const edge of edges) {
    const nodePairId = computeNodePairId(edge);
    if (!(nodePairId in edgeCosts)) {
      edgeCosts[nodePairId] = { individualCosts: {} };
      edgeCosts[nodePairId].individualCosts[edge.from] = [];
      edgeCosts[nodePairId].individualCosts[edge.to] = [];
    }

    edgeCosts[nodePairId].individualCosts[edge.from].push(edge.weight);
  }

  // Sort each list of costs
  for (const edgePair of Object.keys(edgeCosts)) {
    const costsForThisPair = edgeCosts[edgePair].individualCosts;
    for (const nodeId of Object.keys(costsForThisPair)) {
      costsForThisPair[nodeId].sort().reverse();
    }
  }

  // Compute the lowest cost edge for each pair of nodes
  for (const edgePair of Object.keys(edgeCosts)) {
    edgeCosts[edgePair].lowestCost = 100000000;
    const costsForThisPair = edgeCosts[edgePair].individualCosts;
    for (const nodeId of Object.keys(costsForThisPair)) {
      if (costsForThisPair[nodeId][0] < edgeCosts[edgePair].lowestCost)
        edgeCosts[edgePair].lowestCost = costsForThisPair[nodeId][0];
    }
  }

  // Identify the asymmetric nodes
  for (const edgePair of Object.keys(edgeCosts)) {
    edgeCosts[edgePair].invalid = false;

    const costArraysForThisPair = Object.values(edgeCosts[edgePair].individualCosts);
    if (costArraysForThisPair[0].length !== costArraysForThisPair[1].length) {
      edgeCosts[edgePair].invalid = true;
      continue;
    }

    for (let i = 0; i < costArraysForThisPair[0].length; ++i) {
      if (costArraysForThisPair[0][i] !== costArraysForThisPair[1][i]) {
        edgeCosts[edgePair].invalid = true;
      }
    }
  }

  return edgeCosts;
}

function isEdgeInPath(edge, path) {
  const sourceEgressPosition = path.indexOf(edge[0]);
  const targetEgressPosition = path.indexOf(edge[1]);

  return (
    targetEgressPosition - sourceEgressPosition === 1 &&
    sourceEgressPosition !== -1 &&
    targetEgressPosition !== -1
  );
}

export function convertOSPFToCytoScapeElements(graphDataInput, settings, selectedNodeId) {
  let graphData = structuredClone(graphDataInput);
  const outputElements = [];
  const edgeCosts = computeEdgeCosts(graphData.edges);
  const includedNodeIds = [];

  let selectedNode = null;
  for (const node of graphData.nodes) {
    if (node.id === selectedNodeId) selectedNode = node;
  }

  const missingEdgeCounts = {};

  for (const node of graphData.nodes) {
    missingEdgeCounts[node.id] = node.missing_edges;
    if (!settings.includeEgress && !node.in_neighbor_set) continue;
    const classes = ["primaryNode"];
    if (node.id === selectedNode) classes.push("selected");
    if (node.exit_paths.outbound.length === 1) classes.push("exit");
    includedNodeIds.push(node.id);
    outputElements.push({
      data: { id: node.id, label: node.nn ?? node.id },
      classes: classes,
      selected: node.id === selectedNodeId,
    });
  }

  const egressOutboundPath =
    selectedNode?.exit_paths?.outbound.map(([node_id, cost]) => node_id) ?? [];
  const egressReturnPath = selectedNode?.exit_paths?.return.map(([node_id, cost]) => node_id) ?? [];

  let nodesWithHiddenEgressNeighbors = [];
  if (settings.lowestCostOnly) {
    for (const edgeId of Object.keys(edgeCosts)) {
      const nodes = edgeId.split("->");
      const invalid = edgeCosts[edgeId].invalid;
      const reversedEdge = nodes.slice().reverse();

      if (includedNodeIds.indexOf(nodes[0]) === -1 || includedNodeIds.indexOf(nodes[1]) === -1) {
        missingEdgeCounts[nodes[0]] += 1;
        missingEdgeCounts[nodes[1]] += 1;
        if (includedNodeIds.indexOf(nodes[0]) !== -1 || includedNodeIds.indexOf(nodes[1]) !== -1) {
          if (isEdgeInPath(nodes, egressOutboundPath) || isEdgeInPath(nodes, egressReturnPath)) {
            nodesWithHiddenEgressNeighbors.push(
              includedNodeIds.indexOf(nodes[1]) === -1 ? nodes[0] : nodes[1]
            );
          }
        }
        continue;
      }

      const classes = [];
      if (settings.bothDirections) classes.push("directionalEdge");
      if (invalid) classes.push("invalidCosts");

      let label = edgeCosts[edgeId].individualCosts[nodes[0]][0];

      if (!settings.bothDirections && invalid) {
        label = "Mismatch";
      }

      let primaryDirectionClasses = [];
      const secondaryDirectionClasses = [];

      if (isEdgeInPath(nodes, egressOutboundPath) || isEdgeInPath(nodes, egressReturnPath)) {
        primaryDirectionClasses.push("egress");
      }

      if (
        isEdgeInPath(reversedEdge, egressOutboundPath) ||
        isEdgeInPath(reversedEdge, egressReturnPath)
      ) {
        secondaryDirectionClasses.push("egress");
      }

      if (!settings.bothDirections) {
        primaryDirectionClasses = primaryDirectionClasses.concat(secondaryDirectionClasses);
      }

      outputElements.push({
        data: {
          source: nodes[0],
          target: nodes[1],
          label: label,
        },
        classes: classes.concat(primaryDirectionClasses),
      });

      if (settings.bothDirections) {
        label = edgeCosts[edgeId].individualCosts[nodes[1]][0];
        outputElements.push({
          data: {
            source: nodes[1],
            target: nodes[0],
            label: label,
          },
          classes: classes.concat(secondaryDirectionClasses),
        });
      }
    }
  } else {
    for (const edge of graphData.edges) {
      const costData = edgeCosts[computeNodePairId(edge)];

      if (includedNodeIds.indexOf(edge.from) === -1 || includedNodeIds.indexOf(edge.to) === -1) {
        if (costData.individualCosts[edge.from][0] === edge.weight) {
          missingEdgeCounts[edge.from] += 1;
          if (includedNodeIds.indexOf(edge.from) !== -1) {
            if (
              isEdgeInPath([edge.from, edge.to], egressOutboundPath) ||
              isEdgeInPath([edge.from, edge.to], egressReturnPath) ||
              isEdgeInPath([edge.to, edge.from], egressOutboundPath) ||
              isEdgeInPath([edge.to, edge.from], egressReturnPath)
            ) {
              nodesWithHiddenEgressNeighbors.push(edge.from);
            }
          }
        }
        continue;
      }

      if (settings.bothDirections || edge.from < edge.to) {
        const classes = [];
        if (settings.bothDirections) classes.push("directionalEdge");
        if (costData.invalid) classes.push("invalidCosts");

        let label = edge.weight;
        if (!settings.bothDirections && costData.invalid) {
          label = "Mismatch";
        }

        if (costData.individualCosts[edge.from][0] === edge.weight) {
          if (
            isEdgeInPath([edge.from, edge.to], egressOutboundPath) ||
            isEdgeInPath([edge.from, edge.to], egressReturnPath)
          ) {
            classes.push("egress");
          }
          if (!settings.bothDirections) {
            if (
              isEdgeInPath([edge.to, edge.from], egressOutboundPath) ||
              isEdgeInPath([edge.to, edge.from], egressReturnPath)
            ) {
              classes.push("egress");
            }
          }
        }

        outputElements.push({
          data: {
            // id: edge.from + "->" + edge.to,
            source: edge.from,
            target: edge.to,
            label: label,
          },
          classes: classes,
        });
      }
    }
  }

  for (const nodeId of Object.keys(missingEdgeCounts)) {
    if (missingEdgeCounts[nodeId] > 0 && includedNodeIds.indexOf(nodeId) !== -1) {
      const edgeClasses = ["dashedEdge"];
      if (nodesWithHiddenEgressNeighbors.indexOf(nodeId) !== -1) {
        edgeClasses.push("egress");
        edgeClasses.push("directionalEdge");
      }
      outputElements.push({
        data: {
          id: nodeId + "_missing",
          label: missingEdgeCounts[nodeId] + " more",
        },
        classes: ["invisibleNode"],
      });
      outputElements.push({
        data: {
          source: nodeId,
          target: nodeId + "_missing",
        },
        classes: edgeClasses,
      });
    }
  }

  return outputElements;
}

export function convertOutageToCytoScapeElements(graphDataInput) {
  let graphData = structuredClone(graphDataInput);
  const outputElements = [];

  const edgeCosts = computeEdgeCosts(graphData.edges);

  for (const node of graphData.nodes) {
    const nodeClasses = ["primaryNode"];

    if (graphData.outage_lists.offline.indexOf(node.id) !== -1) nodeClasses.push("offline");
    if (graphData.outage_lists.removed.indexOf(node.id) !== -1) nodeClasses.push("removed");
    if (graphData.outage_lists.rerouted.indexOf(node.id) !== -1) nodeClasses.push("rerouted");

    if (node.exit_paths.outbound) {
      if (node.exit_paths.outbound.length === 1) {
        nodeClasses.push("exit");
      } else {
        const egressEdge = { from: node.id, to: node.exit_paths.outbound[1][0] };
        const edgeClasses = ["directionalEdge"];
        // if (edgeCosts[computeNodePairId(egressEdge)][node.id] === null)
        //   edgeClasses.push("dashedEdge");

        outputElements.push({
          data: {
            source: egressEdge.from,
            target: egressEdge.to,
            id: egressEdge.from + "->" + egressEdge.to,
            label: "",
          },
          classes: edgeClasses,
        });
      }
    }

    outputElements.push({
      data: { id: node.id, label: node.nn ?? node.id },
      classes: nodeClasses,
    });

    for (const edgeID of Object.keys(edgeCosts)) {
      const edgeNodes = Object.keys(edgeCosts[edgeID].individualCosts);
      if (edgeCosts[edgeID].lowestCost === null) {
        const edgeClasses = ["dashedEdge", "boldRedText"];

        outputElements.push({
          data: {
            source: edgeNodes[0],
            target: edgeNodes[1],
            label: "X",
            id: edgeID,
          },
          classes: edgeClasses,
        });
      }

      const offlineNodes = graphData.outage_lists.offline;
      if (offlineNodes.indexOf(edgeNodes[0]) !== -1 || offlineNodes.indexOf(edgeNodes[1]) !== -1) {
        outputElements.push({
          data: {
            source: edgeNodes[0],
            target: edgeNodes[1],
            id: edgeID,
          },
          // classes: edgeClasses,
        });
      }
    }
  }

  // return [];
  return outputElements;
}
