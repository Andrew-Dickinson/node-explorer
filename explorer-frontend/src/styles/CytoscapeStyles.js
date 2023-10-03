export const black = "#000";
export const red = "#c02b12";
export const darkRed = "#9d0000";
export const yellow = "#f1c102";
export const blue = "#036ad9";
export const lightBlue = "#7BB8FF";
export const lightGrey = "#ccc";
export const darkGrey = "#9f9f9f";

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
    selector: ".boldRedText",
    style: {
      color: darkRed,
      "font-weight": "bold",
      "font-size": "20px",
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
    selector: ".offline",
    style: {
      "background-color": darkRed,
    },
  },
  {
    selector: ".removed",
    style: {
      "background-color": darkRed,
    },
  },
  {
    selector: ".rerouted",
    style: {
      "background-color": yellow,
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
    selector: ".egress",
    style: {
      "line-color": lightBlue,
      "target-arrow-color": lightBlue,
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
