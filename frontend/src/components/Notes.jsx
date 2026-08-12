import { useEffect, useState } from "react";
import { notesApi } from "../api";

export default function Notes() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [drafts, setDrafts] = useState({});
  const [error, setError] = useState("");

  const load = () => notesApi.list().then(setNotes).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await notesApi.create(title, body);
      setTitle("");
      setBody("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleSave = async (id) => {
    setError("");
    try {
      await notesApi.updateBody(id, drafts[id] ?? "");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Notes</h2>
      <form onSubmit={handleCreate} className="col">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New note title"
        />
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Body"
        />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul>
        {notes.map((n) => (
          <li key={n.id} className="col">
            <strong>{n.title}</strong>
            <textarea
              value={drafts[n.id] ?? n.body}
              onChange={(e) => setDrafts({ ...drafts, [n.id]: e.target.value })}
            />
            <button onClick={() => handleSave(n.id)}>Save</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
