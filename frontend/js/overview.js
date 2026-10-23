// AeroCold Operations Overview Controller
import { api } from './api.js';

let currentPlanId = 'PLAN-7741';
let currentIncidentId = 'INC-8921-TH';

async function initOverview() {
  try {
    const data = await api.getDashboardOverview();
    updateKpis(data);
    loadRecentLogs();
  } catch (err) {
    console.warn('Backend sync warning:', err);
  }

  // Setup Authorize Diversion Button
  const authBtn = document.getElementById('authorize-btn');
  if (authBtn) {
    authBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      authBtn.disabled = true;
      authBtn.innerHTML = `
        <span class="material-symbols-outlined text-[18px] animate-spin">sync</span>
        <span>Transmitting Diversion Packet...</span>
      `;

      try {
        const res = await api.approvePlan(currentPlanId, 'Sarah Jenkins', 'Lead Dispatcher');
        authBtn.className = 'w-full py-3 px-4 rounded-lg bg-surface-container-high text-on-surface font-label-md text-label-md font-semibold flex items-center justify-center gap-2 transition-all';
        authBtn.innerHTML = `
          <span class="material-symbols-outlined text-[18px] text-primary">check_circle</span>
          <span>Diversion Transmitted (EDI 214 Dispatched)</span>
        `;
        showToast('Autonomous Diversion Authorized & Dispatched to Unit AC-2048');
        loadRecentLogs();
      } catch (err) {
        authBtn.disabled = false;
        authBtn.innerHTML = `
          <span class="material-symbols-outlined text-[18px] text-error">error</span>
          <span>Dispatch Failed — Retry</span>
        `;
        console.error(err);
      }
    });

    // Space key shortcut
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && e.target === document.body && authBtn && !authBtn.disabled) {
        e.preventDefault();
        authBtn.click();
      }
    });
  }

  // Setup Simulate Thermal Spike Button
  const simBtn = document.getElementById('toggle-sim-btn');
  if (simBtn) {
    simBtn.addEventListener('click', async () => {
      simBtn.disabled = true;
      try {
        const res = await api.simulateSpike(currentIncidentId);
        simBtn.classList.toggle('bg-primary');
        simBtn.classList.toggle('text-on-primary');
        simBtn.classList.toggle('text-on-surface');
        simBtn.querySelector('span:last-child').textContent = `Spike Active (+${res.new_temp_c}°C)`;

        // Update core temp on screen
        const tempDisplays = document.querySelectorAll('.font-display-hero');
        tempDisplays.forEach(el => el.textContent = res.new_temp_c);

        showToast(`Thermal surge simulated: Core temp is now ${res.new_temp_c}°C (+0.35°C/min)`);
        loadRecentLogs();
      } catch (err) {
        console.error(err);
      } finally {
        simBtn.disabled = false;
      }
    });
  }

  // Wire navigation buttons inside overview page
  document.querySelectorAll('a').forEach(a => {
    if (a.textContent.includes('Open Incident Workspace AC-2048')) {
      a.href = 'incident.html?id=INC-8921-TH';
    }
  });

  document.querySelectorAll('button').forEach(btn => {
    if (btn.textContent.includes('Compare 3 Alternate Cold Hubs') || btn.textContent.includes('Compare 3 Alternate')) {
      btn.onclick = () => { window.location.href = 'recovery.html'; };
    }
    if (btn.textContent.includes('Simulate Thermal Spike')) {
      btn.onclick = () => {
        if (simBtn) simBtn.click();
      };
    }
    if (btn.textContent.includes('Refresh Telemetry')) {
      btn.onclick = async () => {
        btn.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span><span>Syncing...</span>';
        await initOverview();
        setTimeout(() => {
          btn.innerHTML = '<span class="material-symbols-outlined text-[16px]">sync</span><span>Refresh Telemetry</span>';
        }, 500);
      };
    }
  });
}

function updateKpis(data) {
  if (data.recommended_plan) {
    currentPlanId = data.recommended_plan.id;
    if (data.recommended_plan.status === 'APPROVED') {
      const authBtn = document.getElementById('authorize-btn');
      if (authBtn) {
        authBtn.className = 'w-full py-3 px-4 rounded-lg bg-surface-container-high text-on-surface font-label-md text-label-md font-semibold flex items-center justify-center gap-2';
        authBtn.innerHTML = `
          <span class="material-symbols-outlined text-[18px] text-primary">check_circle</span>
          <span>Diversion Authorized & Locked (Bay 4)</span>
        `;
      }
    }
  }
}

async function loadRecentLogs() {
  try {
    const logs = await api.getActivityLogs(5);
    const ledgerContainer = document.querySelector('.flex.flex-col.gap-3.font-code-sm');
    if (ledgerContainer && logs.length > 0) {
      ledgerContainer.innerHTML = logs.map(l => {
        const timeStr = new Date(l.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        return `
          <div class="flex items-start gap-2.5 pb-2.5 bg-surface-bright p-2.5 rounded transition-all hover:bg-surface-container-low">
            <div class="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0"></div>
            <div class="flex flex-col">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-on-surface">${timeStr}</span>
                <span class="text-secondary">• ${l.event_type}</span>
              </div>
              <p class="text-secondary mt-0.5 leading-snug">${l.message}</p>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (err) {
    console.warn('Could not refresh activity logs:', err);
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
  }, 4000);
}

document.addEventListener('DOMContentLoaded', initOverview);
