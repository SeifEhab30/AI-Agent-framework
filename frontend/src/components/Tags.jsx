import { useEffect, useState } from "react";
import { tagsApi } from "../api";

export default function Tags() {
  const [tags, setTags] = useState([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const load = () => tagsApi.list().then(setTags).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await tagsApi.create(name);
      setName("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Tags</h2>
      <form onSubmit={handleCreate} className="new-card">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="card-list">
        {tags.map((t) => (
          <li key={t.id} className="entry-card">
            <div className="entry-row">
              <span className="entry-title">{t.name}</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
