import { adventureRoute, adventureStory } from "./adventures";

export interface ExpeditionImage {
  src: string;
  alt: string;
  caption: string;
  width: number;
  height: number;
}

export interface Expedition {
  id: string;
  title: string;
  dateLabel: string;
  route: string;
  paragraphs: string[];
  facts: { label: string; value: string }[];
  showRouteMap: boolean;
  missingDetails?: string;
  images: ExpeditionImage[];
}

// Existing first-person accounts are the source of these entries. Keep the
// supported 2025 expedition distinct from the earlier, mostly independent ride.
// Do not infer a calendar year or exact mileage for the first journey.
export const expeditionsIntro = adventureStory[0];
export const expeditionsReflection = adventureStory[3];
export const expeditionRouteCaption =
  "The 2025 route, simplified. This shows the general direction, not a recorded GPS track.";
export const expeditionsMissingMedia =
  "Ride photographs and day-by-day route notes haven't been added yet.";

export const expeditions: Expedition[] = [
  {
    id: "ride-for-unity",
    title: "Ride for Unity",
    dateLabel: "2025",
    route: `${adventureRoute.start} to ${adventureRoute.finish}`,
    paragraphs: [adventureStory[2]],
    facts: [
      { label: "Distance", value: `Roughly ${adventureRoute.distance}` },
      { label: "Duration", value: adventureRoute.time },
      { label: "Group", value: "About 150 riders" },
      { label: "Representing", value: "Kerala" },
    ],
    showRouteMap: true,
    // Add only the owner's verified ride photographs, with descriptive alt text.
    images: [],
  },
  {
    id: "first-cross-country-ride",
    title: "The first ride north",
    dateLabel: "At twenty",
    route: "Kerala toward Kashmir",
    paragraphs: [adventureStory[1]],
    facts: [],
    showRouteMap: false,
    missingDetails:
      "The exact date, distance and duration of this ride aren't recorded here.",
    images: [],
  },
];
