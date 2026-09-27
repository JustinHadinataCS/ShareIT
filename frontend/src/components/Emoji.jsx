// Decorative only: hidden from screen readers so labels read as plain text.
function Emoji({ children }) {
  return <span aria-hidden="true">{children}</span>;
}

export default Emoji;
