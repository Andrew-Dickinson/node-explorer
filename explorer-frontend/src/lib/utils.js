import { useEffect, useRef } from "react";
import _ from "lodash";

export function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export function arraysEqual(a, b) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (a.length !== b.length) return false;

  // If you don't care about the order of the elements inside
  // the array, you should sort both arrays here.
  // Please note that calling sort on an array will modify that array.
  // you might want to clone your array first.

  for (var i = 0; i < a.length; ++i) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}
//
// export function containsObject(obj, arr) {
//   var i;
//   for (i = 0; i < arr.length; i++) {
//     if (arr[i] === obj) {
//       return true;
//     }
//   }
//
//   return false;
// }

export function humanLabelFromIP(ipAddr) {
  /**
   * If you change me, please also update the corresponding
   * compute_nn_string_from_ip function in utils.py in the back-end
   */
  if (!_.startsWith(ipAddr, "10.69.")) {
    return ipAddr;
  }

  const components = _.split(ipAddr, ".");
  const thirdOctet = _.toInteger(components[2]);
  let fourthOctet = _.toInteger(components[3]);

  const routerIndex = _.toInteger(fourthOctet / 100);

  while (fourthOctet >= 100) {
    fourthOctet -= 100;
  }

  if (thirdOctet > 100) {
    return ipAddr;
  }

  let suffix = "";
  if (routerIndex > 0) {
    suffix = ` (.${routerIndex}xx)`;
  }
  return (100 * thirdOctet + fourthOctet).toString() + suffix;
}

export function ipFromMaybeNN(maybeNN) {
  if (maybeNN.indexOf(".") !== -1) {
    // If the input string contains a dot we assume it's an IP and
    // don't mess with it
    return maybeNN;
  }

  const nnInt = _.toInteger(maybeNN);
  return `10.69.${_.toInteger(nnInt / 100)}.${nnInt % 100}`;
}
