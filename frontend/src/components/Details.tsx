import { type Item } from "../api";
import { resources, roles } from "../resources";
import { Modal, date } from "../ui";

// One read-only dialog for every resource and the dashboard previews.
export default function Details({
  name,
  item,
  close,
}: {
  name: string;
  item: Item;
  close: () => void;
}) {
  const config = resources[name];
  const titleKey = name === "subjects" ? "subject_name" : config.columns[0][0];
  const extra: Record<string, [string, string][]> = {
    classes: [["subject_names", "Subjects"]],
    users: [["created_at", "Joined on"]],
    clubs: [["is_member", "Membership"]],
  };
  const fields = [...config.columns, ...(extra[name] || [])];
  const description = item.notice_description || item.club_description;

  function format(key: string) {
    const value = item[key];
    if (value == null)
      return key === "subject_name" && name === "notices" ? "Department" : "—";
    if (key === "user_type") return roles[value as keyof typeof roles];
    if (key === "is_active") return value ? "Active" : "Inactive";
    if (key === "is_member") return value ? "Joined" : "Not joined";
    if (key.endsWith("_date") || key.endsWith("_at")) return date(value);
    if (Array.isArray(value))
      return value.length ? value.join(", ") : "None assigned";
    return String(value);
  }

  return (
    <Modal title={String(item[titleKey])} close={close}>
      <dl className="record-details">
        {fields.map(([key, label]) => (
          <div key={key}>
            <dt>{label}</dt>
            <dd>{format(key)}</dd>
          </div>
        ))}
      </dl>
      {description && <p className="notice-content">{description}</p>}
    </Modal>
  );
}
