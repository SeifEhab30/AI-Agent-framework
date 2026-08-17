import { useState } from "react";
import Widgets from "./components/Widgets";
import Notes from "./components/Notes";
import Bookmarks from "./components/Bookmarks";
import "./App.css";

const TABS = {
  widgets: Widgets,
  notes: Notes,
  bookmarks: Bookmarks,
};

export default function App() {
  const [tab, setTab] = useState("widgets");
  const Active = TABS[tab];

  return (
    <div className="shell">
      <header className="plate">
        <span className="plate-label">Todoapp</span>
        <span className="plate-sub">Card Catalog</span>
      </header>
      <nav className="tabs">
        {Object.keys(TABS).map((name) => (
          <button
            key={name}
            className={name === tab ? "active" : ""}
            onClick={() => setTab(name)}
            aria-current={name === tab ? "true" : undefined}
          >
            {name}
          </button>
        ))}
      </nav>
      <main className="drawer">
        <Active />
      </main>
    </div>
  );
}
