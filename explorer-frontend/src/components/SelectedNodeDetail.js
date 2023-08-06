import React, { useState } from "react";
import {
  Accordion,
  AccordionBody,
  AccordionHeader,
  AccordionItem,
  Badge,
  Card,
  CardHeader,
  CardLink,
  CardSubtitle,
  CardTitle,
  Col,
  ListGroup,
  ListGroupItem,
  Row,
  UncontrolledAccordion,
} from "reactstrap";
import { ImExit, ImMap, ImLink } from "react-icons/im";
import { TbChartDots3, TbListDetails, TbNetwork } from "react-icons/tb";
import { FaNetworkWired } from "react-icons/fa";
import { arraysEqual } from "../lib/utils";

function ip2int(ip) {
  return (
    ip.split(".").reduce(function (ipInt, octet) {
      return (ipInt << 8) + parseInt(octet, 10);
    }, 0) >>> 0
  );
}

function generateNetList(networks) {
  if (!networks.length) return "None";
  return (
    <ListGroup>
      {networks.map((networkDetail, i) => (
        <ListGroupItem key={i}>
          <b>{networkDetail.id}</b> (Cost{" "}
          {networkDetail.metric2 ? networkDetail.metric2 : networkDetail.metric})
        </ListGroupItem>
      ))}
    </ListGroup>
  );
}

function generatePathList(path, exit_network_cost, onclick) {
  return (
    <ListGroup className={"mt-1"}>
      {path.map(([router_id, cost], i) => (
        <ListGroupItem key={router_id} href={"/explorer?router=" + router_id}>
          <CardLink
            href={"/explorer?router=" + router_id}
            onClick={(e) => {
              e.preventDefault();
              onclick(router_id);
            }}
          >
            <b>{router_id}</b>
          </CardLink>{" "}
          {cost !== null ? <>Cost&nbsp;{cost}</> : <>Cost&nbsp;0 (self)</>}
          {i === path.length - 1 && exit_network_cost !== null ? (
            <> +&nbsp;{exit_network_cost}&nbsp;(to exit)</>
          ) : (
            ""
          )}
        </ListGroupItem>
      ))}
    </ListGroup>
  );
}

function SelectedNodeDetail(props) {
  const { nodeDetail, updateSelectedRouter } = props;

  const nn = nodeDetail?.nn ?? null;
  const nn_int = nodeDetail?.nn_int ?? null;

  const exit_path = nodeDetail?.exit_paths?.outbound ?? [];
  const egress_return_path = nodeDetail?.exit_paths?.return ?? [];
  const show_egress_return = !arraysEqual(
    egress_return_path
      .map(([node_id, cost]) => node_id)
      .slice()
      .reverse(),
    exit_path.map(([node_id, cost]) => node_id)
  );
  const exit_network_cost = nodeDetail?.exit_network_cost ?? 0;

  const exit_cost =
    exit_path
      .map(([node_id, cost]) => cost)
      .filter((val) => val !== null)
      .reduce((total, cur) => total + cur, 0) + exit_network_cost;

  const egres_return_cost = egress_return_path
    .map(([node_id, cost]) => cost)
    .filter((val) => val !== null)
    .reduce((total, cur) => total + cur, 0);

  const is_exit = exit_path.length === 1;
  const routerId = nodeDetail?.id ?? null;

  const routers = nodeDetail?.networks?.router ?? [];
  const external = nodeDetail?.networks?.external ?? [];
  const stubnets = nodeDetail?.networks?.stubnet ?? [];

  const default_route = external.filter((network) => network.id === "0.0.0.0/0")[0];
  const direct_exit_cost = default_route?.metric ?? default_route?.metric2 ?? null;

  routers.sort((a, b) => {
    if (ip2int(a.id) < ip2int(b.id)) {
      return -1;
    }
    if (ip2int(a.id) > ip2int(b.id)) {
      return 1;
    }
    if (a.metric < b.metric) {
      return -1;
    }
    if (a.metric > b.metric) {
      return 1;
    }
    return 0;
  });

  const [accordianState, updateAccordianState] = useState("-1");
  const accordianToggle = (id) => {
    if (accordianState === id) {
      updateAccordianState();
    } else {
      updateAccordianState(id);
    }
  };

  return (
    <Row>
      <Col>
        <Card className={"mb-3"}>
          <CardHeader>
            <CardTitle>
              <h5 className={"mt-2"}>Network Number {nn}</h5>
            </CardTitle>
            <CardSubtitle className={"text-muted"}>
              <h6>OSPF Router ID: {routerId}</h6>
            </CardSubtitle>
          </CardHeader>
          <Accordion open={accordianState} toggle={accordianToggle} flush>
            <AccordionItem>
              <AccordionHeader targetId="0">
                <TbListDetails />
                <span className={"ms-1"}>Node Details</span>
                {show_egress_return && accordianState !== "0" ? (
                  <Badge className={"ms-1"} color={"danger"} pill>
                    Path Mismatch
                  </Badge>
                ) : (
                  ""
                )}
              </AccordionHeader>
              <AccordionBody accordionId="0">
                <b>
                  <ImMap /> Map Link:{" "}
                </b>
                {nn_int ? (
                  <a
                    href={"https://www.nycmesh.net/map/nodes/" + nn_int}
                    target="_blank"
                    rel="noreferrer"
                  >
                    NN{nn_int}
                  </a>
                ) : (
                  "N/A"
                )}
                <br />
                <b>
                  <ImExit /> Is Exit:{" "}
                </b>
                {is_exit ? `Yes (cost ${direct_exit_cost})` : "No"}
                <br />
                <b>
                  <TbChartDots3 /> Exit Path
                  {show_egress_return ? (
                    <>
                      <Badge className={"ms-1"} color={"danger"} pill>
                        Path Mismatch
                      </Badge>
                    </>
                  ) : (
                    ` (Total Cost ${exit_cost})`
                  )}
                </b>
                <Row>
                  <Col>
                    {show_egress_return ? (
                      <h6 className={"text-center w-auto mb-0 fw-bold mt-1"}>
                        Outbound (Cost&nbsp;{exit_cost})
                      </h6>
                    ) : (
                      ""
                    )}
                    {generatePathList(exit_path, exit_network_cost, updateSelectedRouter)}
                  </Col>
                  {show_egress_return ? (
                    <Col>
                      <h6 className={"text-center w-auto mb-0 fw-bold mt-1"}>
                        Return <br className={"d-none d-xl-inline"} />
                        (Cost&nbsp;{egres_return_cost})
                      </h6>
                      {generatePathList(egress_return_path, null, updateSelectedRouter)}
                    </Col>
                  ) : (
                    ""
                  )}
                </Row>
              </AccordionBody>
            </AccordionItem>
            <AccordionItem>
              <AccordionHeader targetId="1">
                <ImLink />
                &nbsp;&nbsp;Adjacent Routers ({routers.length ?? 0})
              </AccordionHeader>
              <AccordionBody accordionId="1">
                <ListGroup>
                  {routers.map((router, i) => (
                    <ListGroupItem key={i}>
                      <b>
                        <CardLink
                          href={"/explorer?router=" + router.id}
                          onClick={(e) => {
                            e.preventDefault();
                            updateSelectedRouter(router.id);
                          }}
                        >
                          {router.id}
                        </CardLink>
                      </b>{" "}
                      (Cost {router.metric})
                    </ListGroupItem>
                  ))}
                </ListGroup>
              </AccordionBody>
            </AccordionItem>
            <AccordionItem>
              <AccordionHeader targetId="2">
                <FaNetworkWired />
                &nbsp;&nbsp;Advertised Stubnets ({stubnets.length ?? 0})
              </AccordionHeader>
              <AccordionBody accordionId="2">{generateNetList(stubnets)}</AccordionBody>
            </AccordionItem>
            <AccordionItem>
              <AccordionHeader targetId="3">
                <TbNetwork />
                &nbsp;&nbsp;Advertised External Networks ({external.length ?? 0})
              </AccordionHeader>
              <AccordionBody accordionId="3">{generateNetList(external)}</AccordionBody>
            </AccordionItem>
          </Accordion>
        </Card>
      </Col>
    </Row>
  );
}

export default SelectedNodeDetail;
