import React from "react";
import { Outlet } from "react-router-dom";
import { Container } from "reactstrap";
import OurNavBar from "./OurNavBar";

function Layout() {
  return (
    <>
      {/*<Container fluid className={"p-0"}>*/}
      <OurNavBar />
      <Container className={"pt-3 gy-3"}>
        <Outlet />
      </Container>
      {/*</Container>*/}
      {/*<Navbar>*/}
      {/*  <NavbarBrand href="/">*/}
      {/*    Home*/}
      {/*  </NavbarBrand>*/}
      {/*</Navbar>*/}
    </>
  );
}

export default Layout;
