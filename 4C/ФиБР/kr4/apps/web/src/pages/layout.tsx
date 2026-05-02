import { Outlet } from "react-router";
import type { ReactNode } from "react";

export default function RootLayout(): ReactNode {
  return (
    <div>
      <header></header>
      <aside></aside>
      <main className="main">
        <Outlet />
      </main>
      <footer></footer>
    </div>
  );
}
