export interface WritingNote {
  id: string;
  label: string;
  title: string;
  paragraphs: string[];
  pullquote: string;
  tags: string[];
}

export const writingNotes: WritingNote[] = [
  {
    id: "ai-design-loop",
    label: "Field note 01 / AI in product design",
    title: "AI made prototyping cheap. It did not make judgment cheap.",
    paragraphs: [
      "I have not found a separate 'AI design process' useful. I still try to understand the context and define the problem before I make an idea tangible and test what happens. AI can help with parts of that work, but it does not make any stage optional.",
      "Synthetic personas can help me find better questions before research. They cannot validate a need or reproduce the strange specificity of a real conversation. AI summaries can cluster messy notes, but evidence and product context still determine what those clusters mean. The people affected by the decision still need a say.",
      "AI saves me the most time when I turn an idea into something people can try. I now move from a rough flow to a code prototype before polishing a static specification. A working interaction exposes problems that a still screen can hide. Once it works, I still need to resolve the states, accessibility, spacing, and implementation details.",
      "A running prototype can still be unsafe or incomplete. Security, data protection, edge cases, and compliance need deliberate work. So does the interface. Sometimes I can help by making a small code fix and asking an engineer to review it. Sometimes the right call is to keep the prototype out of production.",
      "I am wary of large prompt libraries that nobody has tested. The number of prompts says little about whether they help in real work. I would rather test a small set in real scenarios and gather feedback. If an entry does not hold up, I remove it before publishing the library.",
    ],
    pullquote:
      "AI can produce more options. I still have to explain which one holds up and why.",
    tags: [
      "ai product design",
      "research",
      "prototyping",
      "code",
      "evaluation",
      "judgment",
    ],
  },
  {
    id: "invisible-interface",
    label: "Field note 02 / Conversation systems",
    title: "System messages are part of the conversation.",
    paragraphs: [
      "Some of the most important messages in a chat come from neither the user nor the assistant. A system message might confirm that an action finished or mark the end of a session. It might also explain a visibility boundary or an access condition. These messages are small, but they change what a person thinks just happened.",
      "It is tempting to design each message as a one-off. That falls apart when several teams give the same event different words and visual treatments. I found it more useful to classify each message by its job before writing it.",
      "A useful classification also needs to say what does not count. When an assistant completes a request, that is chat output. A network outage is an application error. An ignored suggestion that collapses is interface behaviour. If a change tells the user nothing new, another message usually adds noise.",
      "A system message should read like a receipt, not another speaker in the chat. One sentence is usually enough. It does not need an avatar or conversational padding. Messages that record an event should remain in the timeline. A general reminder can disappear only if the same information remains easy to find elsewhere.",
    ],
    pullquote:
      "If a state change communicates nothing new, it probably does not need another message.",
    tags: [
      "conversation design",
      "system messages",
      "content design",
      "chat",
      "taxonomy",
      "interaction design",
    ],
  },
];
