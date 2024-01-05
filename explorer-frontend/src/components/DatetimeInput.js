import moment from "moment";
import { FormGroup } from "reactstrap";
import React from "react";

export function DatetimeInput(props) {
  return (
    <FormGroup>
      Select to jump to a different timestamp or{" "}
      <a
        href={"#"}
        onClick={(e) => {
          e.preventDefault();
          props.onTimeSelected(undefined);
        }}
      >
        click here
      </a>{" "}
      to use live data: <br />
      <input
        aria-label="Date and time"
        type="datetime-local"
        min={moment().subtract(7, "days").format("YYYY-MM-DD[T]HH:mm")}
        max={moment().format("YYYY-MM-DD[T]HH:mm")}
        className={"mt-1 form-control"}
        value={moment.unix(props.currentTime).format("YYYY-MM-DD[T]HH:mm")}
        onChange={(e) => {
          props.onTimeSelected(moment(e.target.value).unix());
        }}
      />
    </FormGroup>
  );
}
