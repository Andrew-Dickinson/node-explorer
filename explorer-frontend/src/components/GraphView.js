import React, { useEffect, useState } from "react";
import { Alert, Col, Row } from "reactstrap";
import GraphViewSettings from "./GraphViewSettings";
import SelectedNodeDetail from "./SelectedNodeDetail";
import JSONDataAccordion from "./JSONDataAccordion";
import { convertOSPFToCytoScapeElements, getNodeDetails } from "../lib/GraphHelpers";
import { usePrevious } from "../lib/utils";
import { LastUpdatedCard } from "./LastUpdatedCard";
import { NodeGraph } from "./NodeGraph";

function Disclaimer() {
  return (
    <Row>
      <Col>
        <Alert color={"info"}>
          <h4>NB: OSPF data may be imperfect</h4>
          <p>
            This tool pulls from the output of <code>birdc show ospf state</code> and may not be
            100% accurate. It seems to be pretty good from experimentation but for critical decision
            making please double check the router configuration. Report any inconsistencies you
            notice to <b>@Andrew Dickinson</b> on slack so we can fix them!
          </p>
        </Alert>
      </Col>
    </Row>
  );
}

function GraphView(props) {
  const {
    graphData,
    searchDistance,
    updateSearchDistance,
    selectedNode,
    onNodeSelected,
    displayWarning,
  } = props;

  const [settings, setSettings] = useState({
    bothDirections: false,
    lowestCostOnly: true,
    searchDistance: searchDistance,
    includeEgress: true,
  });
  const previousSettings = usePrevious(settings);

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

  return (
    <Row className={"gy-3"}>
      <Col className={"col-xxl-9 col-lg-8 col-xs-12"}>
        <Col className={"mb-3 d-block d-lg-none"}>
          <LastUpdatedCard updatedTime={graphData.updated} />
        </Col>
        <NodeGraph
          graphElements={convertOSPFToCytoScapeElements(graphData, settings, selectedNode)}
          selectedNode={selectedNode}
          onNodeSelected={(nodeId) => {
            updateSearchDistance(1);
            onNodeSelected(nodeId);
          }}
          refitDependencies={[graphData, settings?.includeEgress]}
        />
        <div className={"d-none d-lg-block"}>
          <JSONDataAccordion data={graphData} />
          {displayWarning ? <Disclaimer /> : null}
        </div>
      </Col>
      <Col className={"col-xxl-3 col-lg-4 mt-lg-3 col-12 mt-0"}>
        <SelectedNodeDetail
          nodeDetail={getNodeDetails(graphData, selectedNode)}
          updateSelectedRouter={onNodeSelected}
        />
        <GraphViewSettings settings={settings} onUpdate={updateSetting} />
        <div className={"mt-3 d-block d-lg-none"}>
          <JSONDataAccordion data={graphData} />
          {displayWarning ? <Disclaimer /> : null}
        </div>
      </Col>
    </Row>
  );
}

export default GraphView;
