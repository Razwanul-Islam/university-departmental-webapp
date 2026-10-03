import { useState, type FormEvent } from "react";
import {
  ArrowRight,
  BookOpen,
  Users,
  GraduationCap,
  CircleHelp,
} from "lucide-react";
import { send, saveTokens, type User } from "../api";
import { ErrorBox } from "../ui";

export default function Auth({ onLogin }: { onLogin: (user: User) => void }) {
  const [register, setRegister] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await send(
        "user/" + (register ? "register/" : "login/"),
        "POST",
        Object.fromEntries(new FormData(event.currentTarget)),
      );
      saveTokens(response.token);
      onLogin(response.user);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="auth">
      <section className="auth-story">
        <div className="brand">
          <GraduationCap />
          <span>
            department<span className="brand-dot">.</span>
          </span>
        </div>
        <div>
          <span className="eyebrow">YOUR ACADEMIC HOME</span>
          <h1>
            Everything you need.
            <br />
            <em>One place to grow.</em>
          </h1>
          <p>
            From your first class to your next big idea. Stay connected to your
            subjects, your people, and your department.
          </p>
          <div className="auth-features">
            <span>
              <BookOpen size={18} />
              Learning
            </span>
            <span>
              <Users size={18} />
              Community
            </span>
            <span>
              <GraduationCap size={18} />
              Progress
            </span>
          </div>
        </div>
        <small>Built for the everyday life of your department.</small>
      </section>
      <section className="auth-form">
        <div className="auth-card">
          <span className="tag">ACADEMIC PORTAL</span>
          <h2>{register ? "Start your journey" : "Welcome back"}</h2>
          <p>
            {register
              ? "Create your student account. Your department will arrange your enrollment."
              : "Sign in to your departmental workspace."}
          </p>
          <form onSubmit={submit}>
            <ErrorBox message={error} />
            {register && (
              <label>
                Full name
                <input
                  name="name"
                  maxLength={50}
                  autoComplete="name"
                  required
                />
              </label>
            )}
            <label>
              Email address
              <input
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@university.edu"
                required
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                minLength={register ? 8 : undefined}
                autoComplete={register ? "new-password" : "current-password"}
                required
              />
            </label>
            {register && (
              <label>
                Confirm password
                <input
                  name="password2"
                  type="password"
                  autoComplete="new-password"
                  required
                />
              </label>
            )}
            <button className="primary" disabled={busy}>
              {busy ? "Please wait…" : register ? "Create account" : "Sign in"}
              <ArrowRight size={18} />
            </button>
          </form>
          <p className="auth-switch">
            {register ? "Already have an account?" : "New to the department?"}{" "}
            <button
              className="text-button"
              onClick={() => {
                setRegister(!register);
                setError("");
              }}
            >
              {register ? "Sign in" : "Create an account"}
            </button>
          </p>
          <div className="auth-note">
            <CircleHelp size={16} />
            <span>Need a staff account? Contact your department head.</span>
          </div>
        </div>
      </section>
    </main>
  );
}
