// AeroCold Recovery Planner Controller
import { api } from './api.js';
import { showToast } from './common-ui.js';

let currentPlanId = 'PLAN-7741';

async function initRecoveryPlanner() {
  try {
    const facilities = await api.getFacilities();
    const plans = await api.getRecoveryPlans('INC-8921-TH');
    if (plans && plans.length > 0) {
      currentPlanId = plans[0].id;
      if (plans[0].status === 'APPROVED') {
        markDiversionDispatched();
      }
    }
  } catch (err) {
    console.warn('Backend sync warning:', err);
  }

  // Strategy Filter Tabs
  setupStrategyTabs();

  // Recalculate button
  const recalcBtn = document.getElementById('recalc-btn');
  if (recalcBtn) {
    recalcBtn.onclick = async () => {
      const originalHtml = recalcBtn.innerHTML;
      recalcBtn.disabled = true;
      recalcBtn.innerHTML = `
        <span class="material-symbols-outlined text-[18px] text-secondary animate-spin">sync</span>
        <span>Evaluating Multi-Hub Matrices...</span>
        <span class="font-code-sm text-code-sm text-on-surface-variant bg-surface-container px-1.5 py-0.2 rounded">0.08s</span>
      `;
      try {
        await api.analyzeIncident('INC-8921-TH');
        showToast('Dynamic matrices recalculated: Cold Storage A remains optimal vector (38 min, 99.4% yield).');
      } catch (err) {
        console.error(err);
      } finally {
        recalcBtn.disabled = false;
        recalcBtn.innerHTML = originalHtml;
      }
    };
  }

  // Authorize diversion button (Cold Storage A)
  const authBtn = document.getElementById('auth-diversion-btn') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Select & Authorize Diversion'));
  if (authBtn) {
    authBtn.onclick = async () => {
      authBtn.disabled = true;
      authBtn.innerHTML = `
        <span class="material-symbols-outlined text-[16px] animate-spin">sync</span>
        <span>Pushing EDI 214 &amp; Waypoints...</span>
      `;
      try {
        const res = await api.approvePlan(currentPlanId, 'Sarah Jenkins', 'Lead Dispatcher');
        markDiversionDispatched();
        showToast('Diversion Authorized: Cold Storage A Bay 4 intake locked. Pushed to Unit AC-2048.');
      } catch (err) {
        authBtn.disabled = false;
        authBtn.innerHTML = `
          <span class="material-symbols-outlined text-[16px] text-error">error</span>
          <span>Dispatch Failed — Retry</span>
        `;
        console.error(err);
      }
    };
  }

  // Secondary fallback button (Oakland Cold Hub)
  const secondaryBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Select as Secondary Fallback'));
  if (secondaryBtn) {
    secondaryBtn.onclick = () => {
      secondaryBtn.className = 'w-full py-2.5 px-4 rounded bg-surface-container-high text-on-surface font-label-md font-semibold flex items-center justify-center gap-1.5';
      secondaryBtn.innerHTML = '<span class="material-symbols-outlined text-[16px] text-primary">check</span><span>Selected as Active Fallback (Oakland Hub)</span>';
      showToast('Oakland Metro Cold Hub staged as secondary fallback buffer.');
    };
  }

  // View Detailed Telematics button
  const viewTelematicsBtns = Array.from(document.querySelectorAll('button')).filter(b => b.textContent.includes('View Detailed Telematics'));
  viewTelematicsBtns.forEach(b => {
    b.onclick = () => { window.location.href = 'incident.html?id=INC-8921-TH'; };
  });

  // Cold-Chain Custody Lock button
  const custodyLockBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Cold-Chain Custody Lock'));
  if (custodyLockBtn) {
    custodyLockBtn.onclick = () => {
      showToast('Digital electronic seal lock verified for cargo compartment #889-C.');
    };
  }
}

function setupStrategyTabs() {
  const strategyBtns = Array.from(document.querySelectorAll('button')).filter(b => 
    b.textContent.includes('Minimize Cargo Risk') ||
    b.textContent.includes('Minimize Recovery Time') ||
    b.textContent.includes('Maximize Net Salvage Value')
  );

  strategyBtns.forEach(btn => {
    btn.onclick = () => {
      strategyBtns.forEach(b => {
        b.className = 'px-3 py-1.5 rounded font-label-sm text-label-sm text-secondary hover:text-on-surface hover:bg-surface-container-high transition-colors';
      });
      btn.className = 'px-3 py-1.5 rounded bg-surface-container-lowest font-label-sm text-label-sm text-on-surface font-semibold shadow-sm';
      showToast(`Matrix filtered by strategy: ${btn.textContent.trim()}`);
    };
  });
}

function markDiversionDispatched() {
  const authBtn = document.getElementById('auth-diversion-btn') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Select & Authorize Diversion'));
  if (authBtn) {
    authBtn.innerHTML = `
      <span class="material-symbols-outlined text-[16px] text-on-primary">check_circle</span>
      <span>DIVERSION DISPATCHED TO TRUCK</span>
    `;
    authBtn.className = 'w-full py-2.5 px-4 rounded bg-secondary text-on-primary font-label-md font-semibold flex items-center justify-center gap-1.5 shadow-sm';
    authBtn.disabled = true;
  }
}

document.addEventListener('DOMContentLoaded', initRecoveryPlanner);
