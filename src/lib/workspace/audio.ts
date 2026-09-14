/** All audio is synthesized locally. Nothing starts before a deliberate gesture. */
export class DeskAudio {
  private context?: AudioContext;
  private master?: GainNode;
  private ambient?: GainNode;
  private oscillators: OscillatorNode[] = [];
  private lastTap = -Infinity;
  enabled = false;
  playing = false;

  async enable(value: boolean) {
    if (!value) {
      this.enabled = false;
      this.pause();
      if (this.master && this.context) this.master.gain.setTargetAtTime(0, this.context.currentTime, .035);
      return;
    }
    this.context ??= new AudioContext();
    this.master ??= this.context.createGain();
    this.master.connect(this.context.destination);
    await this.context.resume();
    this.enabled = true;
    this.master.gain.setTargetAtTime(.13, this.context.currentTime, .035);
  }

  tap(kind: 'metal' | 'switch' = 'metal') {
    if (!this.enabled || !this.context || !this.master || performance.now() - this.lastTap < 900) return;
    this.lastTap = performance.now();
    const ctx = this.context, now = ctx.currentTime;
    for (const frequency of kind === 'metal' ? [718, 1193, 1921] : [280]) {
      const osc = ctx.createOscillator(), gain = ctx.createGain();
      osc.frequency.value = frequency;
      osc.type = 'sine';
      gain.gain.setValueAtTime(kind === 'metal' ? .14 : .25, now);
      gain.gain.exponentialRampToValueAtTime(.0001, now + .22);
      osc.connect(gain); gain.connect(this.master); osc.start(now); osc.stop(now + .25);
      osc.onended = () => { osc.disconnect(); gain.disconnect(); };
    }
  }

  async toggleAmbient() {
    if (this.playing) { this.pause(); return; }
    if (!this.enabled) await this.enable(true);
    const ctx = this.context!;
    this.ambient = ctx.createGain();
    this.ambient.gain.setValueAtTime(0, ctx.currentTime);
    this.ambient.gain.linearRampToValueAtTime(.1, ctx.currentTime + 1.5);
    this.ambient.connect(this.master!);
    // Soft, unmetered chord. No external music requests or autoplay.
    [130.81, 196, 261.63, 329.63].forEach((frequency, i) => {
      const osc = ctx.createOscillator();
      osc.type = 'sine'; osc.frequency.value = frequency; osc.detune.value = i % 2 ? 3 : -3;
      osc.connect(this.ambient!); osc.start(); this.oscillators.push(osc);
    });
    this.playing = true;
  }

  pause() {
    this.oscillators.forEach(osc => { osc.stop(); osc.disconnect(); });
    this.oscillators = [];
    this.ambient?.disconnect();
    this.playing = false;
  }
  suspend() { if (this.context?.state === 'running') void this.context.suspend(); }
  resume() { if (this.enabled) void this.context?.resume(); }
  dispose() { this.pause(); void this.context?.close(); }
}
