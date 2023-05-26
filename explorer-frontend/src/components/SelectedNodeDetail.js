import React from "react";
import {
  Accordion,
  AccordionBody,
  AccordionHeader,
  AccordionItem,
  Card,
  CardBody,
  CardHeader,
  CardLink,
  CardSubtitle,
  CardText,
  CardTitle,
  Col,
  Form,
  FormGroup,
  Input,
  Label,
  ListGroup,
  ListGroupItem,
  Row,
  UncontrolledAccordion,
} from "reactstrap";
import { ImExit, ImMap, ImLink } from "react-icons/im";
import { TbChartDots3, TbListDetails, TbNetwork } from "react-icons/tb";
import { FaNetworkWired } from "react-icons/fa";

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

function SelectedNodeDetail(props) {
  const { nodeDetail, updateSelectedRouter } = props;

  const nn = nodeDetail?.nn ?? null;
  const nn_int = nodeDetail?.nn_int ?? null;
  const exit_path = nodeDetail?.exit_path ?? [];
  const routerId = nodeDetail?.id ?? null;

  const routers = nodeDetail?.networks?.router ?? [];
  const external = nodeDetail?.networks?.external ?? [];
  const stubnets = nodeDetail?.networks?.stubnet ?? [];

  const is_exit = nodeDetail?.exit ?? null;

  const default_route = external.filter((network) => network.id === "0.0.0.0/0")[0];
  const direct_exit_cost = default_route?.metric ?? null;

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
          <UncontrolledAccordion defaultOpen={"-1"} flush>
            <AccordionItem>
              <AccordionHeader targetId="-1">
                <TbListDetails />
                &nbsp;&nbsp;Node Details
              </AccordionHeader>
              <AccordionBody accordionId="-1">
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
                  <TbChartDots3 /> Exit Path:{" "}
                </b>
                <ul className={"m-0"}>
                  {exit_path.map((router_id) => (
                    <li key={router_id}>
                      <a
                        href={"/explorer?router=" + router_id}
                        onClick={(e) => {
                          e.preventDefault();
                          updateSelectedRouter(router_id);
                        }}
                      >
                        {router_id}
                      </a>
                    </li>
                  ))}
                </ul>
              </AccordionBody>
            </AccordionItem>
            <AccordionItem>
              <AccordionHeader targetId="0">
                <ImLink />
                &nbsp;&nbsp;Adjacent Routers ({routers.length ?? 0})
              </AccordionHeader>
              <AccordionBody accordionId="0">
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
          </UncontrolledAccordion>
        </Card>
      </Col>
    </Row>
  );
}

export default SelectedNodeDetail;
