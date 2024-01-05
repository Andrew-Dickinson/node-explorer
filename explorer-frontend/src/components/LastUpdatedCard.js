import { Card, CardBody, CardHeader, CardText, CardTitle } from "reactstrap";
import moment from "moment/moment";
import { BsClockFill } from "react-icons/bs";
import React from "react";
import { DatetimeInput } from "./DatetimeInput";

export function LastUpdatedCard(props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <h5 className={"mt-2"}>
            <BsClockFill className={"shift-up"}>Clock</BsClockFill> {"   "}Time Travel Mode
          </h5>
        </CardTitle>
      </CardHeader>
      <CardBody>
        <LastUpdatedContents
          updatedTime={props.updatedTime}
          urlState={props.urlState}
          setUrlState={props.setUrlState}
        />
      </CardBody>
    </Card>
  );
}

export function LastUpdatedContents(props) {
  const timeInUse = props.updatedTime ?? props.urlState.timestamp;
  return (
    <>
      {timeInUse ? (
        <CardText>
          {props.updatedTime ? "Using" : "Attempting to use "} data from{" "}
          {timeInUse ? moment.unix(timeInUse).calendar() + " " : "Never "}
          <i>{timeInUse ? "(" + moment.unix(timeInUse).fromNow() + ")" : ""}</i>
        </CardText>
      ) : (
        ""
      )}
      {props.urlState.timestamp ? (
        <DatetimeInput
          currentTime={props.urlState.timestamp}
          onTimeSelected={(timestamp) => {
            props.setUrlState((oldState) => {
              return { ...oldState, timestamp };
            });
          }}
        />
      ) : (
        <CardText>
          Attempting to use live data.{" "}
          <a
            href={""}
            onClick={(e) => {
              e.preventDefault();
              props.setUrlState((oldState) => {
                return { ...oldState, timestamp: moment().unix() };
              });
            }}
          >
            Click here
          </a>{" "}
          to use historical data instead
        </CardText>
      )}
    </>
  );
}
