import { useEffect, useState } from "react";
import { remindersApi } from "../api";

export default function Reminders() {
  const [reminders, setReminders] = useState([]);
  const [message, setMessage] = useState("");
  const [dueAt, setDueAt] = useState("");
  const [error, setError] = useState("");

  const load = () => remindersApi.list().then(setReminders).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await remindersApi.create(message, dueAt);
      setMessage("");
      setDueAt("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleMarkDone = async (id) => {
    setError("");
    try {
      await remindersApi.markDone(id);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    setError("");
    try {
      await remindersApi.delete(id);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Reminders</h2>
      <form onSubmit={handleCreate} className="new-card">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Message"
        />
        <input
          type="datetime-local"
          value={dueAt}
          onChange={(e) => setDueAt(e.target.value)}
          aria-label="Due date"
        />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="card-list">
        {reminders.map((r) => (
          <li key={r.id} className="entry-card">
            <div className="entry-row">
              <span className={`entry-title ${r.done ? "done" : ""}`}>{r.message}</span>
              {r.done ? (
                <span className="stamp">Done</span>
              ) : (
                <button onClick={() => handleMarkDone(r.id)}>Done</button>
              )}
              <button onClick={() => handleDelete(r.id)}>Delete</button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
