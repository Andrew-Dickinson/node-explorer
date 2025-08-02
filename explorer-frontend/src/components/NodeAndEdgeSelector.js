import React, { useEffect, useState } from "react";
import { Button, Col, Input, Label, Row, Spinner, Tooltip } from "reactstrap";
import { BsFillXCircleFill } from "react-icons/bs";
import axios from "axios";
import { EDGES_DATA_URL } from "../constants";
import { FaPlusCircle } from "react-icons/fa";
import _ from "lodash";
import SimpleTooltip from "./SimpleTooltip";
import { humanLabelFromIP, ipFromMaybeNN } from "../lib/utils";

async function doesEdgeExist(router1_id, router2_id, timestamp) {
  try {
    const res = await axios.get(EDGES_DATA_URL + `${router1_id}/${router2_id}`, {
      params: timestamp ? { timestamp } : undefined,
    });
    return res.data && res.data.edges && res.data.edges.length !== 0;
  } catch (err) {
    return false;
  }
}

export function NodeSelector(props) {
  const { selectedNodes, onSelectionUpdate } = props;
  const [textBoxContent, setTextBoxContent] = useState("");

  function isInputTextBoxValid() {
    return (
      selectedNodes.indexOf(ipFromMaybeNN(textBoxContent)) === -1 && textBoxContent.length !== 0
    );
  }
  function handleSubmit() {
    setTextBoxContent("");
    onSelectionUpdate((prevSelected) => [...prevSelected, ipFromMaybeNN(textBoxContent)]);
  }

  return (
    <>
      <Row>
        <Col className={"col-12 col-md-6 col-lg-8 col-xxl-6"}>
          <h4>Offline Routers</h4>
          <ul className="list-group">
            {selectedNodes && selectedNodes.length ? (
              selectedNodes.map((node) => (
                <li
                  className="list-group-item d-flex justify-content-between align-items-center"
                  key={node}
                >
                  {humanLabelFromIP(node)}
                  <a
                    role="button"
                    onClick={() =>
                      onSelectionUpdate((prevSelected) => prevSelected.filter((n) => node !== n))
                    }
                  >
                    <BsFillXCircleFill color={"#c72857"} />
                  </a>
                </li>
              ))
            ) : (
              <span className={"fst-italic"}>None</span>
            )}
          </ul>
        </Col>
      </Row>
      <Row className={"gx-1 mt-3"}>
        <Label className={"mb-1 small fst-italic"} for={"new_node_num"}>
          Enter a Network Number or IP Address
        </Label>
        <Col className={"col-9 col-md-5 col-lg-8 col-xxl-6"}>
          <Input
            type="text"
            className="form-control"
            id="new_node_num"
            value={textBoxContent}
            onChange={(e) => setTextBoxContent(e.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && isInputTextBoxValid()) {
                handleSubmit();
              }
            }}
          />
        </Col>
        <Col className={"col-3 col-md-2"}>
          <Button
            color={"primary"}
            className={"w-100 ps-0 pe-0"}
            disabled={!isInputTextBoxValid()}
            onClick={handleSubmit}
          >
            Add&nbsp;&nbsp;
            <FaPlusCircle className={"shift-up"} />
          </Button>
        </Col>
      </Row>
    </>
  );
}

export function EdgeSelector(props) {
  const { selectedEdges, onSelectionUpdate } = props;

  const [textBox1Content, setTextBox1Content] = useState("");
  const [textBox2Content, setTextBox2Content] = useState("");
  // const [selectedEdges, setSelectedEdges] = useState([{ from: "1", to: "2" }]);
  const [loading, setLoading] = useState(false);
  const [pendingEdgeExists, setPendingEdgeExists] = useState(false);

  const edge_already_selected = () =>
    _.some(selectedEdges, {
      from: ipFromMaybeNN(textBox1Content),
      to: ipFromMaybeNN(textBox2Content),
    });

  function isInputTextBoxValid() {
    return (
      pendingEdgeExists &&
      !edge_already_selected() &&
      textBox2Content !== "" &&
      textBox1Content !== ""
    );
  }
  function handleSubmit() {
    onSelectionUpdate((prevSelected) => [
      ...prevSelected,
      { from: ipFromMaybeNN(textBox1Content), to: ipFromMaybeNN(textBox2Content) },
    ]);
    setTextBox1Content("");
    setTextBox2Content("");
  }

  return (
    <>
      <Row>
        <h4>Offline Links</h4>
        <Col className={"col-12 col-md-6 col-lg-8 col-xxl-6"}>
          {selectedEdges && selectedEdges.length ? (
            <ul className="list-group">
              {selectedEdges.map((edge) => (
                <li
                  className="list-group-item d-flex justify-content-between align-items-center"
                  key={`${edge.from}->${edge.to}`}
                >
                  {humanLabelFromIP(edge.from)} {"->"} {humanLabelFromIP(edge.to)}
                  <a
                    role="button"
                    onClick={() =>
                      onSelectionUpdate((prevSelected) =>
                        prevSelected.filter((e) => !_.eq(edge, e))
                      )
                    }
                  >
                    <BsFillXCircleFill color={"#c72857"} />
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <span className={"fst-italic"}>None</span>
          )}
        </Col>
      </Row>
      <Row className={"gx-1 mt-3"}>
        <Label className={"mb-1 small fst-italic"} for={"new_node_num1"}>
          Enter Two Network Numbers or IP Addresses
        </Label>
        <Col className={"col-6 col-md-5"}>
          <Input
            type="text"
            className="form-control"
            id="new_node_num1"
            value={textBox1Content}
            onChange={(e) => {
              setTextBox1Content(e.target.value);

              doesEdgeExist(
                ipFromMaybeNN(e.target.value),
                ipFromMaybeNN(textBox2Content),
                props.timestamp
              ).then((edgeExists) => {
                setLoading(false);
                setPendingEdgeExists(edgeExists);
              });
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !loading && isInputTextBoxValid()) {
                handleSubmit();
              }
            }}
          />
        </Col>
        <Col className={"col-6 col-md-5"}>
          <Input
            type="text"
            className="form-control"
            id="new_node_num2"
            value={textBox2Content}
            onChange={(e) => {
              setTextBox2Content(e.target.value);
              setLoading(true);
              doesEdgeExist(ipFromMaybeNN(textBox1Content), ipFromMaybeNN(e.target.value)).then(
                (edgeExists) => {
                  setLoading(false);
                  setPendingEdgeExists(edgeExists);
                }
              );
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !loading && isInputTextBoxValid()) {
                handleSubmit();
              }
            }}
          />
        </Col>
        <Col className={"col-12 mt-2 mt-md-0 col-md-2"}>
          <div
            className={"d-inline-block w-100"}
            id={"DisabledButton"}
            tabIndex="0"
            // role={loading || !pendingEdgeExists || edge_already_selected ? "button" : ""}
          >
            <Button
              color={"primary"}
              type="submit"
              className={"w-100 ps-0 pe-0"}
              disabled={loading || !isInputTextBoxValid()}
              onClick={handleSubmit}
            >
              Add&nbsp;&nbsp;
              {loading ? (
                <Spinner role="status" style={{ width: "0.8rem", height: "0.8rem" }} />
              ) : (
                <FaPlusCircle className={"shift-up"} />
              )}
            </Button>
          </div>
          <SimpleTooltip
            target={"DisabledButton"}
            disabled={
              loading || isInputTextBoxValid() || textBox1Content === "" || textBox2Content === ""
            }
          >
            {!pendingEdgeExists
              ? `There are no links connecting ${textBox1Content} to ${textBox2Content}`
              : edge_already_selected()
              ? "You've already selected that edge"
              : ""}
          </SimpleTooltip>
        </Col>
      </Row>
    </>
  );
}

export function NodeAndEdgeSelector(props) {
  return (
    <>
      <Col className={"col-12 col-lg-6 mb-3"}>
        <NodeSelector
          selectedNodes={props.selectedNodes}
          onSelectionUpdate={props.onNodeSelectionUpdate}
        />
      </Col>
      <Col className={"col-12 col-lg-6 mb-3"}>
        <EdgeSelector
          selectedEdges={props.selectedEdges}
          onSelectionUpdate={props.onEdgeSelectionUpdate}
          timestamp={props.timestamp}
        />
      </Col>
    </>
  );
}
