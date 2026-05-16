import { Link } from "react-router";

export default function Header() {
  return <header>
    <ul>
      <li>
        <Link to="/">Main</Link>
      </li>
      <li>
        <Link to="/about">About</Link>
      </li>
    </ul>
  </header>
}