import { Card, CardBody, CardText } from "reactstrap";
import moment from "moment/moment";
import { BsClockFill } from "react-icons/bs";
import React from "react";

export function LastUpdatedCard(props) {
  return (
    <Card>
      <CardBody>
        <CardText>
          Last Updated{" "}
          <i>
            {props.updatedTime ? moment.unix(props.updatedTime).fromNow() : "Never"}
            {"  "}
          </i>
          <BsClockFill className={"shift-up"}>Clock</BsClockFill>
        </CardText>
      </CardBody>
    </Card>
  );
}
