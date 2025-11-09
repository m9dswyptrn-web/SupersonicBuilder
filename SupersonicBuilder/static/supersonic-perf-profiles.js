/**
 * supersonic-perf-profiles.js
 * Performance profiles for Supersonic Commander
 */

const PROFILE_PRESETS = {
  quiet: {
    perf: { fpsMin: 22, fpsRelease: 35, fpsDurationMs: 2500, rttMaxMs: 700, rttDurationMs: 3500, cooldownMs: 20000 },
    masterVol: 0.35,
    vols: { ready: 0.9, online: 0.9, error: 0.7, bench: 0.9, voice: 0.9 },
    reducedMotion: true,
    theme: 'dark'
  },
  balanced: {
    perf: { fpsMin: 25, fpsRelease: 40, fpsDurationMs: 2000, rttMaxMs: 500, rttDurationMs: 3000, cooldownMs: 15000 },
    masterVol: 0.7,
    vols: { ready: 1.0, online: 1.0, error: 0.9, bench: 1.0, voice: 1.0 },
    reducedMotion: false,
    theme: 'dark'
  },
  performance: {
    perf: { fpsMin: 30, fpsRelease: 48, fpsDurationMs: 1200, rttMaxMs: 350, rttDurationMs: 2000, cooldownMs: 9000 },
    masterVol: 0.85,
    vols: { ready: 1.1, online: 1.0, error: 0.8, bench: 1.1, voice: 1.0 },
    reducedMotion: false,
    theme: 'dark'
  }
};

function applyProfile(name) {
  const P = PROFILE_PRESETS[name];
  if (!P) {
    console.error('Unknown profile:', name);
    return;
  }

  if (!window.SETTINGS) window.SETTINGS = {};

  window.SETTINGS.perf = Object.assign({}, window.SETTINGS.perf || {}, P.perf);
  window.SETTINGS.volume = P.masterVol;
  window.SETTINGS.volumes = Object.assign({}, window.SETTINGS.volumes || {}, P.vols);

  if (P.reducedMotion) document.body.classList.add('reduced-motion');
  else document.body.classList.remove('reduced-motion');

  window.SETTINGS.profile = name;

  if (typeof window.saveSettings === 'function') window.saveSettings();
  if (typeof window.applySettingsToUI === 'function') window.applySettingsToUI();

  updateProfileTag();
  
  const msProfileTxt = document.getElementById('msProfileTxt');
  if (msProfileTxt) msProfileTxt.textContent = name;

  const status = document.getElementById('status');
  if (status) {
    status.textContent = `Profile applied: ${name}`;
    setTimeout(() => status.textContent = '', 2000);
  }
}

function updateProfileTag() {
  const tag = document.getElementById('profileTag');
  if (!tag) return;
  const n = window.SETTINGS?.profile || 'balanced';
  tag.textContent = 'Current: ' + n;
}

function detectClosestProfile() {
  const S = window.SETTINGS;
  if (!S) return;

  let best = 'balanced', bestScore = Infinity;

  for (const [name, P] of Object.entries(PROFILE_PRESETS)) {
    let score = 0;
    const Q = P.perf, R = S.perf || {};
    score += Math.abs((R.fpsMin ?? 0) - Q.fpsMin);
    score += Math.abs((R.fpsRelease ?? 0) - Q.fpsRelease);
    score += Math.abs((R.fpsDurationMs ?? 0) - Q.fpsDurationMs) / 200;
    score += Math.abs((R.rttMaxMs ?? 0) - Q.rttMaxMs) / 10;
    score += Math.abs((R.rttDurationMs ?? 0) - Q.rttDurationMs) / 200;
    score += Math.abs((R.cooldownMs ?? 0) - Q.cooldownMs) / 500;
    score += Math.abs((S.volume ?? 0) - P.masterVol) * 10;
    if (score < bestScore) { bestScore = score; best = name; }
  }

  S.profile = best;
  updateProfileTag();
}

window.applyProfile = applyProfile;
window.updateProfileTag = updateProfileTag;
window.detectClosestProfile = detectClosestProfile;
window.PROFILE_PRESETS = PROFILE_PRESETS;
