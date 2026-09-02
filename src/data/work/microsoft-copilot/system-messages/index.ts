import type { WorkItem } from "@/types";

export const systemMessages: WorkItem = {
  parentSlug: "microsoft-copilot",
  slug: "system-messages",
  title: "System messages",
  description:
    "Notes on classifying chat messages that confirm an action or mark a change without speaking as the assistant.",
  label: "Chat UX / content design",
  year: "2025 to present",
  status: "draft",
  passwordProtected: true,
  confidentialityNote:
    "I have left out internal scenarios, product policy, visual details, and implementation details.",
  sections: [
    {
      type: "text",
      heading: "Some chat messages belong to the system",
      content:
        "A system message is neither user input nor assistant output. It records an event in the chat, such as a completed action or a session change. The framework groups those events before the team chooses copy or a visual pattern.",
    },
    {
      type: "framework",
      label: "Classification system",
      heading: "Classify the event before choosing a pattern",
      content:
        "We tried to give each scenario one primary job. When a scenario appeared to need two patterns, we went back and clarified the event first.",
      items: [
        {
          title: "Action receipt",
          content:
            "A short message that confirms a completed action at that point in the conversation.",
        },
        {
          title: "Session lifecycle",
          content:
            "A divider that marks the beginning or end of a session or mode.",
        },
        {
          title: "Context change",
          content:
            "A marker that tells the reader when the conversation context changes.",
        },
        {
          title: "Conversation-wide notice",
          content:
            "A notice for a condition that applies to the conversation rather than one message.",
        },
      ],
    },
    {
      type: "image-full",
      images: ["/shots/system-messages-site/system-messages-site__home-desktop-hero.png"],
      caption: "Public documentation prototype for the system-message framework",
    },
    {
      type: "text",
      heading: "The framework also needed exclusions",
      content:
        "We excluded assistant output, service errors, and ordinary interface changes. Adding a neutral sentence to the timeline did not make those states clearer. The classification was more useful when it also told the team not to add a message.",
    },
    {
      type: "text",
      heading: "Ask what changed before styling the message",
      content:
        "We checked whether an event belonged at one point in the timeline or across the conversation, whether it was complete or ongoing, and whether the interface already explained it. That kept the decision focused on the event rather than a preferred component.",
    },
    {
      type: "text",
      heading: "Write like a receipt, not a speaker",
      content:
        "System copy should state the change in one sentence and leave out conversational filler. Links stay secondary. The message records an event; it does not join the conversation.",
    },
  ],
};
