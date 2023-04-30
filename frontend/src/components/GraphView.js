import React, { useEffect, useState } from "react";
import cytoscape from "cytoscape";
import CytoscapeComponent from "react-cytoscapejs";
import CytoscapeStyles from "../styles/CytoscapeStyles";
import euler from "cytoscape-euler";
import { Col, Row } from "reactstrap";
import GraphViewSettings from "./GraphViewSettings";
import SelectedNodeDetail from "./SelectedNodeDetail";
import JSONDataAccordion from "./JSONDataAccordion";
import {
  convertToCytoScapeElements,
  getNodeDetails,
} from "../lib/GraphHelpers";

cytoscape.use(euler);

function GraphView(props) {
  const {
    graphData,
    searchDistance,
    updateSearchDistance,
    selectedNode,
    onNodeSelected,
  } = props;

  const [settings, setSettings] = useState({
    bothDirections: false,
    lowestCostOnly: true,
    searchDistance: searchDistance,
  });

  useEffect(() => {
    updateSearchDistance(settings.searchDistance);
  }, [settings]);

  useEffect(() => {
    updateSetting("searchDistance", searchDistance);
  }, [searchDistance]);

  function updateSetting(settingName, newValue) {
    setSettings((oldSettings) => {
      const newSettings = { ...oldSettings };
      newSettings[settingName] = newValue;
      return newSettings;
    });
  }

  const [cyRef, updateCyRef] = useState(null);

  useEffect(() => {
    if (cyRef) {
      cyRef.layout(layoutProps).run();
      cyRef.fit();
    }
  }, [graphData, cyRef]);

  useEffect(() => {
    if (cyRef) {
      cyRef.on("select", "node", (_evt) => {
        let nodeId = _evt.target.id().toString();
        if (nodeId.endsWith("_missing")) {
          updateSearchDistance(1);
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

  const layoutProps = {
    name: "euler",
    randomize: true,
    // Prevent the user grabbing nodes during the layout
    ungrabifyWhileSimulating: true,
    animate: "end",
    animationDuration: 500,
    springLength: 120,
    gravity: -10,
    theta: 0.2,
  };

  return (
    <Row className={"gy-3"}>
      <Col className={"col-xxl-9 col-lg-8 col-xs-12"}>
        <CytoscapeComponent
          className={"rounded graph-view"}
          elements={convertToCytoScapeElements(
            graphData,
            settings,
            selectedNode
          )}
          style={{ width: "100%", height: "35rem" }}
          stylesheet={CytoscapeStyles}
          layout={layoutProps}
          cy={(cy) => {
            updateCyRef(cy);
          }}
        />
        <JSONDataAccordion data={graphData} />
      </Col>
      <Col className={"col-xxl-3"}>
        <SelectedNodeDetail
          nodeDetail={getNodeDetails(graphData, selectedNode)}
        />
        <GraphViewSettings settings={settings} onUpdate={updateSetting} />
      </Col>
    </Row>
  );
}

export default GraphView;
