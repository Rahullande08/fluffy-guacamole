// AeroCold Operations Overview Controller
import { api } from './api.js';
import { showToast } from './common-ui.js';

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

  // Setup Fleet Filter Buttons
  setupFleetFilters();

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
  const simBtns = [
    document.getElementById('toggle-sim-btn'),
    Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Simulate Thermal Spike'))
  ].filter(Boolean);

  simBtns.forEach(btn => {
    btn.onclick = async () => {
      btn.disabled = true;
      try {
        const res = await api.simulateSpike(currentIncidentId);
        btn.classList.toggle('bg-primary');
        btn.classList.toggle('text-on-primary');
        btn.classList.toggle('text-on-surface');
        const textSpan = btn.querySelector('span:last-child') || btn;
        textSpan.textContent = `Spike Active (+${res.new_temp_c}°C)`;

        // Update core temp readouts across screen
        document.querySelectorAll('.font-display-hero').forEach(el => el.textContent = res.new_temp_c);

        showToast(`Thermal surge simulated: Core temp is now ${res.new_temp_c}°C (+0.35°C/min)`);
        loadRecentLogs();
      } catch (err) {
        console.error(err);
      } finally {
        btn.disabled = false;
      }
    };
  });

  // Wire Map Elements (AC-2048 card & Cold Storage A card)
  const ac2048Card = document.querySelector('.absolute.left-\\[410px\\]');
  if (ac2048Card) {
    ac2048Card.style.cursor = 'pointer';
    ac2048Card.onclick = () => { window.location.href = 'incident.html?id=INC-8921-TH'; };
  }

  const coldStorageCard = document.querySelector('.absolute.right-6.top-8');
  if (coldStorageCard) {
    coldStorageCard.style.cursor = 'pointer';
    coldStorageCard.onclick = () => { window.location.href = 'recovery.html'; };
  }

  // Wire buttons inside overview
  document.querySelectorAll('a').forEach(a => {
    if (a.textContent.includes('Open Incident Workspace AC-2048')) {
      a.href = 'incident.html?id=INC-8921-TH';
    }
  });

  document.querySelectorAll('button').forEach(btn => {
    if (btn.textContent.includes('Compare 3 Alternate Cold Hubs') || btn.textContent.includes('Compare 3 Alternate')) {
      btn.onclick = () => { window.location.href = 'recovery.html'; };
    }
    if (btn.textContent.includes('Refresh Telemetry')) {
      btn.onclick = async () => {
        btn.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span><span>Syncing...</span>';
        await initOverview();
        setTimeout(() => {
          btn.innerHTML = '<span class="material-symbols-outlined text-[16px]">sync</span><span>Refresh Telemetry</span>';
          showToast('Telemetry synchronized across 48 units.');
        }, 500);
      };
    }
  });
}

function setupFleetFilters() {
  const filterBtns = Array.from(document.querySelectorAll('button')).filter(b => 
    b.textContent.trim() === 'ALL FLEETS' ||
    b.textContent.trim() === 'PERISHABLES' ||
    b.textContent.trim() === 'PHARMA' ||
    b.textContent.includes('HIGH RISK')
  );

  filterBtns.forEach(btn => {
    btn.onclick = () => {
      filterBtns.forEach(b => {
        b.className = 'px-2.5 py-1 rounded font-label-sm text-label-sm text-secondary hover:text-on-surface hover:bg-surface-container-high transition-colors';
      });
      btn.className = 'px-2.5 py-1 rounded bg-surface-container-lowest font-label-sm text-label-sm text-on-surface font-semibold shadow-[0_1px_2px_rgba(0,0,0,0.03)]';
      
      const filterName = btn.textContent.trim();
      if (filterName.includes('HIGH RISK')) {
        showToast('Filtering for active critical breach: Unit AC-2048');
      } else {
        showToast(`Fleet filtered by category: ${filterName}`);
      }
    };
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

document.addEventListener('DOMContentLoaded', initOverview);
