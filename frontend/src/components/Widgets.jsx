import { useEffect, useState } from "react";
import { widgetsApi } from "../api";

export default function Widgets() {
  const [widgets, setWidgets] = useState([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  const load = () => widgetsApi.list().then(setWidgets).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await widgetsApi.create(title);
      setTitle("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleToggle = async (id) => {
    setError("");
    try {
      await widgetsApi.toggle(id);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Widgets</h2>
      <form onSubmit={handleCreate} className="row">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New widget title"
        />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul>
        {widgets.map((w) => (
          <li key={w.id}>
            <label>
              <input type="checkbox" checked={w.done} onChange={() => handleToggle(w.id)} />
              <span className={w.done ? "done" : ""}>{w.title}</span>
            </label>
          </li>
        ))}
      </ul>
    </section>
  );
}
