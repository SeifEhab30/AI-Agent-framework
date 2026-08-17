import { useEffect, useState } from "react";
import { widgetsApi } from "../api";

export default function Widgets() {
  const [widgets, setWidgets] = useState([]);
  const [label, setLabel] = useState("");
  const [value, setValue] = useState("0");
  const [drafts, setDrafts] = useState({});
  const [error, setError] = useState("");

  const load = () => widgetsApi.list().then(setWidgets).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await widgetsApi.create(label, Number(value) || 0);
      setLabel("");
      setValue("0");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleSetValue = async (id) => {
    setError("");
    try {
      await widgetsApi.setValue(id, Number(drafts[id]) || 0);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Widgets</h2>
      <form onSubmit={handleCreate} className="new-card">
        <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Label" />
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Value"
          inputMode="numeric"
          className="value-input"
        />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="card-list">
        {widgets.map((w) => (
          <li key={w.id} className="entry-card entry-widget">
            <span className="widget-label">{w.label}</span>
            <span className="widget-value">{w.value}</span>
            <input
              value={drafts[w.id] ?? String(w.value)}
              onChange={(e) => setDrafts({ ...drafts, [w.id]: e.target.value })}
              inputMode="numeric"
              className="value-input"
            />
            <button onClick={() => handleSetValue(w.id)}>Set</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
