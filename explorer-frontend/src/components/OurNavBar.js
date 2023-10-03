import React, { useState } from "react";
import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from "reactstrap";
import { BsGithub } from "react-icons/bs";
import { COMMIT_HASH } from "../constants";

function OurNavBar() {
  const [isOpen, setIsOpen] = useState(false);

  const toggle = () => setIsOpen(!isOpen);

  return (
    <div>
      <Navbar color={"dark"} light={false} dark={true} expand={"sm"} container={"sm"}>
        <NavbarBrand href="/">
          <img
            alt="logo"
            src="/NYC_Mesh_logo.svg"
            style={{
              height: 35,
              width: 35,
            }}
            className={"mx-2"}
          />
          Node Explorer
        </NavbarBrand>
        <NavbarToggler onClick={toggle} />
        <Collapse isOpen={isOpen} navbar>
          <Nav className="me-auto" navbar>
            <NavItem>
              <NavLink href="/explorer">OSPF Explorer</NavLink>
            </NavItem>
            <NavItem>
              <NavLink href="/outage-analyzer">Outage Simulator (beta)</NavLink>
            </NavItem>
          </Nav>
          <Nav className={"ms-auto"} navbar>
            <NavItem className={"ms-auto"}>
              <NavLink href="https://github.com/Andrew-Dickinson/node-explorer">
                <BsGithub size={25}>GitHub Link</BsGithub>
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink
                href={"https://github.com/Andrew-Dickinson/node-explorer/commit/" + COMMIT_HASH}
                className={"fst-italic"}
              >
                {COMMIT_HASH.substring(0, 7)}
              </NavLink>
            </NavItem>
          </Nav>
        </Collapse>
      </Navbar>
    </div>
  );
}

export default OurNavBar;
