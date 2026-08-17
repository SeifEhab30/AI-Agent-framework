import { useEffect, useState } from "react";
import { bookmarksApi } from "../api";

export default function Bookmarks() {
  const [bookmarks, setBookmarks] = useState([]);
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  const load = () => bookmarksApi.list().then(setBookmarks).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await bookmarksApi.create(url, title);
      setUrl("");
      setTitle("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleRename = async (id) => {
    const newTitle = window.prompt("New title?");
    if (!newTitle) return;
    setError("");
    try {
      await bookmarksApi.rename(id, newTitle);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <h2>Bookmarks</h2>
      <form onSubmit={handleCreate} className="new-card">
        <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="URL" />
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="card-list">
        {bookmarks.map((b) => (
          <li key={b.id} className="entry-card">
            <div className="entry-row">
              <a className="entry-link" href={b.url} target="_blank" rel="noreferrer">
                {b.title}
              </a>
              <button onClick={() => handleRename(b.id)}>Rename</button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
