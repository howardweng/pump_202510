import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import { BrowserRouter } from "react-router-dom";
import "./global.css";
import "./index.css"; // Tailwind CSS styles

const container = document.getElementById("root");
const root = createRoot(container);

root.render(

  <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
    <App />
  </BrowserRouter>

);


reportWebVitals();
