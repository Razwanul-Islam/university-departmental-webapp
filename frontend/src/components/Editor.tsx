import { useEffect, useState, type FormEvent } from "react";
import { Check } from "lucide-react";
import { all, send, type Item } from "../api";
import { label, itemId, type Resource } from "../resources";
import { ErrorBox, Modal } from "../ui";

export default function Editor({
  config,
  item,
  close,
  saved,
}: {
  config: Resource;
  item: Item | null;
  close: () => void;
  saved: () => void;
}) {
  const [values, setValues] = useState<Item>(
    item ? { ...item } : { is_active: true, subjects: [], user_type: "S" },
  );
  const [lookups, setLookups] = useState<Record<string, Item[]>>({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    Promise.all([
      all("user/users/?is_active=true"),
      all("academic/subjects/"),
      all("academic/classes/"),
      all("academic/exams/"),
      all("academic/enrollments/"),
    ])
      .then(([users, subjects, classes, exams, enrollments]) => {
        if (active) {
          setLookups({
            users,
            teachers: users.filter((u) => u.user_type !== "S"),
            students: users.filter((u) => u.user_type === "S"),
            subjects,
            classes,
            exams,
            enrollments,
          });
          setLoading(false);
        }
      })
      .catch((e) => {
        if (active) {
          setError(e.message);
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);
  function optionsFor(source: string) {
    let items = lookups[source] || [];
    if (config.id === "result_id") {
      if (source === "exams")
        items = items.filter((e) => e.subject_id === Number(values.subject_id));
      if (source === "students") {
        const eligible = (lookups.enrollments || [])
          .filter((e) =>
            (lookups.classes || []).some(
              (c) =>
                c.class_id === e.academic_class &&
                c.subjects.includes(Number(values.subject_id)),
            ),
          )
          .map((e) => e.student);
        items = items.filter((s) => eligible.includes(s.id));
      }
    }
    return items;
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const payload: Item = {};
    for (const field of config.fields) {
      const value = values[field.key];
      if (field.type === "password" && !value) continue;
      payload[field.key] =
        field.type === "select" && field.source
          ? value
            ? Number(value)
            : null
          : field.type === "number"
            ? Number(value)
            : field.type === "checkbox"
              ? !!value
              : field.type === "multi"
                ? value || []
                : value || "";
    }
    try {
      await send(
        config.endpoint + (item ? item[config.id] + "/" : ""),
        item ? "PATCH" : "POST",
        payload,
      );
      saved();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal title={(item ? "Edit " : "New ") + config.singular} close={close}>
      <form onSubmit={submit}>
        <ErrorBox message={error} />
        {loading ? (
          <div className="loading">Loading form…</div>
        ) : (
          config.fields.map((field) => (
            <div
              key={field.key}
              className={
                "field " + (field.type === "checkbox" ? "checkbox-label" : "")
              }
            >
              <label htmlFor={field.key}>{field.label}</label>
              {field.type === "textarea" ? (
                <textarea
                  id={field.key}
                  rows={4}
                  required={field.required}
                  value={values[field.key] || ""}
                  onChange={(e) =>
                    setValues({ ...values, [field.key]: e.target.value })
                  }
                />
              ) : field.type === "select" || field.type === "multi" ? (
                <>
                  <select
                    id={field.key}
                    multiple={field.type === "multi"}
                    required={field.required}
                    value={
                      values[field.key] ?? (field.type === "multi" ? [] : "")
                    }
                    onChange={(e) => {
                      const value =
                        field.type === "multi"
                          ? Array.from(e.target.selectedOptions, (o) =>
                              Number(o.value),
                            )
                          : e.target.value;
                      setValues({
                        ...values,
                        [field.key]: value,
                        ...(field.key === "subject_id" &&
                        config.id === "result_id"
                          ? { exam_id: "", user_id: "" }
                          : {}),
                      });
                    }}
                  >
                    {field.type !== "multi" && (
                      <option value="">
                        Select{" "}
                        {field.source === "exams" ? "an exam" : "an option"}
                      </option>
                    )}
                    {(
                      field.options ||
                      optionsFor(field.source!).map((i) => [
                        String(itemId(i)),
                        label(i),
                      ])
                    ).map(([id, name]) => (
                      <option key={id} value={id}>
                        {name}
                      </option>
                    ))}
                  </select>
                  {field.type === "multi" && (
                    <small>Hold Ctrl or Cmd to choose multiple subjects.</small>
                  )}
                </>
              ) : (
                <input
                  id={field.key}
                  type={field.type || "text"}
                  autoComplete={
                    field.type === "password" ? "new-password" : undefined
                  }
                  required={
                    field.required || (field.key === "password" && !item)
                  }
                  min={
                    field.key === "marks"
                      ? 0
                      : field.key === "semester"
                        ? 1
                        : field.key === "session"
                          ? 2000
                          : undefined
                  }
                  max={
                    field.key === "marks"
                      ? 100
                      : field.key === "semester"
                        ? 12
                        : field.key === "session"
                          ? 2100
                          : undefined
                  }
                  step={field.type === "number" ? 1 : undefined}
                  checked={
                    field.type === "checkbox" ? !!values[field.key] : undefined
                  }
                  value={
                    field.type === "checkbox"
                      ? undefined
                      : (values[field.key] ?? "")
                  }
                  onChange={(e) =>
                    setValues({
                      ...values,
                      [field.key]:
                        field.type === "checkbox"
                          ? e.target.checked
                          : e.target.value,
                    })
                  }
                />
              )}
            </div>
          ))
        )}
        <div className="form-actions">
          <button type="button" className="secondary" onClick={close}>
            Cancel
          </button>
          <button className="primary" disabled={loading || busy}>
            {busy ? "Saving…" : "Save " + config.singular}
            <Check size={16} />
          </button>
        </div>
      </form>
    </Modal>
  );
}
