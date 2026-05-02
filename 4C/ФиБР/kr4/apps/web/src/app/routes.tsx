// oxlint-disable sort-imports
import MongoDBPage from "@/pages/mongo/page";
import PostgresDBPage from "@/pages/postgres/page";
import RootLayout from "@/pages/layout";
import { Route } from "react-router";
import type { ReactNode } from "react";

export default function WebsiteRoutes(): ReactNode {
  return (
    <Route path="/" element={<RootLayout />}>
      <Route path="/db">
        <Route path="/db/mongo" element={<MongoDBPage />} />
        <Route path="/db/postgres" element={<PostgresDBPage />} />
      </Route>
    </Route>
  );
}
