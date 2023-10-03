import cytoscape from "cytoscape";
import CytoscapeStyles from "../styles/CytoscapeStyles";
import CytoscapeComponent from "react-cytoscapejs";
import React, { useEffect, useState } from "react";
import euler from "cytoscape-euler";
import dagre from "cytoscape-dagre";

cytoscape.use(euler);
cytoscape.use(dagre);

export function NodeGraph(props) {
  const { graphElements, onNodeSelected, refitDependencies, layoutName } = props;

  const [cyRef, updateCyRef] = useState(null);

  const layoutProps = {
    name: layoutName, // TODO Reverse dagre and see if it gets better
    randomize: true,
    // Prevent the user grabbing nodes during the layout
    ungrabifyWhileSimulating: true,
    animate: "end",
    animationDuration: 500,
    springLength: 120,
    gravity: -10,
    theta: 0.2,
  };

  useEffect(() => {
    if (cyRef) {
      cyRef.on("select", "node", (_evt) => {
        let nodeId = _evt.target.id().toString();
        if (nodeId.endsWith("_missing")) {
          nodeId = nodeId.replace("_missing", "");
        }
        onNodeSelected(nodeId);
      });

      cyRef.on("mouseover", "node", (event) => {
        if (event.cy.container()) {
          event.cy.container().style.cursor = "pointer";
        }
      });

      cyRef.on("mouseout", "node", (event) => {
        if (event.cy.container()) {
          event.cy.container().style.cursor = "default";
        }
      });
    }
  }, [cyRef]);
  function refitGraph() {
    if (cyRef) {
      cyRef.layout(layoutProps).run();
      cyRef.fit();
    }
  }

  useEffect(() => {
    refitGraph();
  }, [...refitDependencies, cyRef]);

  return (
    <CytoscapeComponent
      className={"rounded graph-view mb-3"}
      elements={graphElements}
      style={{ width: "100%", height: "35rem" }}
      stylesheet={CytoscapeStyles}
      layout={layoutProps}
      cy={(cy) => {
        updateCyRef(cy);
      }}
    />
  );
}
