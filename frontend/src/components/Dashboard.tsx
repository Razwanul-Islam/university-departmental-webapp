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
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { api, type Item, type User } from "../api";
import { ErrorBox, Empty, date, navigate } from "../ui";
import Details from "./Details";

export default function Dashboard({ user }: { user: User }) {
  const [data, setData] = useState<Item | null>(null);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  const [slide, setSlide] = useState(0);
  const highlights = [
    {
      label: "YOUR ACADEMIC HOME",
      title: "Your next chapter. All in one place.",
      description: user.user_type === "H"
        ? "Bring your people, plans, and progress together. A clearer view of everything that matters."
        : user.user_type === "T"
          ? "A little more space for what you do best. Your subjects, your students, and their next breakthrough."
          : "Big ideas start with a little clarity. Your subjects, your progress, and your people, together.",
      action: "Explore your subjects",
      route: "subjects",
      icon: BookOpen,
      metric: data?.subjects,
      metricLabel: "Subjects in your workspace",
      note: "A place for possibility",
      theme: "learning",
    },
    {
      label: "MAKE ROOM FOR YOUR NEXT MILESTONE",
      title: "A clear plan. A confident next step.",
      description: "See what's coming, find your focus, and take it one day at a time. Your exam schedule is right here.",
      action: "See your exam schedule",
      route: "exams",
      icon: CalendarDays,
      metric: data?.upcoming_exams,
      metricLabel: "Upcoming assessments",
      note: "You've got this",
      theme: "focus",
    },
    {
      label: "BETTER, TOGETHER",
      title: "Find your people. Follow your curiosity.",
      description: "University goes beyond the classroom. Discover a club, share an interest, and make something of your own.",
      action: "Discover your community",
      route: "clubs",
      icon: Users,
      metric: null,
      metricLabel: "Your campus community",
      note: "There's a place for you",
      theme: "community",
    },
  ];
  const highlight = highlights[slide];
  const HighlightIcon = highlight.icon;
  const changeSlide = (direction: number) =>
    setSlide((value) => (value + direction + highlights.length) % highlights.length);
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
          <p>Good to see you, {user.name}. Make space for what matters.</p>
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
      <section
        className={"welcome " + highlight.theme}
        aria-label="Workspace highlights"
        aria-roledescription="carousel"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
            event.preventDefault();
            changeSlide(event.key === "ArrowRight" ? 1 : -1);
          }
        }}
      >
        <div className="hero-copy" key={slide} role="group" aria-roledescription="slide" aria-label={`${slide + 1} of ${highlights.length}`} aria-live="polite">
          <span className="welcome-label"><span className="live-dot" />{highlight.label}</span>
          <h2>{highlight.title}</h2>
          <p>{highlight.description}</p>
          <button className="hero-action" onClick={() => navigate(highlight.route)}>
            {highlight.action}<ArrowUpRight size={19} />
          </button>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="hero-orbit" />
          <div className="hero-glass" key={highlight.theme}>
            <span className="hero-icon"><HighlightIcon size={36} strokeWidth={1.5} /></span>
            <span className="hero-card-label">DEPARTMENT / WORKSPACE</span>
            <strong>{highlight.metric === null ? "Together." : highlight.metric ?? "�"}</strong>
            <span>{highlight.metricLabel}</span>
            <div className="hero-card-line" />
            <span className="hero-card-bottom">A little closer to your goals <ArrowUpRight size={17} /></span>
          </div>
          <div className="hero-floating"><GraduationCap size={22} /><span>{highlight.note}</span></div>
          <span className="hero-coordinate">LEARN / CONNECT / GROW</span>
        </div>
        <div className="carousel-controls">
          <div className="carousel-dots" aria-label="Choose a highlight">
            {highlights.map((item, index) => (
              <button key={item.theme} aria-label={`Show highlight ${index + 1}: ${item.title}`} aria-pressed={slide === index} onClick={() => setSlide(index)} />
            ))}
          </div>
          <span className="carousel-count">0{slide + 1}<span> / 0{highlights.length}</span></span>
          <div className="carousel-arrows">
            <button aria-label="Previous highlight" onClick={() => changeSlide(-1)}><ChevronLeft size={19} /></button>
            <button aria-label="Next highlight" onClick={() => changeSlide(1)}><ChevronRight size={19} /></button>
          </div>
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
