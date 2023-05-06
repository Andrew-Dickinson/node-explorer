const API_BASE = process.env.REACT_APP_API_URL_OVERRIDE
  ? process.env.REACT_APP_API_URL_OVERRIDE
  : "/api";

export const COMMIT_HASH = process.env.REACT_APP_COMMIT_HASH
  ? process.env.REACT_APP_COMMIT_HASH
  : "???????";

export const NEIGHBORS_DATA_URL = API_BASE + "/neighbors/";
