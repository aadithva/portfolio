import { MathUtils, Spherical, Vector3 } from 'three';

/** Offsets from an authored view, never a free-roaming camera. */
export class DeskCameraOrbit {
  static readonly limits = { yaw: MathUtils.degToRad(22), pitch: MathUtils.degToRad(10), near: .76, far: 1.08 };
  private desired = new Vector3(0, 0, 1);
  private current = new Vector3(0, 0, 1);
  private spherical = new Spherical();
  private offset = new Vector3();

  get yaw() { return this.current.x; }
  get pitch() { return this.current.y; }
  get distance() { return this.current.z; }
  get modified() { return Math.abs(this.desired.x) + Math.abs(this.desired.y) + Math.abs(this.desired.z - 1) > .0001; }
  get canZoomIn() { return this.desired.z > DeskCameraOrbit.limits.near + .001; }
  get canZoomOut() { return this.desired.z < DeskCameraOrbit.limits.far - .001; }
  get zoom() { return 1 / this.desired.z; }

  rotate(x: number, y: number) {
    const { yaw, pitch } = DeskCameraOrbit.limits;
    this.desired.x = MathUtils.clamp(this.desired.x + x, -yaw, yaw);
    this.desired.y = MathUtils.clamp(this.desired.y + y, -pitch, pitch);
  }

  zoomBy(factor: number) {
    if (!Number.isFinite(factor) || factor <= 0) return;
    const { near, far } = DeskCameraOrbit.limits;
    this.desired.z = MathUtils.clamp(this.desired.z * factor, near, far);
  }

  reset() { this.desired.set(0, 0, 1); this.current.copy(this.desired); }

  step(dt: number, immediate: boolean) {
    this.current.lerp(this.desired, immediate ? 1 : 1 - Math.exp(-dt * 15));
    if (this.current.distanceToSquared(this.desired) < .0000001) this.current.copy(this.desired);
    return this.current.distanceToSquared(this.desired) > 0;
  }

  apply(position: Vector3, target: Vector3) {
    if (this.current.x === 0 && this.current.y === 0 && this.current.z === 1) return;
    this.offset.copy(position).sub(target);
    this.spherical.setFromVector3(this.offset);
    this.spherical.theta += this.current.x;
    this.spherical.phi = MathUtils.clamp(this.spherical.phi + this.current.y, .35, 1.4);
    this.spherical.radius *= this.current.z;
    position.copy(target).add(this.offset.setFromSpherical(this.spherical));
    // All authored views approach the open front of the room. Keep the camera
    // above the tabletop and on this side of the furniture, even at the limits.
    position.y = Math.max(position.y, 1.48);
    position.z = Math.max(position.z, .08);
  }
}
