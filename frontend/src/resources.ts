export type Field = {
  key: string;
  label: string;
  type?: string;
  source?: string;
  required?: boolean;
  options?: [string, string][];
};
export type Resource = {
  title: string;
  singular: string;
  description: string;
  endpoint: string;
  id: string;
  columns: [string, string][];
  fields: Field[];
};
const text = (key: string, label: string, type = "text"): Field => ({
  key,
  label,
  type,
  required: true,
});
const select = (
  key: string,
  label: string,
  source: string,
  required = true,
): Field => ({ key, label, type: "select", source, required });
export const resources: Record<string, Resource> = {
  subjects: {
    title: "Subjects",
    singular: "subject",
    description: "The curriculum, connected to the people who teach it.",
    endpoint: "academic/subjects/",
    id: "subject_id",
    columns: [
      ["subject_code", "Code"],
      ["subject_name", "Subject"],
      ["teacher_name", "Teacher"],
    ],
    fields: [
      text("subject_name", "Subject name"),
      text("subject_code", "Subject code"),
      select("teacher_id", "Teacher", "teachers"),
    ],
  },
  classes: {
    title: "Classes",
    singular: "class",
    description: "A home for each cohort, its subjects, and its class teacher.",
    endpoint: "academic/classes/",
    id: "class_id",
    columns: [
      ["class_name", "Class"],
      ["semester", "Semester"],
      ["session", "Session"],
      ["academic_year", "Academic year"],
      ["teacher_name", "Class teacher"],
      ["student_count", "Students"],
    ],
    fields: [
      text("class_name", "Class name"),
      text("semester", "Semester", "number"),
      text("session", "Session", "number"),
      text("academic_year", "Academic year"),
      select("class_teacher", "Class teacher", "teachers"),
      { ...select("subjects", "Subjects", "subjects", false), type: "multi" },
    ],
  },
  enrollments: {
    title: "Enrollments",
    singular: "enrollment",
    description: "Connect students with their academic classes.",
    endpoint: "academic/enrollments/",
    id: "id",
    columns: [
      ["student_name", "Student"],
      ["class_name", "Class"],
      ["enrolled_at", "Enrolled on"],
    ],
    fields: [
      select("student", "Student", "students"),
      select("academic_class", "Class", "classes"),
    ],
  },
  exams: {
    title: "Exams",
    singular: "exam",
    description: "Upcoming assessments and the subjects they belong to.",
    endpoint: "academic/exams/",
    id: "exam_id",
    columns: [
      ["exam_name", "Exam"],
      ["subject_name", "Subject"],
      ["exam_date", "Date"],
    ],
    fields: [
      text("exam_name", "Exam name"),
      select("subject_id", "Subject", "subjects"),
      text("exam_date", "Exam date", "date"),
    ],
  },
  results: {
    title: "Results",
    singular: "result",
    description: "Student performance, with grades calculated automatically.",
    endpoint: "academic/results/",
    id: "result_id",
    columns: [
      ["student_name", "Student"],
      ["subject_name", "Subject"],
      ["exam_name", "Exam"],
      ["marks", "Marks / 100"],
      ["grade", "Grade"],
    ],
    fields: [
      select("subject_id", "Subject", "subjects"),
      select("exam_id", "Exam", "exams"),
      select("user_id", "Student", "students"),
      text("marks", "Marks out of 100", "number"),
    ],
  },
  notices: {
    title: "Notice board",
    singular: "notice",
    description: "The latest updates from your department.",
    endpoint: "academic/notices/",
    id: "notice_id",
    columns: [
      ["notice_title", "Title"],
      ["subject_name", "Audience"],
      ["author_name", "Posted by"],
      ["notice_date", "Updated on"],
    ],
    fields: [
      text("notice_title", "Title"),
      text("notice_description", "Announcement", "textarea"),
      select(
        "subject_id",
        "Subject (leave blank for the whole department)",
        "subjects",
        false,
      ),
    ],
  },
  clubs: {
    title: "Clubs",
    singular: "club",
    description:
      "Find your people. Make something happen beyond the classroom.",
    endpoint: "academic/clubs/",
    id: "club_id",
    columns: [
      ["club_name", "Club"],
      ["coordinator_name", "Coordinator"],
      ["member_count", "Members"],
    ],
    fields: [
      text("club_name", "Club name"),
      text("club_description", "About the club", "textarea"),
      select("user_id", "Coordinator", "users"),
    ],
  },
  users: {
    title: "People",
    singular: "person",
    description: "Manage the students, teachers, and heads in your department.",
    endpoint: "user/users/",
    id: "id",
    columns: [
      ["name", "Name"],
      ["email", "Email"],
      ["user_type", "Role"],
      ["is_active", "Status"],
    ],
    fields: [
      text("name", "Full name"),
      text("email", "Email", "email"),
      {
        key: "user_type",
        label: "Role",
        type: "select",
        required: true,
        options: [
          ["S", "Student"],
          ["T", "Teacher"],
          ["H", "Head"],
        ],
      },
      { key: "is_active", label: "Active account", type: "checkbox" },
      {
        key: "password",
        label: "Password (required for a new account)",
        type: "password",
      },
    ],
  },
};
export const roles = { H: "Department head", T: "Teacher", S: "Student" };
export function label(item: Record<string, any>) {
  return (
    item.name ||
    item.exam_name ||
    item.class_name ||
    item.club_name ||
    item.subject_name
  );
}
export function itemId(item: Record<string, any>) {
  return (
    item.id || item.exam_id || item.class_id || item.club_id || item.subject_id
  );
}
