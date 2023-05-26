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
import { GrDocumentText } from "react-icons/gr";

function JSONDataAccordion(data) {
  return (
    <Row className={"mb-3"}>
      <Col>
        <UncontrolledAccordion defaultOpen={"0"}>
          <AccordionItem>
            <AccordionHeader targetId="1">
              <GrDocumentText />
              &nbsp;&nbsp;Raw JSON Data
            </AccordionHeader>
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
