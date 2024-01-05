import React, { useEffect, useState } from "react";
import { NEIGHBORS_DATA_URL } from "../constants";
import axios from "axios";

import * as PropTypes from "prop-types";
import JSONDataAccordion from "../components/JSONDataAccordion";
import GraphView from "../components/GraphView";
import {
  Alert,
  Button,
  Col,
  Form,
  FormGroup,
  Input,
  InputGroup,
  InputGroupText,
  Row,
  Spinner,
} from "reactstrap";
import NodeSearchBar from "../components/NodeSearchBar";
import useUrlState from "@ahooksjs/use-url-state";
import { usePrevious } from "../lib/utils";

JSONDataAccordion.propTypes = { data: PropTypes.shape({}) };

function Explorer(props) {
  const [urlState, setUrlState] = useUrlState({ router: "10.69.51.51" });
  const [searchDistance, setSearchDistance] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [graphData, updateanalysisData] = useState({ nodes: [], edges: [] });

  const prevSearchDistance = usePrevious(searchDistance);
  const prevUrlState = usePrevious(urlState);

  function loadGraphData() {
    setError(null);
    setLoading(true);
    const prevLastUpdate = graphData.updated;
    axios
      .get(NEIGHBORS_DATA_URL + urlState.router, {
        params: {
          searchDistance: searchDistance,
          includeEgress: true,
          timestamp: urlState.timestamp,
        },
      })
      .then((res) => {
        updateanalysisData(res.data);
        setLoading(false);
        props.setDataLastUpdated(res.data.updated);
      })
      .catch((err) => {
        setLoading(false);
        setError("Err");
        props.setDataLastUpdated(prevLastUpdate);
      });
  }

  useEffect(() => {
    loadGraphData();
  }, []);
  useEffect(() => {
    if (
      (prevUrlState?.router !== undefined && prevUrlState?.router !== urlState.router) ||
      (prevUrlState !== undefined && prevUrlState?.timestamp !== urlState.timestamp)
    ) {
      loadGraphData();
    }
  }, [urlState]);
  useEffect(() => {
    if (prevSearchDistance !== undefined && prevSearchDistance !== searchDistance) {
      loadGraphData();
    }
  }, [searchDistance]);

  return (
    <>
      <h2 className={"mb-3"}>OSPF Data Explorer</h2>
      {error ? (
        <Row>
          <Col className={"col-xxl-9 col-lg-8"}>
            <Alert color={"danger"}>
              <h4>Could not fetch node graph for {urlState.router}</h4>
              <p>Please enter a different ip address / node number or try again</p>
            </Alert>
          </Col>
        </Row>
      ) : null}

      <NodeSearchBar
        loading={loading}
        routerId={urlState.router}
        updateRouterId={(newRouterId) => {
          setUrlState((oldState) => {
            return { ...oldState, router: newRouterId };
          });
        }}
        updatedTime={props.dataLastUpdated}
      />

      <GraphView
        graphData={graphData}
        searchDistance={searchDistance}
        updateSearchDistance={setSearchDistance}
        selectedNode={urlState.router}
        displayWarning={false}
        urlState={urlState}
        setUrlState={setUrlState}
        onNodeSelected={(newRouterId) => {
          setUrlState((oldState) => {
            return { ...oldState, router: newRouterId };
          });
        }}
      />
    </>
  );
}

export default Explorer;
