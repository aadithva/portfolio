import workspaceAsset from '../../../public/models/workspace-saved.manifest.json';

/** Coordinates are in the exported glTF's Y-up space. Keep views and bindings here. */
export type SectionId = 'work' | 'about' | 'writing' | 'achievements' | 'experiments' | 'contact' | 'design' | 'play' | 'expeditions';
export type GuidedViewId = 'overview' | 'desk-detail' | 'shelf-detail';
export type AchievementId = 'iitg-degree' | 'ride-for-unity';
export type ViewId = GuidedViewId | 'computer' | 'medal-detail' | SectionId;
export type CameraView = { position: [number, number, number]; target: [number, number, number]; fov: number };
export const views: Record<ViewId, CameraView> = {
  overview: { position: [2.4, 3.7, 5.7], target: [0, 1.7, -.9], fov: 36 },
  'desk-detail': { position: [.75, 2.75, 1.55], target: [0, 1.68, -1.12], fov: 38 },
  'shelf-detail': { position: [.5, 3.1, 1.6], target: [-.1, 2.69, -1.46], fov: 40 },
  // Fallback before loading. The computer camera is fitted to the actual screen.
  computer: { position: [0, 1.72, -.33], target: [0, 1.72, -1.13], fov: 36 },
  work: { position: [.08, 1.96, .85], target: [0, 1.72, -1.26], fov: 36 },
  about: { position: [-.8, 3.14, .4], target: [-.8, 2.9, -1.7], fov: 38 },
  contact: { position: [-.65, 2.85, .2], target: [-.68, 2.65, -1.7], fov: 38 },
  writing: { position: [-.75, 2.56, .2], target: [-.72, 2.27, -1.5], fov: 38 },
  achievements: { position: [1.144, 3.0825, -.895], target: [-.2, 2.9825, -2.239], fov: 40 },
  'medal-detail': { position: [.1, 2.42, -.18], target: [0, 2.24, -1.283], fov: 40 },
  experiments: { position: [.1, 2.65, .45], target: [0, 1.35, -.92], fov: 39 },
  design: { position: [-.9, 2.95, .1], target: [-.73, 2.25, -1.5], fov: 39 },
  play: { position: [.5, 2.4, .5], target: [0, 1.36, -.9], fov: 42 },
  expeditions: { position: [1.42, 2.38, 3.81], target: [-2.08, 2.13, .31], fov: 40 },
};
// The mobile stage starts below the introduction. Favor the monitor and desk surface.
export const mobileViews: Partial<Record<ViewId, CameraView>> = {
  overview: { position: [.558, 3.439, 4.152], target: [-.17, 2.14, -1.0], fov: 39 },
  'desk-detail': { position: [.25, 2.55, 1.8], target: [0, 1.66, -1.1], fov: 39 },
  'shelf-detail': { position: [.1, 3.0, 1.8], target: [-.05, 2.7, -1.46], fov: 40 },
};
export const scenePalette = {
  background: '#191918', panel: '#222220', raised: '#2b2b28',
  ivory: '#eeeae2', muted: '#aaa69e', red: '#e05243', brightRed: '#f47867',
};
// Runtime presentation multipliers leave the authored Blender lights and baked assets intact.
export const presentationLighting = {
  exposure: .85, indirect: .05, practicals: .5, areaFill: .08, monitor: .1,
  night: { hemisphere: .025, environment: .04 },
  day: { hemisphere: .65, environment: .25 },
};
export type ObjectBinding = { label: string; section?: SectionId; achievement?: AchievementId; action?: string; motion: 'solid' | 'paper' | 'book' | 'metal' | 'plant' | 'chair' | 'lid'; };
export const objectBindings: Record<string, ObjectBinding> = {
  monitor: { label: 'Enter my computer', section: 'work', motion: 'solid' },
  laptop: { label: 'Prototypes & side projects', section: 'experiments', motion: 'solid' },
  bicycle: { label: 'Explore my cycling expeditions', section: 'expeditions', motion: 'solid' },
  certificate_iitg: { label: 'IIT Guwahati graduation certificate', section: 'achievements', achievement: 'iitg-degree', motion: 'solid' },
  trophy_1: { label: 'Achievements', section: 'achievements', motion: 'metal' },
  trophy_2: { label: 'Achievements', section: 'achievements', motion: 'metal' },
  medal_1: { label: 'Ride for Unity medal', section: 'achievements', achievement: 'ride-for-unity', motion: 'metal' },
  books: { label: 'Writing & reading', section: 'writing', motion: 'book' },
  about: { label: 'A little about me', section: 'about', motion: 'paper' },
  contact: { label: 'Say hello', section: 'contact', motion: 'paper' },
  figma: { label: 'Design experiments', section: 'design', motion: 'lid' },
  can: { label: 'A tiny caffeine break', action: 'can', motion: 'metal' },
  lamp_1: { label: 'Toggle the top light', action: 'lamp_1', motion: 'metal' },
  lamp_2: { label: 'Toggle the middle light', action: 'lamp_2', motion: 'metal' },
  lamp_3: { label: 'Toggle the lower light', action: 'lamp_3', motion: 'metal' },
  window: { label: 'Change the time of day', action: 'day', motion: 'solid' },
  speaker: { label: 'Play / pause ambient sound', action: 'speaker', motion: 'solid' },
  controller: { label: 'A little side quest', section: 'play', motion: 'solid' },
  controller_black: { label: 'A little side quest', section: 'play', motion: 'solid' },
  plant_1: { label: 'Give the leaves a nudge', action: 'plant', motion: 'plant' },
  plant_2: { label: 'Hello, little plant', action: 'plant', motion: 'plant' },
  chair: { label: 'Take a spin', action: 'chair', motion: 'chair' },
  toy: { label: 'Hello there', action: 'toy', motion: 'solid' },
  pencil: { label: 'Nudge the pencil', action: 'pencil', motion: 'solid' },
  sticker_1: { label: 'Found a hidden sticker', action: 'sticker', motion: 'paper' },
  sticker_2: { label: 'Another hidden sticker', action: 'sticker', motion: 'paper' },
};
export const assetUrl = `${workspaceAsset.file}?v=${workspaceAsset.revision}`;
export const viewObjects: Partial<Record<ViewId, string>> = {
  work: 'monitor', about: 'about', contact: 'contact', writing: 'books',
  achievements: 'certificate_iitg', experiments: 'laptop', design: 'figma', play: 'controller',
  'medal-detail': 'medal_1',
  expeditions: 'bicycle',
};
export const achievementViews: Record<AchievementId, ViewId> = { 'iitg-degree': 'achievements', 'ride-for-unity': 'medal-detail' };
export const motionDuration = 850;
export const idleDelay = 24000;
// Bounded framing in scene units. The desk uses 1.31 units for its 75 cm height.
export const cursorFraming = { horizontal: .16, up: .24, down: .2, damping: 3.8 };
