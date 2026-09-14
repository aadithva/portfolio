import type { NavLink } from "@/types";

/** The same destinations and order in the room and on standalone pages. */
export const navLinks: (NavLink & { id: string })[] = [
  { id: "work", label: "Work", href: "/work" },
  { id: "about", label: "About", href: "/about" },
  { id: "writing", label: "Writing", href: "/writing" },
  { id: "achievements", label: "Achievements", href: "/achievements" },
  { id: "expeditions", label: "Expeditions", href: "/expeditions" },
  { id: "contact", label: "Contact", href: "/contact" },
];
