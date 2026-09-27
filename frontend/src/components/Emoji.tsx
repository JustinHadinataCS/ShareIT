import type { ReactNode } from "react";

// Decorative only: hidden from screen readers so labels read as plain text.
function Emoji({ children }: { children: ReactNode }) {
  return <span aria-hidden="true">{children}</span>;
}

export default Emoji;
