/** Smaller encodings of existing public imagery; originals remain in the case studies. */
export const optimizedProjectPreview = (source: string): string =>
  source === "/shots/owly-website/owly-website__home-desktop-hero.png"
    ? "/media/portfolio/owly-preview.webp"
    : source;
