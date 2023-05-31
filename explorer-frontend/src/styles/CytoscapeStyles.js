const black = "#000";
const red = "#c02b12";
const yellow = "#f1c102";
const blue = "#036ad9";
const lightBlue = "#7BB8FF";
const lightGrey = "#ccc";
const darkGrey = "#9f9f9f";

export default [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "text-outline-color": "#eeeeee",
      "text-outline-width": "2px",
    },
  },
  {
    selector: "edge",
    style: {
      width: 3,
      "line-color": lightGrey,
      "target-arrow-color": lightGrey,
      "curve-style": "bezier",
      "font-size": "12pt",
      label: "data(label)",
      "text-outline-color": "#eeeeee",
      "text-outline-width": "1px",
    },
  },
  {
    selector: ".primaryNode",
    style: {
      "font-weight": "bold",
    },
  },
  {
    selector: ".exit",
    style: {
      "background-color": black,
    },
  },
  {
    selector: ".impaired",
    style: {
      "background-color": yellow,
    },
  },
  {
    selector: ".outage",
    style: {
      "background-color": red,
    },
  },
  {
    selector: ".selected",
    style: {
      "background-color": blue,
    },
  },
  {
    selector: ".directionalEdge",
    style: {
      "target-arrow-shape": "triangle",
    },
  },
  {
    selector: ".invalidCosts",
    style: {
      color: red,
    },
  },
  {
    selector: ".mismatchedCostEdge",
    style: {
      "target-arrow-shape": "triangle",
    },
  },
  {
    selector: ".primaryEgress",
    style: {
      "line-color": darkGrey,
      "target-arrow-color": darkGrey,
    },
  },
  {
    selector: ".dashedEdge",
    style: {
      "line-style": "dashed",
    },
  },
  {
    selector: ".invisibleNode",
    style: {
      "text-valign": "center",
      "background-opacity": 0,
    },
  },
];
