import React from "react";
import {
  Card,
  CardBody,
  CardHeader,
  CardText,
  CardTitle,
  Col,
  Form,
  FormGroup,
  Input,
  Label,
  Row,
} from "reactstrap";
import RangeSlider from "react-bootstrap-range-slider";

function GraphViewSettings(props) {
  const { settings, onUpdate } = props;
  return (
    <Row>
      <Col>
        <Card className={"mb-3"}>
          <CardHeader>
            <h5 className={"mt-2"}>Display Settings</h5>
          </CardHeader>
          <CardBody>
            <FormGroup check>
              <Input
                id="lowestCostOnly"
                type="checkbox"
                checked={settings.lowestCostOnly}
                onChange={(e) => onUpdate("lowestCostOnly", e.target.checked)}
              />
              <Label check>
                Show only lowest cost links <br /> (for each pair of nodes)
              </Label>
            </FormGroup>
            <FormGroup check>
              <Input
                id="bothDirections"
                type="checkbox"
                checked={settings.bothDirections}
                onChange={(e) => onUpdate("bothDirections", e.target.checked)}
              />
              <Label check>Show both directions</Label>
            </FormGroup>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            <h5 className={"mt-2"}>Search Distance</h5>
          </CardHeader>
          <CardBody>
            <CardText>
              <FormGroup>
                <Label>
                  How many links away should we search from the selected node?
                </Label>
                <RangeSlider
                  id={"searchDistanceSlider"}
                  variant={settings.searchDistance > 1 ? "danger" : "primary"}
                  value={settings.searchDistance}
                  min={0}
                  max={2}
                  tooltipLabel={(val) =>
                    val > 1 ? val + " - might be slow" : val
                  }
                  onChange={(e) =>
                    onUpdate("searchDistance", parseInt(e.target.value))
                  }
                />
              </FormGroup>
            </CardText>
          </CardBody>
        </Card>
      </Col>
    </Row>
  );
}

export default GraphViewSettings;
