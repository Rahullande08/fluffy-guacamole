// AeroCold Incident Workspace Controller
import { api } from './api.js';
import { showToast } from './common-ui.js';

let incidentId = 'INC-8921-TH';
let currentPlanId = 'PLAN-7741';
let currentSensor = 'T-04';

const SENSOR_READINGS = {
  'Probe T-04': { temp: '8.2°C', num: 8.2, label: 'Core Reefer Probe T-04', drift: '+0.22°C/min', breach: true },
  'Air Return': { temp: '9.4°C', num: 9.4, label: 'Evaporator Air Return Loop', drift: '+0.31°C/min', breach: true },
  'Ambient': { temp: '24.5°C', num: 24.5, label: 'External Chassis Ambient Sensor', drift: '0.00°C/min', breach: false }
};

async function initIncidentWorkspace() {
  const params = new URLSearchParams(window.location.search);
  if (params.get('id')) {
    incidentId = params.get('id');
  }

  try {
    const data = await api.getIncident(incidentId);
    if (data.recovery_plans && data.recovery_plans.length > 0) {
      currentPlanId = data.recovery_plans[0].id;
      if (data.recovery_plans[0].status === 'APPROVED') {
        markPlanAsApproved(data.recovery_plans[0]);
      }
    }
  } catch (err) {
    console.warn('Backend sync warning:', err);
  }

  // Setup Sensor Tabs (Probe T-04, Air Return, Ambient)
  setupSensorTabs();

  // Find and setup buttons
  const authBtn = document.querySelector('button:has(kbd)');
  const simBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Simulate Excursion'));
  const compareBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Compare 3 Alternate Cold Hubs'));

  if (compareBtn) {
    compareBtn.onclick = () => { window.location.href = 'recovery.html'; };
  }

  if (simBtn) {
    simBtn.onclick = async () => {
      simBtn.disabled = true;
      simBtn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">sync</span><span>Analyzing Excursion...</span>';
      try {
        const spike = await api.simulateSpike(incidentId);
        showToast(`Thermal surge simulated: Probe T-04 jumped to ${spike.new_temp_c}°C (+0.35°C/min)`);
        
        SENSOR_READINGS['Probe T-04'].num = spike.new_temp_c;
        SENSOR_READINGS['Probe T-04'].temp = `${spike.new_temp_c}°C`;
        updateDisplayedTemp('Probe T-04');

        // Refresh AI reasoning with new spike
        api.analyzeIncident(incidentId).catch(console.warn);
      } catch (err) {
        console.error(err);
      } finally {
        simBtn.disabled = false;
        simBtn.innerHTML = '<span class="material-symbols-outlined text-[18px]">query_stats</span><span>Simulate Excursion</span>';
      }
    };
  }

  if (authBtn) {
    authBtn.onclick = async () => {
      authBtn.disabled = true;
      authBtn.innerHTML = `
        <span class="material-symbols-outlined text-[20px] animate-spin">sync</span>
        <span>Transmitting Diversion to Unit AC-2048...</span>
      `;
      try {
        const res = await api.approvePlan(currentPlanId, 'Sarah Jenkins', 'Lead Dispatcher');
        markPlanAsApproved({ approved_by: 'Sarah Jenkins', signature_hash: res.signature_hash });
        showToast('Autonomous Diversion Dispatched: Route instructions pushed to AC-2048 in-cab telematics.');
      } catch (err) {
        authBtn.disabled = false;
        authBtn.innerHTML = `
          <span class="material-symbols-outlined text-[20px] text-error">error</span>
          <span>Authorization Failed — Retry</span>
        `;
        console.error(err);
      }
    };

    // Keyboard Space shortcut
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        if (authBtn && !authBtn.disabled) {
          authBtn.click();
        }
      }
    });
  }
}

function setupSensorTabs() {
  const sensorBtns = Array.from(document.querySelectorAll('button')).filter(b => 
    b.textContent.trim() === 'Probe T-04' || 
    b.textContent.trim() === 'Air Return' || 
    b.textContent.trim() === 'Ambient'
  );

  sensorBtns.forEach(btn => {
    btn.onclick = () => {
      const name = btn.textContent.trim();
      sensorBtns.forEach(b => {
        b.className = 'px-3 py-1.5 rounded font-label-sm text-label-sm text-secondary hover:text-on-surface hover:bg-surface-container-high transition-colors';
      });
      btn.className = 'px-3 py-1.5 rounded bg-surface-container-lowest font-label-sm text-label-sm text-on-surface font-semibold shadow-sm';
      updateDisplayedTemp(name);
    };
  });
}

function updateDisplayedTemp(sensorName) {
  const data = SENSOR_READINGS[sensorName];
  if (!data) return;

  // Update big display reading
  const heroDisplay = document.querySelector('.font-display-hero');
  if (heroDisplay) {
    heroDisplay.textContent = data.num;
  }

  // Update sensor tag
  const subLabel = document.querySelector('span:contains("Probe T-04 Reefer Core"), span:contains("Core Sensor")');
  if (subLabel) {
    subLabel.textContent = data.label;
  }

  showToast(`Switched active telemetry readout to ${sensorName}: ${data.temp}`);
}

function markPlanAsApproved(plan) {
  const authBtn = document.querySelector('button:has(kbd)');
  if (authBtn) {
    authBtn.className = 'w-full py-3.5 px-4 bg-surface-container-high text-on-surface transition-all font-body-md text-body-md font-semibold rounded-lg flex items-center justify-center gap-2';
    authBtn.innerHTML = `
      <span class="material-symbols-outlined text-[20px] text-primary">check_circle</span>
      <span>Diversion Dispatched &amp; Locked (Bay 4)</span>
    `;
    authBtn.disabled = true;
  }

  // Update status badges across page
  document.querySelectorAll('span').forEach(sp => {
    if (sp.textContent.includes('BREACH') || sp.textContent.includes('CRITICAL BREACH')) {
      sp.textContent = 'MITIGATING - EN ROUTE (BAY 4)';
    }
  });
}

document.addEventListener('DOMContentLoaded', initIncidentWorkspace);
