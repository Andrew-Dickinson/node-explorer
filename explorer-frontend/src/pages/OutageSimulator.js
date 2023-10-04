import { Alert, Button, Col, Row, Spinner } from "reactstrap";
import React, { useEffect, useState } from "react";
import useUrlState from "@ahooksjs/use-url-state";
import { NodeAndEdgeSelector } from "../components/NodeAndEdgeSelector";
import axios from "axios";
import { SIMULATE_OUTAGE_URL } from "../constants";
import JSONDataAccordion from "../components/JSONDataAccordion";
import GraphView from "../components/GraphView";
import { NodeGraph } from "../components/NodeGraph";
import { convertOutageToCytoScapeElements } from "../lib/GraphHelpers";
import { BsFillCircleFill, BsX, BsXCircle, BsXLg } from "react-icons/bs";
import { black, darkGrey, darkRed, red, yellow } from "../styles/CytoscapeStyles";
import { humanLabelFromIP } from "../lib/utils";

const OUTAGE_DATA_EMPTY = {
  nodes: [],
  edges: [],
  outage_lists: {
    offline: [],
    removed: [],
    rerouted: [],
  },
};

function NodeUL(props) {
  const { nodeList } = props;

  const [expanded, setExpanded] = useState(false);

  let nodeListToDisplay = nodeList;
  let hiddenNodes = false;
  if (nodeList.length > 10 && !expanded) {
    hiddenNodes = true;
    nodeListToDisplay = nodeListToDisplay.slice(0, 10);
  }

  return nodeListToDisplay.length > 0 ? (
    <ul className={"list-group"}>
      {nodeListToDisplay.map((node) => (
        <li className={"list-group-item"} key={node}>
          {humanLabelFromIP(node)}
        </li>
      ))}
      {hiddenNodes ? (
        <li className={"list-group-item"} key={"showMore"}>
          <a
            role={"button"}
            href={""}
            onClick={(event) => {
              event.preventDefault();
              setExpanded(true);
            }}
          >
            Show {nodeList.length - nodeListToDisplay.length} more...
          </a>
        </li>
      ) : (
        <></>
      )}
      {expanded ? (
        <li className={"list-group-item"} key={"showLess"}>
          <a
            role={"button"}
            href={"#"}
            onClick={(event) => {
              event.preventDefault();
              setExpanded(false);
            }}
          >
            Show fewer...
          </a>
        </li>
      ) : (
        <></>
      )}
    </ul>
  ) : (
    <span className={"fst-italic"}>None</span>
  );
}

export function OutageSimulator(props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [selectedNodes, setSelectedNodes] = useState([]);
  const [selectedEdges, setSelectedEdges] = useState([]);

  const [outageData, setOutageData] = useState(OUTAGE_DATA_EMPTY);

  function simulateOutage() {
    setError(null);
    setLoading(true);
    axios
      .get(SIMULATE_OUTAGE_URL, {
        params: {
          nodes: selectedNodes.join(","),
          edges: selectedEdges.map(({ from, to }) => `${from}->${to}`).join(","),
        },
      })
      .then((res) => {
        setOutageData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        setError(err?.response?.data ?? err?.message ?? "Err");
      });
  }

  useEffect(() => {
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      simulateOutage();
    } else {
      setOutageData(OUTAGE_DATA_EMPTY);
    }
  }, [selectedEdges, selectedNodes]);

  return (
    <>
      <h2 className={"mb-3"}>Outage Simulator (beta)</h2>
      <Row>
        <NodeAndEdgeSelector
          selectedNodes={selectedNodes}
          onNodeSelectionUpdate={setSelectedNodes}
          selectedEdges={selectedEdges}
          onEdgeSelectionUpdate={setSelectedEdges}
        />
      </Row>
      {error ? (
        <Row>
          <Col className={"col-12"}>
            <Alert color={"danger"}>
              <h4>Encountered an Error while Simulating Outage</h4>
              <p>{error}</p>
            </Alert>
          </Col>
        </Row>
      ) : null}
      <Row className={"mb-3"}>
        <h3>
          If the selected routers and links went offline, the following routers would be affected
        </h3>
        <Col className={"col-12 col-md-4"}>
          <h5>Offline (selected&nbsp;for&nbsp;simulation)</h5>
          {loading ? (
            <Spinner role="status" style={{ width: "1.5rem", height: "1.5rem" }} />
          ) : (
            <NodeUL nodeList={outageData.outage_lists.removed} />
          )}
        </Col>
        <Col className={"col-12 col-md-4"}>
          <h5>Offline (due&nbsp;to&nbsp;the&nbsp;outage)</h5>
          {loading ? (
            <Spinner role="status" style={{ width: "1.5rem", height: "1.5rem" }} />
          ) : (
            <NodeUL nodeList={outageData.outage_lists.offline} />
          )}
        </Col>
        <Col className={"col-12 col-md-4"}>
          <h5>Rerouted (due&nbsp;to&nbsp;the&nbsp;outage)</h5>
          {loading ? (
            <Spinner role="status" style={{ width: "1.5rem", height: "1.5rem" }} />
          ) : (
            <NodeUL nodeList={outageData.outage_lists.rerouted} />
          )}
        </Col>
      </Row>
      <Row>
        <Col>
          <h3>
            {loading ? (
              <>
                <Spinner role="status" style={{ width: "1.5rem", height: "1.5rem" }} />
                &nbsp;
              </>
            ) : (
              ""
            )}
            Impact Graph
          </h3>
          <NodeGraph
            graphElements={convertOutageToCytoScapeElements(outageData)}
            layoutName={"euler"}
            onNodeSelected={(_) => {}}
            refitDependencies={[outageData]}
          />
          {/*<h3>Key</h3>*/}
          <ul className={"list-group list-group-horizontal-md"}>
            <li className={"list-group-item"}>
              <BsFillCircleFill style={{ color: black }} /> Exit (Supernode)
            </li>
            <li className={"list-group-item"}>
              <BsFillCircleFill style={{ color: darkRed }} /> Offline Router
            </li>
            <li className={"list-group-item"}>
              <span
                style={{
                  color: darkRed,
                  fontWeight: "bold",
                  fontSize: "20px",
                  "vertical-align": "-2px",
                }}
              >
                X
              </span>
              &nbsp;Offline Link
            </li>
            <li className={"list-group-item"}>
              <BsFillCircleFill style={{ color: yellow }} /> Will be Re-routed
            </li>
            {/*<li className={"list-group-item"}>*/}
            {/*  <BsFillCircleFill style={{ color: red }} /> Offline (due to the outage)*/}
            {/*</li>*/}
            <li className={"list-group-item"}>
              <BsFillCircleFill style={{ color: darkGrey }} /> Not Re-routed (may experience traffic
              shifts)
            </li>
          </ul>
        </Col>
      </Row>
      <Row>
        <Col>
          <Alert color={"info"} className={"mt-3"}>
            <h4>Beta: Outage simulation may be imperfect</h4>
            <p>
              The simulation that this tool does to compute re-routes and impact is tricky to get
              right and we&apos;re not sure if it&apos;s 100% correct yet. Especialy in the case of
              asymmetric routing the display above may not be accurate/useful. Report any
              inconsistencies you notice to <b>@Andrew&nbsp;Dickinson</b> on slack so we can fix
              them!
            </p>
          </Alert>
        </Col>
      </Row>
      <JSONDataAccordion data={outageData ?? {}} />
    </>
  );
}
