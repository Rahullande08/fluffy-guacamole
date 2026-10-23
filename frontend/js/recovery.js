// AeroCold Recovery Planner Controller
import { api } from './api.js';

let currentPlanId = 'PLAN-7741';

async function initRecoveryPlanner() {
  try {
    const facilities = await api.getFacilities();
    // Check if plan already approved
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

  // Authorize diversion button
  const authBtn = document.getElementById('auth-diversion-btn');
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
}

function markDiversionDispatched() {
  const authBtn = document.getElementById('auth-diversion-btn');
  if (authBtn) {
    authBtn.innerHTML = `
      <span class="material-symbols-outlined text-[16px] text-on-primary">check_circle</span>
      <span>DIVERSION DISPATCHED TO TRUCK</span>
    `;
    authBtn.classList.remove('bg-primary');
    authBtn.classList.add('bg-secondary');
    authBtn.disabled = true;
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

document.addEventListener('DOMContentLoaded', initRecoveryPlanner);
