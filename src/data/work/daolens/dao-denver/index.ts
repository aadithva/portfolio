import type { WorkItem } from "@/types";

export const daoDenver: WorkItem = {
  parentSlug: "daolens",
  slug: "dao-denver",
  title: "DAO Denver",
  description:
    "A two-week sprint to turn a sleek B2B Web3 product into a booth people might actually stop at — designed together with Ans K James.",
  label: "Event identity / go-to-market",
  year: "2023",
  status: "documented",
  sections: [
    {
      type: "text",
      heading: "Eight deliverables. Two weeks. One trade floor.",
      content:
        "DaoLens was sponsoring a booth at DAO Denver during ETHDenver 2023. The request covered the booth, banners, social posts, stickers, merchandise, posters, pamphlets, a website, and a paper game. The Behance project credits Ans K James and me together without splitting every deliverable by person, so I present it here as a shared build — not a solo identity project with a collaborator added in the footer.",
    },
    {
      type: "image-full",
      images: ["/images/projects/dao-denver-cover.png"],
      caption: "DaoLens at DAO Denver — booth and event identity",
    },
    {
      type: "text",
      heading: "Loud, on purpose",
      content:
        "DaoLens already had a futuristic, gradient-heavy identity built for a B2B product. A trade floor needed a different volume. The event direction became bolder, brighter, flatter, and more playful — Space Mono and Poppins, blocky illustrations, and a sharp yellow accent — while keeping enough of the original brand that the booth still belonged to DaoLens.",
    },
    {
      type: "framework",
      label: "Event system",
      heading: "The same idea had to survive eight formats",
      content:
        "A booth identity only works when it still behaves at the size of a sticker, a screen, a shirt, and a very large banner.",
      items: [
        {
          title: "Stop",
          content:
            "A booth, banners, and a dartboard merch game gave people a visible reason to pause.",
        },
        {
          title: "Explain",
          content:
            "Pamphlets and website mockups translated the DAO Manager product into something visitors could understand quickly.",
        },
        {
          title: "Travel",
          content:
            "Stickers, shirts, mugs, notebooks, and tote bags let the visual language leave the booth.",
        },
        {
          title: "Continue",
          content:
            "Social posts carried panel discussions and event activations into the wider ETHDenver conversation.",
        },
      ],
    },
    {
      type: "image-grid",
      images: [
        "/images/projects/dao-denver-g1.png",
        "/images/projects/dao-denver-g2.png",
        "/images/projects/dao-denver-g3.png",
      ],
      caption: "Booth, illustration system, and event applications",
      columns: 3,
    },
    {
      type: "text",
      heading: "The game nobody expected at a DAO booth",
      content:
        "Alongside the expected merch, the system included a paper fortune-teller with deliberately silly Web3 copy. The joke was not there to prove we could write jokes. It gave someone walking past a low-stakes way to touch the brand, smile, and stay for the product conversation.",
    },
    {
      type: "image-grid",
      images: [
        "/images/projects/dao-denver-g4.png",
        "/images/projects/dao-denver-g5.png",
        "/images/projects/dao-denver-g6.png",
      ],
      caption: "Merchandise, social posts, games, and product marketing",
      columns: 3,
    },
    {
      type: "stats",
      stats: [
        { label: "Timeline", value: "2 weeks" },
        { label: "Event", value: "3 days" },
        { label: "Formats", value: "8" },
        { label: "Collaboration", value: "With Ans" },
      ],
    },
  ],
};
