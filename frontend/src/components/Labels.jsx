import { useEffect, useState } from "react";
import { labelsApi } from "../api";

export default function Labels() {
  const [labels, setLabels] = useState([]);
  const [name, setName] = useState("");
  const [color, setColor] = useState("");
  const [error, setError] = useState("");

  const load = () => labelsApi.list().then(setLabels).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await labelsApi.create(name, color);
      setName("");
      setColor("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    setError("");
    try {
      await labelsApi.delete(id);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Labels</h2>
      <form onSubmit={handleCreate} className="new-card">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
        <input value={color} onChange={(e) => setColor(e.target.value)} placeholder="#RRGGBB" />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="card-list">
        {labels.map((l) => (
          <li key={l.id} className="entry-card">
            <div className="entry-row">
              <span className="entry-title">{l.name}</span>
              <span className="stamp" style={{ backgroundColor: l.color }}>
                {l.color}
              </span>
              <button onClick={() => handleDelete(l.id)}>Delete</button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
