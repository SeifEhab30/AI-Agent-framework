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
    <div className="app">
      <h1>Todoapp</h1>
      <nav className="tabs">
        {Object.keys(TABS).map((name) => (
          <button
            key={name}
            className={name === tab ? "active" : ""}
            onClick={() => setTab(name)}
          >
            {name}
          </button>
        ))}
      </nav>
      <Active />
    </div>
  );
}
