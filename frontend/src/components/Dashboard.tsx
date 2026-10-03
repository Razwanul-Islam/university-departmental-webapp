import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  BookOpen,
  CalendarDays,
  GraduationCap,
  Megaphone,
  Users,
  RefreshCw,
  ArrowRight,
} from "lucide-react";
import { api, type Item, type User } from "../api";
import { ErrorBox, Empty, date, navigate } from "../ui";
import Details from "./Details";

export default function Dashboard({ user }: { user: User }) {
  const [data, setData] = useState<Item | null>(null);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  const [detail, setDetail] = useState<{ name: string; item: Item } | null>(
    null,
  );
  useEffect(() => {
    let active = true;
    api("academic/dashboard/")
      .then((v) => {
        if (active) setData(v);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [reload]);
  return (
    <>
      <div className="page-title">
        <div>
          <span className="eyebrow">YOUR DEPARTMENT, AT A GLANCE</span>
          <h1>Overview</h1>
          <p>A little clarity for the day ahead.</p>
        </div>
        <span className="today">
          <CalendarDays size={16} />
          {date(new Date().toISOString())}
        </span>
      </div>
      <ErrorBox message={error} />
      {error && (
        <button
          className="secondary"
          onClick={() => {
            setError("");
            setReload(reload + 1);
          }}
        >
          <RefreshCw size={16} />
          Try again
        </button>
      )}
      <section className="welcome">
        <div>
          <span className="welcome-label">
            <span className="live-dot" />
            CONNECTED TO YOUR DEPARTMENT
          </span>
          <h2>Good to see you, {user.name.split(" ")[0]}.</h2>
          <p>
            {user.user_type === "H"
              ? "A clear view of your department. Keep your people and academics moving forward."
              : user.user_type === "T"
                ? "Your subjects, your students, and the progress you make together."
                : "Your next class, your latest results, and everything in between."}
          </p>
          <button onClick={() => navigate("subjects")}>
            Explore your subjects
            <ArrowUpRight size={17} />
          </button>
        </div>
        <div className="campus-art" aria-hidden="true">
          <div className="art-orbit" />
          <div className="art-building">
            <div className="art-roof" />
            <div className="art-windows">
              {Array.from({ length: 12 }, (_, i) => (
                <span key={i} />
              ))}
            </div>
            <div className="art-door" />
          </div>
          <span className="art-label">LEARN. CONNECT. GROW.</span>
        </div>
      </section>
      <section className="stats">
        {[
          ["Subjects", data?.subjects, BookOpen, "Your academic curriculum"],
          [
            "Upcoming exams",
            data?.upcoming_exams,
            CalendarDays,
            "Time to plan ahead",
          ],
          [
            "Results recorded",
            data?.results,
            GraduationCap,
            "Progress, made visible",
          ],
          ["Notice board", data?.notices, Megaphone, "Stay in the know"],
        ].map(([title, value, Icon, note], i) => {
          const Component = Icon as typeof BookOpen;
          return (
            <button
              className="stat"
              key={String(title)}
              onClick={() =>
                navigate(["subjects", "exams", "results", "notices"][i])
              }
            >
              <span className="stat-top">
                {String(title)}
                <Component size={18} />
              </span>
              <strong>{value === undefined ? "—" : String(value)}</strong>
              <span className="stat-note">
                {String(note)}
                <ArrowUpRight size={14} />
              </span>
            </button>
          );
        })}
      </section>
      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Latest announcements</h2>
              <p>The things you should know.</p>
            </div>
            <button className="text-button" onClick={() => navigate("notices")}>
              View all
              <ArrowUpRight size={15} />
            </button>
          </div>
          {!data ? (
            <div className="loading">Loading announcements…</div>
          ) : !data.recent_notices.length ? (
            <Empty title="You're all caught up" />
          ) : (
            data.recent_notices.map((n: Item) => (
              <article className="announcement" key={n.notice_id}>
                <div className="announcement-icon">
                  <Megaphone size={19} />
                </div>
                <div>
                  <span className="tag">{n.subject_name || "DEPARTMENT"}</span>
                  <h3>
                    <button
                      className="record-link"
                      onClick={() => setDetail({ name: "notices", item: n })}
                    >
                      {n.notice_title}
                    </button>
                  </h3>
                  <p>{n.notice_description}</p>
                  <small>
                    {n.author_name} · {date(n.notice_date)}
                  </small>
                </div>
              </article>
            ))
          )}
        </section>
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>On the horizon</h2>
              <p>Your next assessments.</p>
            </div>
            <CalendarDays size={20} />
          </div>
          {!data ? (
            <div className="loading">Loading exams…</div>
          ) : !data.exam_schedule.length ? (
            <Empty title="Room to focus">
              No upcoming exams are scheduled.
            </Empty>
          ) : (
            data.exam_schedule.map((e: Item) => (
              <article className="exam-preview" key={e.exam_id}>
                <div className="date-tile">
                  <span>
                    {new Date(e.exam_date + "T12:00:00").toLocaleDateString(
                      "en-GB",
                      { month: "short" },
                    )}
                  </span>
                  <strong>{e.exam_date.slice(8)}</strong>
                </div>
                <div>
                  <h3>
                    <button
                      className="record-link"
                      onClick={() => setDetail({ name: "exams", item: e })}
                    >
                      {e.exam_name}
                    </button>
                  </h3>
                  <p>{e.subject_name}</p>
                </div>
                <ArrowUpRight size={16} />
              </article>
            ))
          )}
          <button className="panel-link" onClick={() => navigate("exams")}>
            See exam schedule
            <ArrowRight size={16} />
          </button>
        </section>
      </div>
      <section className="community-strip">
        <div className="community-icon">
          <Users size={26} />
        </div>
        <div>
          <h3>There’s more to university than a classroom.</h3>
          <p>Meet your community. Find a club that feels like you.</p>
        </div>
        <button className="secondary" onClick={() => navigate("clubs")}>
          Explore clubs
          <ArrowUpRight size={16} />
        </button>
      </section>
      {detail && (
        <Details
          name={detail.name}
          item={detail.item}
          close={() => setDetail(null)}
        />
      )}
    </>
  );
}
