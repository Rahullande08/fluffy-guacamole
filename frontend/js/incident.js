// AeroCold Incident Workspace Controller
import { api } from './api.js';

let incidentId = 'INC-8921-TH';
let currentPlanId = 'PLAN-7741';

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

  // Find buttons
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
        const analysis = await api.analyzeIncident(incidentId);
        showToast(`Spike simulated (+${spike.new_temp_c}°C). AI analysis updated.`);
        // Update temp readouts
        document.querySelectorAll('span, div').forEach(el => {
          if (el.textContent.trim() === '8.2' || el.textContent.trim() === '8.2°C') {
            el.textContent = `${spike.new_temp_c}°C`;
          }
        });
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
        showToast('Autonomous Diversion Dispatched: Route instructions pushed to AC-2048 telematics.');
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

  // Update status badge if present
  const badge = document.querySelector('.bg-primary.text-on-primary');
  if (badge && badge.textContent.includes('BREACH')) {
    badge.textContent = 'MITIGATING - DIVERTED';
  }
}

function showToast(msg) {
  let toast = document.getElementById('aerocold-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'aerocold-toast';
    toast.className = 'fixed bottom-6 right-6 z-50 bg-primary text-on-primary px-4 py-3 rounded-lg shadow-xl font-label-md text-label-md flex items-center gap-2 transition-all duration-300';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span class="material-symbols-outlined text-[18px]">verified</span><span>${msg}</span>`;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(16px)';
  }, 4500);
}

document.addEventListener('DOMContentLoaded', initIncidentWorkspace);
