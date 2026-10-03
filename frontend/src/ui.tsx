import { useEffect, type ReactNode } from "react";
import { BookOpen, X } from "lucide-react";

export const date = (value: string) =>
  new Date(
    value.length === 10 ? value + "T12:00:00" : value,
  ).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Dhaka",
  });
export const initials = (name: string) =>
  name
    .trim()
    .split(/\s+/)
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
export const navigate = (page: string) => {
  window.location.hash = page;
};
export function ErrorBox({ message }: { message: string }) {
  return message ? (
    <div className="error" role="alert">
      {message}
    </div>
  ) : null;
}
export function Empty({
  title = "Nothing here yet",
  children,
}: {
  title?: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty">
      <BookOpen size={30} />
      <h3>{title}</h3>
      <p>
        {children || "Records will appear here when your department adds them."}
      </p>
    </div>
  );
}
export function Modal({
  title,
  close,
  children,
}: {
  title: string;
  close: () => void;
  children: ReactNode;
}) {
  useEffect(() => {
    const previous = document.activeElement as HTMLElement;
    const dialog = document.querySelector<HTMLDialogElement>("dialog");
    dialog?.showModal();
    return () => {
      dialog?.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      className="modal"
      onCancel={close}
      onClick={(e) => {
        if (e.target === e.currentTarget) close();
      }}
    >
      <div className="modal-head">
        <h2>{title}</h2>
        <button
          className="icon-button"
          aria-label="Close dialog"
          onClick={close}
        >
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
