import { useState, type FormEvent } from "react";
import { Check, ArrowRight } from "lucide-react";
import { send, type User } from "../api";
import { roles } from "../resources";
import { ErrorBox, initials } from "../ui";

export default function Profile({
  user,
  updated,
  logout,
}: {
  user: User;
  updated: (value: User) => void;
  logout: () => Promise<void>;
}) {
  const [name, setName] = useState(user.name);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  async function save(event: FormEvent<HTMLFormElement>, password = false) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);
    try {
      if (password) {
        await send(
          "user/password/",
          "POST",
          Object.fromEntries(new FormData(event.currentTarget)),
        );
        await logout();
      } else {
        updated(await send("user/userprofile/", "PATCH", { name }));
        setSuccess("Your profile has been updated.");
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="page-title">
        <div>
          <span className="eyebrow">YOUR WORKSPACE</span>
          <h1>Profile & settings</h1>
          <p>A few details that make this space yours.</p>
        </div>
      </div>
      <ErrorBox message={error} />
      {success && (
        <div className="success" role="status">
          {success}
        </div>
      )}
      <div className="profile-grid">
        <section className="panel profile-panel">
          <div className="profile-summary">
            <span className="avatar large">{initials(user.name)}</span>
            <div>
              <h2>{user.name}</h2>
              <span className="badge green">{roles[user.user_type]}</span>
            </div>
          </div>
          <form onSubmit={save}>
            <label>
              Full name
              <input
                value={name}
                maxLength={50}
                required
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <label>
              Email address
              <input value={user.email} disabled />
            </label>
            <button className="primary" disabled={busy}>
              Save profile
              <Check size={16} />
            </button>
          </form>
        </section>
        <section className="panel profile-panel">
          <h2>Change password</h2>
          <p>You'll sign in again after changing your password.</p>
          <form onSubmit={(e) => save(e, true)}>
            <label>
              Current password
              <input
                name="old_password"
                type="password"
                autoComplete="current-password"
                required
              />
            </label>
            <label>
              New password
              <input
                name="password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
              />
            </label>
            <label>
              Confirm new password
              <input
                name="password2"
                type="password"
                autoComplete="new-password"
                required
              />
            </label>
            <button className="secondary" disabled={busy}>
              Update password
              <ArrowRight size={16} />
            </button>
          </form>
        </section>
      </div>
    </>
  );
}
