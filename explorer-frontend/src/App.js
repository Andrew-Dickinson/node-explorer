import "./styles/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import React, { useState } from "react";
import Layout from "./components/Layout";
import NoPage from "./pages/NoPage";
import Explorer from "./pages/Explorer";

import "bootstrap/dist/css/bootstrap.min.css";
import "react-bootstrap-range-slider/dist/react-bootstrap-range-slider.css";
import { OutageSimulator } from "./pages/OutageSimulator";

function App() {
  const [dataLastUpdated, setDataLastUpdated] = useState(null);
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout dataLastUpdated={dataLastUpdated} />}>
          <Route index element={<Navigate to="/explorer" />} />
          <Route
            path="/explorer"
            element={
              <Explorer dataLastUpdated={dataLastUpdated} setDataLastUpdated={setDataLastUpdated} />
            }
          />
          <Route
            path="/outage-analyzer"
            element={
              <OutageSimulator
                dataLastUpdated={dataLastUpdated}
                setDataLastUpdated={setDataLastUpdated}
              />
            }
          />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
