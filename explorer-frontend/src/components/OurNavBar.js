import React, { useState } from "react";
import {
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink,
  Badge,
  PopoverBody,
  PopoverHeader,
  UncontrolledPopover,
} from "reactstrap";
import { BsClockFill, BsGithub } from "react-icons/bs";
import { COMMIT_HASH } from "../constants";
import moment from "moment";
import { LastUpdatedContents } from "./LastUpdatedCard";

function OurNavBar(props) {
  const { urlState, setUrlState } = props;
  const [isOpen, setIsOpen] = useState(false);
  const toggle = () => setIsOpen(!isOpen);

  const timestampBadge = (
    <Badge pill={true} color={"info"}>
      <BsClockFill />{" "}
      {urlState.timestamp ? moment.unix(urlState.timestamp).format("YYYY/MM/DD HH:mm") : "Live"}
    </Badge>
  );

  return (
    <div>
      <Navbar color={"dark"} light={false} dark={true} expand={"sm"} container={"sm"}>
        <NavbarBrand href={`/explorer?timestamp=${urlState.timestamp ?? ""}`}>
          {" "}
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
              <NavLink href={`/explorer?timestamp=${urlState.timestamp ?? ""}`}>
                OSPF Explorer
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink href={`/outage-analyzer?timestamp=${urlState.timestamp ?? ""}`}>
                Outage Simulator (beta)
              </NavLink>
            </NavItem>
          </Nav>
          <Nav className={"ms-auto"} navbar>
            <NavItem className={"ms-auto me-3 d-none d-sm-block"}>
              <NavLink href={"#"} id={"datetimePopover"}>
                {timestampBadge}
              </NavLink>
              <UncontrolledPopover placement="bottom" target={"datetimePopover"} trigger="legacy">
                <PopoverHeader>
                  <h5>Time Travel Mode</h5>
                </PopoverHeader>
                <PopoverBody>
                  <LastUpdatedContents
                    updatedTime={props.dataLastUpdated}
                    urlState={urlState}
                    setUrlState={setUrlState}
                  />
                </PopoverBody>
              </UncontrolledPopover>
            </NavItem>
            <NavItem>
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
