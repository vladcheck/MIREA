import { BrowserRouter } from "react-router";
import { StrictMode } from "react";
import WebsiteRoutes from "./routes";
import { createRoot } from "react-dom/client";

const root = document.querySelector("#root");
if (root) {
  createRoot(root).render(
    <StrictMode>
      <BrowserRouter>
        <WebsiteRoutes />
      </BrowserRouter>
    </StrictMode>,
  );
}
