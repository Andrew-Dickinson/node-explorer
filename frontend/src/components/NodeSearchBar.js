import React, { useEffect, useState } from "react";
import {
  Button,
  Card,
  CardBody,
  CardText,
  Col,
  Form,
  Input,
  InputGroup,
  InputGroupText,
  Row,
  Spinner,
} from "reactstrap";
import { BsClock, BsClockFill, BsGithub } from "react-icons/bs";
import moment from "moment";

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
            IP Address (OSPF ID) or Network Number
          </InputGroupText>
          <Input
            type="text"
            id="nn_input"
            value={textBoxContent}
            onChange={(e) => setTextBoxContent(e.target.value)}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                (isValidIpAddress() || isValidNN())
              ) {
                handleSubmit();
              }
            }}
          />
          <Button
            color="primary"
            disabled={loading || !(isValidIpAddress() || isValidNN())}
            onClick={() => handleSubmit()}
          >
            {loading ? "Loading " : "Go To Node "}
            {loading ? (
              <Spinner
                // type="grow"
                role="status"
                style={{ width: "0.8rem", height: "0.8rem" }}
              >
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            ) : (
              <></>
            )}
          </Button>
        </InputGroup>
      </Col>
      <Col>
        <Card>
          <CardBody>
            <CardText>
              OSPF DB Updated{" "}
              <i>
                {updatedTime ? moment.unix(updatedTime).fromNow() : "Never"}
                {"  "}
              </i>
              <BsClockFill>Clock</BsClockFill>
            </CardText>
          </CardBody>
        </Card>
      </Col>
    </Row>
  );
}

export default NodeSearchBar;
