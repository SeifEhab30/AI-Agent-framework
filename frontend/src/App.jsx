import { useState } from "react";
import Todos from "./components/Todos";
import Notes from "./components/Notes";
import Bookmarks from "./components/Bookmarks";
import Widgets from "./components/Widgets";
import "./App.css";

const TABS = {
  todos: Todos,
  notes: Notes,
  bookmarks: Bookmarks,
  widgets: Widgets,
};

export default function App() {
  const [tab, setTab] = useState("todos");
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
