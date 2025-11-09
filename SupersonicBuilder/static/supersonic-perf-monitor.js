/**
 * supersonic-perf-monitor.js
 * Enterprise-grade performance monitoring for Supersonic Commander
 * Features:
 * - Real-time FPS monitoring with EMA smoothing
 * - Network latency (RTT) tracking
 * - Automated performance watchdog with configurable thresholds
 * - Performance profiles (Quiet, Balanced, Performance)
 * - Auto-optimization on performance degradation
 */

class SupersonicPerfMonitor {
  constructor() {
    this.fpsLast = performance.now();
    this.fpsEMA = 60;
    this.fpsMin = 999;
    this.fpsMax = 0;
    this.rttEMA = 0;
    this.rttMin = 1e9;
    this.rttMax = 0;
    this.lowFpsSince = null;
    this.highRttSince = null;
    this.lastFpsAlert = 0;
    this.lastRttAlert = 0;
    this.perfTweaksActive = false;
    this.rafHandle = null;
    this.pingInterval = null;
  }

  init() {
    this.startFpsMonitoring();
    this.startPing();
    this.bindUI();
  }

  startFpsMonitoring() {
    const tick = (t) => {
      const dt = t - this.fpsLast;
      this.fpsLast = t;
      if (dt > 0) {
        const inst = 1000 / dt;
        this.fpsEMA = this.fpsEMA * 0.9 + inst * 0.1;
        this.fpsMin = Math.min(this.fpsMin, inst);
        this.fpsMax = Math.max(this.fpsMax, inst);
        this.updatePerfLabel();
      }
      this.rafHandle = requestAnimationFrame(tick);
    };
    this.rafHandle = requestAnimationFrame(tick);
  }

  async startPing() {
    const pingOnce = async () => {
      try {
        const t0 = performance.now();
        const url = `/api/ping?t=${encodeURIComponent(Date.now())}`;
        const res = await fetch(url, { cache: 'no-store' });
        const t1 = performance.now();
        if (res.ok) {
          const rtt = Math.max(0, t1 - t0);
          this.rttEMA = this.rttEMA === 0 ? rtt : (this.rttEMA * 0.85 + rtt * 0.15);
          this.rttMin = Math.min(this.rttMin, rtt);
          this.rttMax = Math.max(this.rttMax, rtt);
          this.updatePerfLabel();
        }
      } catch (e) {
        this.rttEMA = 999;
        this.rttMax = Math.max(this.rttMax, 999);
        this.updatePerfLabel();
      }
    };

    this.pingInterval = setInterval(pingOnce, 1500);
    pingOnce();
  }

  updatePerfLabel() {
    const fps = this.fmtFps(this.fpsEMA);
    const rtt = this.fmtMs(this.rttEMA);
    const color = this.perfColorFor(fps, rtt);
    const dot = { green: '🟢', yellow: '🟡', red: '🔴' }[color] || '⏱️';

    const txt = document.getElementById('msPerfTxt');
    const icon = document.getElementById('msPerfIcon');
    if (txt) txt.textContent = `${fps} fps / ${rtt} ms`;
    if (icon) icon.textContent = `⏱️ ${dot}`;

    const ppFps = document.getElementById('ppFps');
    const ppRtt = document.getElementById('ppRtt');
    const pfmin = document.getElementById('ppFpsMin');
    const pfmax = document.getElementById('ppFpsMax');
    const prmin = document.getElementById('ppRttMin');
    const prmax = document.getElementById('ppRttMax');

    if (ppFps) ppFps.textContent = `${fps} fps`;
    if (ppRtt) ppRtt.textContent = `${rtt} ms`;
    if (pfmin) pfmin.textContent = `${this.fmtFps(this.fpsMin)}`;
    if (pfmax) pfmax.textContent = `${this.fmtFps(this.fpsMax)}`;
    if (prmin) prmin.textContent = `${this.fmtMs(this.rttMin)}`;
    if (prmax) prmax.textContent = `${this.fmtMs(this.rttMax)}`;

    this.watchdogTick(fps, rtt);
  }

  watchdogTick(currentFps, currentRttMs) {
    if (!window.SETTINGS || !window.SETTINGS.perf) return;

    const P = window.SETTINGS.perf;
    const FPS_MIN = P.fpsMin ?? 25;
    const FPS_RELEASE = P.fpsRelease ?? 40;
    const FPS_MIN_DUR = P.fpsDurationMs ?? 2000;
    const RTT_MAX = P.rttMaxMs ?? 500;
    const RTT_MAX_DUR = P.rttDurationMs ?? 3000;
    const COOLDOWN = P.cooldownMs ?? 15000;

    const now = Date.now();

    if (currentFps < FPS_MIN) {
      if (this.lowFpsSince == null) this.lowFpsSince = now;
      const sustained = (now - this.lowFpsSince) >= FPS_MIN_DUR;
      if (sustained && (now - this.lastFpsAlert) >= COOLDOWN) {
        this.lastFpsAlert = now;
        this.showToast('⚠️ Low FPS detected — reducing motion can help');
        if (window.SETTINGS?.perfAuto) this.applyPerfTweaks();
      }
    } else {
      this.lowFpsSince = null;
      if (currentFps >= FPS_RELEASE && this.perfTweaksActive) this.restorePerfTweaks();
    }

    if (currentRttMs >= RTT_MAX) {
      if (this.highRttSince == null) this.highRttSince = now;
      const sustained = (now - this.highRttSince) >= RTT_MAX_DUR;
      if (sustained && (now - this.lastRttAlert) >= COOLDOWN) {
        this.lastRttAlert = now;
        this.showToast('🌐 High latency — network busy or server load');
        if (window.SETTINGS?.perfAuto && !this.perfTweaksActive) this.applyPerfTweaks();
      }
    } else {
      this.highRttSince = null;
    }
  }

  applyPerfTweaks() {
    if (this.perfTweaksActive) return;
    this.perfTweaksActive = true;

    document.body.classList.add('reduced-motion');

    if (window.SETTINGS) {
      window.SETTINGS.volume = Math.min(window.SETTINGS.volume ?? 1, 0.4);
      if (typeof window.saveSettings === 'function') window.saveSettings();
    }

    const msBoost = document.getElementById('msBoost');
    if (msBoost) msBoost.classList.add('active');

    this.showToast('Performance mode applied (reduced motion, lower volume)');
  }

  restorePerfTweaks() {
    if (!this.perfTweaksActive) return;
    this.perfTweaksActive = false;

    document.body.classList.remove('reduced-motion');

    const msBoost = document.getElementById('msBoost');
    if (msBoost) msBoost.classList.remove('active');

    this.showToast('Performance mode released');
  }

  async runBenchmark() {
    this.showToast('Running 5s performance sample…');
    let localFpsMin = 999, localFpsMax = 0, localRttMin = 1e9, localRttMax = 0, rttSum = 0, rttN = 0;
    const endAt = performance.now() + 5000;

    const pingFast = async () => {
      const t0 = performance.now();
      try {
        const res = await fetch(`/api/ping?t=${Date.now()}`, { cache: 'no-store' });
        const t1 = performance.now();
        if (res.ok) {
          const r = t1 - t0;
          rttSum += r;
          rttN++;
          localRttMin = Math.min(localRttMin, r);
          localRttMax = Math.max(localRttMax, r);
        }
      } catch (_) { }
    };

    while (performance.now() < endAt) {
      const fpsInst = 1000 / Math.max(1, performance.now() - this.fpsLast);
      localFpsMin = Math.min(localFpsMin, fpsInst);
      localFpsMax = Math.max(localFpsMax, fpsInst);
      pingFast();
      await new Promise(r => setTimeout(r, 250));
    }

    const avgRtt = rttN ? (rttSum / rttN) : NaN;
    document.getElementById('ppFpsMin').textContent = `${this.fmtFps(localFpsMin)}`;
    document.getElementById('ppFpsMax').textContent = `${this.fmtFps(localFpsMax)}`;
    document.getElementById('ppRttMin').textContent = isFinite(localRttMin) ? `${this.fmtMs(localRttMin)}` : '—';
    document.getElementById('ppRttMax').textContent = isFinite(localRttMax) ? `${this.fmtMs(localRttMax)}` : '—';
    document.getElementById('ppRtt').textContent = isFinite(avgRtt) ? `${this.fmtMs(avgRtt)} ms` : '—';
    this.showToast('Performance sample complete');
  }

  bindUI() {
    const btn = document.getElementById('msPerf');
    const pop = document.getElementById('msPerfPop');
    const burst = document.getElementById('ppBurstBtn');
    const boost = document.getElementById('msBoost');
    const profile = document.getElementById('msProfile');

    if (btn && pop) {
      btn.addEventListener('click', () => {
        pop.style.display = (pop.style.display === 'none' || !pop.style.display) ? 'block' : 'none';
      });

      document.addEventListener('click', (e) => {
        if (!pop.contains(e.target) && e.target !== btn) {
          pop.style.display = 'none';
        }
      });
    }

    if (burst) {
      burst.addEventListener('click', () => this.runBenchmark());
    }

    if (boost) {
      boost.addEventListener('click', () => {
        if (this.perfTweaksActive) this.restorePerfTweaks();
        else this.applyPerfTweaks();
      });
    }

    if (profile) {
      profile.addEventListener('click', () => {
        const order = ['quiet', 'balanced', 'performance'];
        const cur = window.SETTINGS?.profile || 'balanced';
        const next = order[(order.indexOf(cur) + 1) % order.length];
        if (typeof window.applyProfile === 'function') {
          window.applyProfile(next);
        }
      });
    }
  }

  fmtFps(x) { return Math.max(0, Math.round(x)); }
  fmtMs(x) { return Math.max(0, Math.round(isFinite(x) ? x : 0)); }

  perfColorFor(fps, rtt) {
    const fpsOK = fps >= 50;
    const fpsWarn = fps >= 30;
    const rttOK = rtt <= 100;
    const rttWarn = rtt <= 300;

    if (fpsOK && rttOK) return 'green';
    if (fpsWarn && rttWarn) return 'yellow';
    return 'red';
  }

  showToast(msg) {
    const status = document.getElementById('status');
    if (status) {
      status.textContent = msg;
      setTimeout(() => status.textContent = '', 3000);
    } else {
      console.log(`[Perf] ${msg}`);
    }
  }

  destroy() {
    if (this.rafHandle) cancelAnimationFrame(this.rafHandle);
    if (this.pingInterval) clearInterval(this.pingInterval);
  }
}

window.SupersonicPerfMonitor = SupersonicPerfMonitor;
