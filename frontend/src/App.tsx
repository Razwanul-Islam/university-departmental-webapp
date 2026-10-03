import { useEffect, useState } from "react";
import {
  BookOpen,
  CalendarDays,
  ClipboardList,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Menu,
  Megaphone,
  Settings,
  Users,
  Layers,
  ChevronRight,
} from "lucide-react";
import { api, hasSession, saveTokens, refreshToken, type User } from "./api";
import { resources, roles } from "./resources";
import { initials, navigate } from "./ui";
import Auth from "./components/Auth";
import Dashboard from "./components/Dashboard";
import ResourcePage from "./components/ResourcePage";
import Profile from "./components/Profile";

const nav = [
  ["dashboard", "Overview", LayoutDashboard],
  ["subjects", "Subjects", BookOpen],
  ["classes", "Classes", Layers],
  ["enrollments", "Enrollments", ClipboardList],
  ["exams", "Exams", CalendarDays],
  ["results", "Results", GraduationCap],
  ["notices", "Notice board", Megaphone],
  ["clubs", "Clubs", Users],
  ["users", "People", Users],
] as const;
export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(hasSession());
  const [page, setPage] = useState(
    window.location.hash.slice(1) || "dashboard",
  );
  const [mobile, setMobile] = useState(false);
  const [sessionError, setSessionError] = useState("");
  useEffect(() => {
    if (hasSession())
      api("user/userprofile/")
        .then(setUser)
        .catch((e) => {
          saveTokens(null);
          setSessionError(e.message);
        })
        .finally(() => setChecking(false));
    const hash = () => {
      setPage(window.location.hash.slice(1) || "dashboard");
      setMobile(false);
    };
    const expired = () => {
      setUser(null);
      setSessionError("Your session expired. Please sign in again.");
    };
    window.addEventListener("hashchange", hash);
    window.addEventListener("session-expired", expired);
    return () => {
      window.removeEventListener("hashchange", hash);
      window.removeEventListener("session-expired", expired);
    };
  }, []);
  async function logout() {
    const refresh = refreshToken();
    const request = refresh
      ? api(
          "user/logout/",
          {
            method: "POST",
            body: JSON.stringify({ refresh }),
            keepalive: true,
          },
          false,
        )
      : Promise.resolve();
    saveTokens(null);
    setUser(null);
    setPage("dashboard");
    window.location.hash = "dashboard";
    await request.catch(() => {});
  }
  if (checking)
    return (
      <div className="boot">
        <GraduationCap size={34} />
        <p>Opening your department…</p>
      </div>
    );
  if (!user)
    return (
      <>
        {sessionError && (
          <div className="session-notice" role="alert">
            {sessionError}
          </div>
        )}
        <Auth
          onLogin={(value) => {
            setUser(value);
            setSessionError("");
            navigate("dashboard");
            setPage("dashboard");
          }}
        />
      </>
    );
  const allowed =
    page === "profile" ||
    page === "dashboard" ||
    (resources[page] && (page !== "users" || user.user_type === "H"));
  const current = allowed ? page : "dashboard";
  return (
    <div className="app-shell">
      {mobile && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setMobile(false)}
        />
      )}
      <aside className={"sidebar " + (mobile ? "open" : "")}>
        <a className="brand" href="#dashboard">
          <GraduationCap size={29} />
          <span>
            department<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="workspace-label">
          <span className="workspace-icon">D</span>
          <div>
            Academic workspace<small>Departmental portal</small>
          </div>
        </div>
        <span className="nav-label">WORKSPACE</span>
        <nav>
          {nav
            .filter(([key]) => key !== "users" || user.user_type === "H")
            .map(([key, title, Icon]) => (
              <a
                key={key}
                href={"#" + key}
                className={current === key ? "active" : ""}
                aria-current={current === key ? "page" : undefined}
              >
                <Icon size={19} />
                <span>{title}</span>
                {current === key && <span className="active-dot" />}
              </a>
            ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span className="live-dot" />
            <span>
              A place to learn.
              <br />
              <strong>A community to belong.</strong>
            </span>
          </div>
          <a href="#profile" className={current === "profile" ? "active" : ""}>
            <Settings size={18} />
            Profile & settings
          </a>
          <button onClick={logout}>
            <LogOut size={18} />
            Sign out
          </button>
          <div className="sidebar-user">
            <span className="avatar">{initials(user.name)}</span>
            <div>
              <strong>{user.name}</strong>
              <small>{roles[user.user_type]}</small>
            </div>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <button
            className="icon-button mobile-toggle"
            aria-label="Open navigation"
            onClick={() => setMobile(true)}
          >
            <Menu size={21} />
          </button>
          <div className="breadcrumb">
            Workspace
            <ChevronRight size={14} />
            <strong>
              {current === "dashboard"
                ? "Overview"
                : current === "profile"
                  ? "Profile & settings"
                  : resources[current].title}
            </strong>
          </div>
          <div className="topbar-right">
            <span className="semester-pill">
              <span className="live-dot" />
              Academic portal
            </span>
            <button
              className="avatar"
              aria-label="Open profile"
              onClick={() => navigate("profile")}
            >
              {initials(user.name)}
            </button>
          </div>
        </header>
        <main className="content" key={current}>
          {current === "dashboard" ? (
            <Dashboard user={user} />
          ) : current === "profile" ? (
            <Profile user={user} updated={setUser} logout={logout} />
          ) : (
            <ResourcePage key={current} name={current} user={user} />
          )}
        </main>
        <footer>
          <span>Departmental portal</span>
          <span>Made for learning, together.</span>
        </footer>
      </div>
    </div>
  );
}
