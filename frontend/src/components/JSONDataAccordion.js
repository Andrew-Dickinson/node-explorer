import {
  AccordionBody,
  AccordionHeader,
  AccordionItem,
  Col,
  Row,
  UncontrolledAccordion,
} from "reactstrap";
import { CopyBlock, dracula } from "react-code-blocks";
import React from "react";

function JSONDataAccordion(data) {
  return (
    <Row className={"mt-3"}>
      <Col>
        <UncontrolledAccordion>
          <AccordionItem>
            <AccordionHeader targetId="1">Raw JSON Data</AccordionHeader>
            <AccordionBody accordionId="1">
              <CopyBlock
                language="json"
                text={JSON.stringify(data, null, 2)}
                showLineNumbers={false}
                theme={dracula}
                wrapLines={false}
                codeBlock
              />
            </AccordionBody>
          </AccordionItem>
        </UncontrolledAccordion>
      </Col>
    </Row>
  );
}

export default JSONDataAccordion;
