import { createRoot } from 'react-dom/client';
import { Scene } from '../../components/workspace/ThreeUIPaperScene';

export function mountThreeUIPaper(host: HTMLElement) {
  const root = createRoot(host);
  root.render(<Scene />);
  return () => root.unmount();
}
