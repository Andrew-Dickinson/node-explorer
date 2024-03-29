import React, { useEffect, useState } from "react";
import { Button, Col, Input, InputGroup, InputGroupText, Row, Spinner } from "reactstrap";
import { FaArrowAltCircleRight } from "react-icons/fa";

function NodeSearchBar(props) {
  const { routerId, updateRouterId, loading, updatedTime } = props;
  const [textBoxContent, setTextBoxContent] = useState(routerId);

  function isValidIpAddress() {
    const ipRegex = new RegExp("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$");
    return ipRegex.test(textBoxContent);
  }

  function isValidNN() {
    if (textBoxContent.indexOf(".") !== -1) return false;
    const nnInt = parseInt(textBoxContent);
    if (isNaN(nnInt)) return false;
    return nnInt > 0 && nnInt < 8192;
  }

  function convertNNToIP(nn) {
    const nnInt = parseInt(nn);
    return "10.69." + Math.floor(nnInt / 100) + "." + (nnInt % 100);
  }

  function handleSubmit() {
    if (isValidIpAddress()) {
      updateRouterId(textBoxContent);
    } else {
      updateRouterId(convertNNToIP(textBoxContent));
    }
  }

  useEffect(() => setTextBoxContent(routerId), [routerId]);

  return (
    <Row className={"mb-3"}>
      <Col className={"col-xxl-9 col-lg-8"}>
        <InputGroup>
          <InputGroupText>
            <span className={"d-sm-none d-inline"}>IP Addr or NN</span>
            <span className={"d-none d-sm-inline"}>IP Address or Network Number</span>
          </InputGroupText>
          <Input
            type="text"
            id="nn_input"
            value={textBoxContent}
            onChange={(e) => setTextBoxContent(e.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && (isValidIpAddress() || isValidNN())) {
                handleSubmit();
              }
            }}
          />
          <Button
            color="primary"
            disabled={loading || !(isValidIpAddress() || isValidNN())}
            onClick={() => handleSubmit()}
          >
            {loading ? "Loading" : "Go to"}&nbsp;&nbsp;
            {loading ? (
              <Spinner role="status" style={{ width: "0.8rem", height: "0.8rem" }} />
            ) : (
              <FaArrowAltCircleRight className={"shift-up"} />
            )}
          </Button>
        </InputGroup>
      </Col>
    </Row>
  );
}

export default NodeSearchBar;
