import React from "react";
import { Outlet } from "react-router-dom";
import { Container } from "reactstrap";
import OurNavBar from "./OurNavBar";
import useUrlState from "@ahooksjs/use-url-state";

function Layout(props) {
  const [urlState, setUrlState] = useUrlState({});

  return (
    <>
      <OurNavBar
        urlState={urlState}
        setUrlState={setUrlState}
        dataLastUpdated={props.dataLastUpdated}
      />
      <Container className={"pt-3 gy-3"}>
        <Outlet />
      </Container>
    </>
  );
}

export default Layout;
