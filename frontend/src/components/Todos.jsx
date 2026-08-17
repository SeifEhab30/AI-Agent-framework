import { useEffect, useState } from "react";
import { todosApi } from "../api";

export default function Todos() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  const load = () => todosApi.list().then(setTodos).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await todosApi.create(title);
      setTitle("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleToggle = async (id) => {
    setError("");
    try {
      await todosApi.toggle(id);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Todos</h2>
      <form onSubmit={handleCreate} className="new-card">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New todo title"
        />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="card-list">
        {todos.map((t) => (
          <li key={t.id} className="entry-card">
            <div className="entry-row">
              <label>
                <input type="checkbox" checked={t.done} onChange={() => handleToggle(t.id)} />
                <span className={`entry-title ${t.done ? "done" : ""}`}>{t.title}</span>
              </label>
              {t.done && <span className="stamp">Done</span>}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
