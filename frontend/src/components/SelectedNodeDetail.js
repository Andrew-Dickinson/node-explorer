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
          {networkDetail.metric2 ? networkDetail.metric2 : networkDetail.metric}
          )
        </ListGroupItem>
      ))}
    </ListGroup>
  );
}

function SelectedNodeDetail(props) {
  const { nodeDetail, updateSelectedRouter } = props;

  const nn = nodeDetail?.nn ?? null;
  const routerId = nodeDetail?.id ?? null;

  const routers = nodeDetail?.networks?.router ?? [];
  const networks = nodeDetail?.networks?.network ?? [];
  const external = nodeDetail?.networks?.external ?? [];
  const stubnets = nodeDetail?.networks?.stubnet ?? [];

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
          <UncontrolledAccordion
            defaultOpen={"0"}
            flush
            className={"border-top"}
          >
            <AccordionItem>
              <AccordionHeader targetId="0">Adjacent Routers</AccordionHeader>
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
                Advertised Stubnets
              </AccordionHeader>
              <AccordionBody accordionId="2">
                {generateNetList(stubnets)}
              </AccordionBody>
            </AccordionItem>
            <AccordionItem>
              <AccordionHeader targetId="3">
                Advertised External Networks
              </AccordionHeader>
              <AccordionBody accordionId="3">
                {generateNetList(external)}
              </AccordionBody>
            </AccordionItem>
          </UncontrolledAccordion>
        </Card>
      </Col>
    </Row>
  );
}

export default SelectedNodeDetail;
