import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  Plus,
  Search,
  RefreshCw,
  Users,
  Check,
  Pencil,
  Trash2,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { api, send, type Item, type User } from "../api";
import { resources, roles } from "../resources";
import { ErrorBox, Empty, Modal, date } from "../ui";
import Editor from "./Editor";
import Details from "./Details";

export default function ResourcePage({
  name,
  user,
}: {
  name: string;
  user: User;
}) {
  const config = resources[name];
  const canWrite =
    user.user_type === "H" || (user.user_type === "T" && name === "results");
  const [data, setData] = useState<Item | null>(null);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editor, setEditor] = useState<Item | null | undefined>(undefined);
  const [detail, setDetail] = useState<Item | null>(null);
  const [deleting, setDeleting] = useState<Item | null>(null);
  const [busy, setBusy] = useState(false);
  const reload = () => setRevision((v) => v + 1);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    const timeout = setTimeout(() => {
      api(
        config.endpoint +
          "?page=" +
          page +
          "&search=" +
          encodeURIComponent(query),
      )
        .then((v) => {
          if (active) setData(v);
        })
        .catch((e) => {
          if (active) setError(e.message);
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }, 200);
    return () => {
      active = false;
      clearTimeout(timeout);
    };
  }, [config.endpoint, query, page, revision]);
  async function remove() {
    setBusy(true);
    try {
      await send(config.endpoint + deleting![config.id] + "/", "DELETE");
      setDeleting(null);
      if (data?.results.length === 1 && page > 1) setPage(page - 1);
      else reload();
    } catch (err) {
      setError((err as Error).message);
      setDeleting(null);
    } finally {
      setBusy(false);
    }
  }
  async function membership(item: Item) {
    setBusy(true);
    setError("");
    try {
      await send(
        config.endpoint + item[config.id] + "/membership/",
        item.is_member ? "DELETE" : "POST",
      );
      reload();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function display(item: Item, key: string) {
    const value = item[key];
    if (key === "user_type")
      return (
        <span className="badge">{roles[value as keyof typeof roles]}</span>
      );
    if (key === "is_active")
      return (
        <span className={"badge " + (value ? "green" : "")}>
          {value ? "Active" : "Inactive"}
        </span>
      );
    if (key === "grade")
      return (
        <span className={"grade " + (value === "F" ? "fail" : "")}>
          {value}
        </span>
      );
    if (key.endsWith("_date") || key === "enrolled_at") return date(value);
    return value ?? (name === "notices" ? "Department" : "—");
  }
  return (
    <>
      <div className="page-title">
        <div>
          <span className="eyebrow">ACADEMIC WORKSPACE</span>
          <h1>{config.title}</h1>
          <p>{config.description}</p>
        </div>
        {canWrite && (
          <button className="primary" onClick={() => setEditor(null)}>
            <Plus size={18} />
            New {config.singular}
          </button>
        )}
      </div>
      <ErrorBox message={error} />
      <section className="panel resource-panel">
        <div className="table-toolbar">
          <div>
            <h2>{config.title}</h2>
            <span className="count">{data?.count ?? "…"} records</span>
          </div>
          <div className="search-box">
            <Search size={17} />
            <input
              aria-label={"Search " + config.title.toLowerCase()}
              placeholder="Search records…"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(1);
              }}
            />
          </div>
          <button
            className="icon-button"
            onClick={reload}
            aria-label="Refresh records"
          >
            <RefreshCw size={17} />
          </button>
        </div>
        {loading ? (
          <div className="loading">Loading {config.title.toLowerCase()}…</div>
        ) : error ? (
          <Empty title="Could not load records">
            <button className="text-button" onClick={reload}>
              Try again
            </button>
          </Empty>
        ) : !data?.results.length ? (
          <Empty title={query ? "No matching records" : "Nothing here yet"}>
            {query
              ? "Try a different search."
              : canWrite
                ? "Add your first " + config.singular + " to get started."
                : "Your department will add records here."}
          </Empty>
        ) : name === "clubs" ? (
          <div className="club-grid">
            {data.results.map((c: Item) => (
              <article className="club-card" key={c.club_id}>
                <div className="club-card-top">
                  <div className="club-avatar">
                    <Users size={24} />
                  </div>
                  {c.is_member && (
                    <span className="badge green">
                      <Check size={12} />
                      Joined
                    </span>
                  )}
                </div>
                <h3>
                  <button className="record-link" onClick={() => setDetail(c)}>
                    {c.club_name}
                  </button>
                </h3>
                <p>{c.club_description}</p>
                <small>
                  {c.coordinator_name} · {c.member_count} members
                </small>
                <div className="club-actions">
                  <button
                    className={c.is_member ? "secondary" : "primary"}
                    disabled={busy}
                    onClick={() => membership(c)}
                  >
                    {c.is_member ? "Leave club" : "Join club"}
                    <ArrowUpRight size={15} />
                  </button>
                  {canWrite && (
                    <>
                      <button
                        className="icon-button"
                        aria-label={"Edit " + c.club_name}
                        onClick={() => setEditor(c)}
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        className="icon-button danger"
                        aria-label={"Delete " + c.club_name}
                        onClick={() => setDeleting(c)}
                      >
                        <Trash2 size={16} />
                      </button>
                    </>
                  )}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  {config.columns.map(([key, title]) => (
                    <th key={key}>{title}</th>
                  ))}
                  {(canWrite || name === "notices") && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {data.results.map((item: Item) => (
                  <tr key={item[config.id]}>
                    {config.columns.map(([key], i) => (
                      <td key={key} className={i === 0 ? "strong-cell" : ""}>
                        {key ===
                          (name === "subjects"
                            ? "subject_name"
                            : config.columns[0][0]) ||
                        (name === "subjects" && key === "subject_code") ? (
                          <button
                            className="record-link"
                            onClick={() => setDetail(item)}
                          >
                            {display(item, key)}
                          </button>
                        ) : (
                          display(item, key)
                        )}
                      </td>
                    ))}
                    {(canWrite || name === "notices") && (
                      <td>
                        <div className="row-actions">
                          {name === "notices" && (
                            <button
                              className="text-button"
                              onClick={() => setDetail(item)}
                            >
                              Read
                            </button>
                          )}
                          {canWrite && (
                            <>
                              <button
                                className="icon-button"
                                aria-label={
                                  "Edit " +
                                  config.singular +
                                  " " +
                                  item[config.id]
                                }
                                onClick={() => setEditor(item)}
                              >
                                <Pencil size={15} />
                              </button>
                              {name !== "users" && (
                                <button
                                  className="icon-button danger"
                                  aria-label={
                                    "Delete " +
                                    config.singular +
                                    " " +
                                    item[config.id]
                                  }
                                  onClick={() => setDeleting(item)}
                                >
                                  <Trash2 size={15} />
                                </button>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination">
          <span>
            {data?.count
              ? "Page " + page + " · " + data.count + " total records"
              : "0 records"}
          </span>
          <div>
            <button
              className="secondary compact"
              disabled={page === 1 || loading}
              onClick={() => setPage(page - 1)}
            >
              <ChevronLeft size={16} />
              Previous
            </button>
            <button
              className="secondary compact"
              disabled={!data?.next || loading}
              onClick={() => setPage(page + 1)}
            >
              Next
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </section>
      {editor !== undefined && (
        <Editor
          config={config}
          item={editor}
          close={() => setEditor(undefined)}
          saved={() => {
            setEditor(undefined);
            reload();
          }}
        />
      )}
      {detail && (
        <Details name={name} item={detail} close={() => setDetail(null)} />
      )}
      {deleting && (
        <Modal
          title={"Delete this " + config.singular + "?"}
          close={() => setDeleting(null)}
        >
          <p>
            This will permanently remove this record. Records used elsewhere are
            protected.
          </p>
          <div className="form-actions">
            <button className="secondary" onClick={() => setDeleting(null)}>
              Cancel
            </button>
            <button
              className="primary destructive"
              disabled={busy}
              onClick={remove}
            >
              {busy ? "Deleting…" : "Delete record"}
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
