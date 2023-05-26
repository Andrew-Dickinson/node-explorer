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
      costsForThisPair[nodeId].sort();
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

export function convertToCytoScapeElements(graphData, settings, selectedNode) {
  const outputElements = [];
  const edgeCosts = computeEdgeCosts(graphData.edges);
  for (const node of graphData.nodes) {
    const classes = ["primaryNode"];
    if (node.id === selectedNode) classes.push("selected");
    if (node.exit) classes.push("exit");
    outputElements.push({
      data: { id: node.id, label: node.nn ?? node.id },
      classes: classes,
      selected: node.id === selectedNode,
    });
    if (node.missing_edges > 0) {
      outputElements.push({
        data: {
          id: node.id + "_missing",
          label: node.missing_edges + " more",
        },
        classes: ["invisibleNode"],
      });
      outputElements.push({
        data: {
          source: node.id,
          target: node.id + "_missing",
        },
        classes: ["dashedEdge"],
      });
    }
  }

  if (settings.lowestCostOnly) {
    for (const edgeId of Object.keys(edgeCosts)) {
      const nodes = edgeId.split("->");
      const invalid = edgeCosts[edgeId].invalid;

      const classes = [];
      if (settings.bothDirections) classes.push("directionalEdge");
      if (invalid) classes.push("invalidCosts");

      let label = edgeCosts[edgeId].individualCosts[nodes[0]][0];

      if (!settings.bothDirections && invalid) {
        label = "Mismatch";
      }

      outputElements.push({
        data: {
          source: nodes[0],
          target: nodes[1],
          label: label,
        },
        classes: classes,
      });

      if (settings.bothDirections) {
        label = edgeCosts[edgeId].individualCosts[nodes[1]][0];
        outputElements.push({
          data: {
            source: nodes[1],
            target: nodes[0],
            label: label,
          },
          classes: classes,
        });
      }
    }
  } else {
    for (const edge of graphData.edges) {
      if (settings.bothDirections || edge.from < edge.to) {
        const classes = [];
        if (settings.bothDirections) classes.push("directionalEdge");
        if (edgeCosts[computeNodePairId(edge)].invalid) classes.push("invalidCosts");

        let label = edge.weight;
        if (!settings.bothDirections && edgeCosts[computeNodePairId(edge)].invalid) {
          label = "Mismatch";
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

  return outputElements;
}
