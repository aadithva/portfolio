import { ThreeDPaper } from '@designcodeio/threeui';
import '@designcodeio/threeui/style.css';

/** The registered Original component, with its authored source and props intact. */
export function Scene() {
  return (
    <div className="shader-frame">
      <ThreeDPaper variant="original" />
    </div>
  );
}
