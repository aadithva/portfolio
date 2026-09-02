import type { WorkItem } from "@/types";

export const daoDenver: WorkItem = {
  parentSlug: "daolens",
  slug: "dao-denver",
  title: "DAO Denver",
  description:
    "A two-week event sprint with Ans K James to adapt DaoLens's B2B Web3 identity for its DAO Denver booth.",
  label: "Event identity / go-to-market",
  year: "2023",
  status: "documented",
  sections: [
    {
      type: "text",
      heading: "Two weeks to prepare for DAO Denver",
      content:
        "DaoLens sponsored a booth at DAO Denver during ETHDenver 2023. The work included the booth, banners, social posts, stickers, merchandise, posters, pamphlets, a website, and a paper game. Ans K James and I are jointly credited on the Behance project, which does not document an individual role split.",
    },
    {
      type: "image-full",
      images: ["/images/projects/dao-denver-cover.png"],
      caption: "DaoLens booth and event identity at DAO Denver",
    },
    {
      type: "text",
      heading: "Loud, on purpose",
      content:
        "DaoLens already had a futuristic, gradient-heavy B2B identity. For the event, we kept parts of it and added Space Mono and Poppins, blocky illustrations, flat colour, and a sharp yellow accent.",
    },
    {
      type: "framework",
      label: "Event identity",
      heading: "Applying the identity across eight formats",
      content:
        "We applied the identity to stickers, screens, shirts, and large banners.",
      items: [
        {
          title: "Booth and banners",
          content:
            "The physical set included the booth, banners, and a dartboard merchandise game.",
        },
        {
          title: "Product material",
          content:
            "Pamphlets and website mockups explained the DAO Manager product.",
        },
        {
          title: "Merchandise",
          content:
            "We applied the visual system to stickers, shirts, mugs, notebooks, and tote bags.",
        },
        {
          title: "Social posts",
          content:
            "Social posts covered panel discussions and event activations.",
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
        "Alongside the usual stickers and shirts, we made a paper fortune-teller with deliberately silly Web3 copy.",
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
        { label: "Context", value: "ETHDenver 2023" },
        { label: "Formats", value: "8" },
        { label: "Collaboration", value: "With Ans" },
      ],
    },
  ],
};
