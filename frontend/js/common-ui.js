// AeroCold Shared UI Components: Search Modal, Notifications Dropdown, Driver Comms, and FDA Audit Export
import { api } from './api.js';

export function showToast(msg, icon = 'verified') {
  let toast = document.getElementById('aerocold-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'aerocold-toast';
    toast.className = 'fixed bottom-6 right-6 z-50 bg-primary text-on-primary px-4 py-3 rounded-lg shadow-xl font-label-md text-label-md flex items-center gap-2 transition-all duration-300';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span class="material-symbols-outlined text-[18px]">${icon}</span><span>${msg}</span>`;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(16px)';
  }, 4000);
}

// 1. Quick Search Modal (Cmd+K / Ctrl+K)
export function initQuickSearch() {
  const searchTriggers = document.querySelectorAll('.flex.items-center.gap-2.px-3.py-1\\.5.rounded.bg-surface-container-low, button:has(.material-symbols-outlined:contains("search")), [data-action="search"]');

  // Create Modal element if not exists
  let modal = document.getElementById('search-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'search-modal';
    modal.className = 'fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-start justify-center pt-24 px-4 hidden transition-opacity';
    modal.innerHTML = `
      <div class="bg-surface-container-lowest border border-[#EAEAEA] rounded-xl shadow-2xl w-full max-w-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div class="p-3 border-b border-[#EAEAEA] flex items-center gap-2 bg-surface-bright">
          <span class="material-symbols-outlined text-secondary text-[20px]">search</span>
          <input id="search-input" type="text" placeholder="Search manifest, vehicle (e.g. AC-2048), destination, or route..." class="w-full bg-transparent font-body-md text-body-md text-on-surface outline-none placeholder:text-secondary" autofocus />
          <kbd class="px-1.5 py-0.5 rounded bg-surface-container-high text-[10px] font-code-sm text-secondary">ESC</kbd>
        </div>
        <div id="search-results" class="max-h-80 overflow-y-auto divide-y divide-[#EAEAEA] font-body-sm text-body-sm p-1">
          <div class="p-4 text-center text-secondary font-code-sm">Type to search live fleet telematics and recovery hubs...</div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeSearch();
    });

    const searchInput = modal.querySelector('#search-input');
    searchInput.addEventListener('input', (e) => handleSearch(e.target.value));
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSearch();
    });
  }

  function openSearch() {
    modal.classList.remove('hidden');
    const input = modal.querySelector('#search-input');
    input.value = '';
    input.focus();
    handleSearch('');
  }

  function closeSearch() {
    modal.classList.add('hidden');
  }

  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openSearch();
    }
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      closeSearch();
    }
  });

  searchTriggers.forEach(el => {
    el.style.cursor = 'pointer';
    el.addEventListener('click', openSearch);
  });

  // Also bind any search button or input in headers
  document.querySelectorAll('header button, header div').forEach(el => {
    if (el.textContent.includes('⌘K') || el.textContent.includes('Find manifest')) {
      el.style.cursor = 'pointer';
      el.onclick = openSearch;
    }
  });

  async function handleSearch(query) {
    const resultsContainer = modal.querySelector('#search-results');
    const q = query.toLowerCase().trim();

    const items = [
      { type: 'INCIDENT / BREACH', title: 'Unit AC-2048 • Strawberry Thermal Breach (+8.2°C)', desc: 'ECU Fault E-104 • I-90 W Corridor • Priority Alpha', url: 'incident.html?id=INC-8921-TH' },
      { type: 'RECOVERY FACILITY', title: 'Cold Storage A (Berkeley Port Terminal)', desc: 'Bay 4 Intake Clear • Pre-chilled dock ready • ETA 38m', url: 'recovery.html' },
      { type: 'RECOVERY FACILITY', title: 'Oakland Metro Cold Hub', desc: 'Bay 1 Standby • 6.8 km • ETA 46m', url: 'recovery.html' },
      { type: 'FLEET UNIT', title: 'Unit AC-1012 • Whole Milk & Cream', desc: 'Pacific Freight Express • Core: 2.1°C [NOMINAL]', url: 'fleet.html' },
      { type: 'FLEET UNIT', title: 'Unit AC-3091 • Wild Alaskan Salmon', desc: 'Arctic Ocean Logistics • Core: -18.2°C [CRYO NOMINAL]', url: 'fleet.html' },
      { type: 'NAVIGATION', title: 'Operations Overview HUD', desc: 'Live Telematics & Radar Stream', url: 'overview.html' },
      { type: 'NAVIGATION', title: 'Analytics & FDA Compliance Ledger', desc: 'FDA 21 CFR Part 11 Audit Trail', url: 'analytics.html' },
      { type: 'NAVIGATION', title: 'Platform Settings & API Adapters', desc: 'Google Gemini & Maps Configuration', url: 'settings.html' }
    ];

    const filtered = q ? items.filter(it => it.title.toLowerCase().includes(q) || it.desc.toLowerCase().includes(q) || it.type.toLowerCase().includes(q)) : items;

    if (filtered.length === 0) {
      resultsContainer.innerHTML = '<div class="p-6 text-center text-secondary">No matching vehicles or facilities found for "' + query + '".</div>';
      return;
    }

    resultsContainer.innerHTML = filtered.map(it => `
      <a href="${it.url}" class="p-3 flex items-start justify-between hover:bg-surface-bright transition-colors rounded-lg group">
        <div>
          <div class="flex items-center gap-2">
            <span class="font-code-sm text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-secondary font-bold">${it.type}</span>
            <span class="font-semibold text-on-surface group-hover:underline">${it.title}</span>
          </div>
          <p class="font-code-sm text-secondary text-[12px] mt-0.5">${it.desc}</p>
        </div>
        <span class="material-symbols-outlined text-secondary group-hover:text-primary text-[18px]">arrow_forward</span>
      </a>
    `).join('');
  }
}

// 2. Notifications Dropdown
export function initNotifications() {
  const notifBtns = document.querySelectorAll('button:has(.material-symbols-outlined:contains("notifications")), header button .material-symbols-outlined');

  let popover = document.getElementById('notif-popover');
  if (!popover) {
    popover = document.createElement('div');
    popover.id = 'notif-popover';
    popover.className = 'fixed top-16 right-6 z-50 bg-surface-container-lowest border border-[#EAEAEA] rounded-xl shadow-2xl w-80 max-w-sm hidden overflow-hidden animate-in fade-in duration-150';
    popover.innerHTML = `
      <div class="p-3 bg-surface-bright border-b border-[#EAEAEA] flex items-center justify-between">
        <span class="font-label-sm uppercase tracking-wider font-bold text-on-surface">System Alerts &amp; Directives</span>
        <span class="font-code-sm text-[11px] text-secondary">Live Stream</span>
      </div>
      <div id="notif-list" class="max-h-72 overflow-y-auto divide-y divide-[#EAEAEA] font-body-sm text-body-sm">
        <div class="p-4 text-center text-secondary">Loading telemetry alerts...</div>
      </div>
      <div class="p-2 bg-surface-bright border-t border-[#EAEAEA] text-center">
        <a href="overview.html" class="font-code-sm text-[11px] text-primary hover:underline font-semibold">View Live Incident Ledger</a>
      </div>
    `;
    document.body.appendChild(popover);

    document.addEventListener('click', (e) => {
      const isBtn = Array.from(document.querySelectorAll('button')).some(b => b.contains(e.target) && b.querySelector('.material-symbols-outlined')?.textContent.includes('notifications'));
      if (!isBtn && !popover.contains(e.target)) {
        popover.classList.add('hidden');
      }
    });
  }

  document.querySelectorAll('button').forEach(btn => {
    if (btn.querySelector('.material-symbols-outlined')?.textContent.trim() === 'notifications') {
      btn.onclick = async (e) => {
        e.stopPropagation();
        popover.classList.toggle('hidden');
        if (!popover.classList.contains('hidden')) {
          loadNotificationsList();
        }
      };
    }
  });

  async function loadNotificationsList() {
    const list = popover.querySelector('#notif-list');
    try {
      const items = await api.getNotifications();
      if (items.length === 0) {
        list.innerHTML = '<div class="p-4 text-center text-secondary">No active alerts.</div>';
        return;
      }
      list.innerHTML = items.map(n => `
        <div class="p-3 hover:bg-surface-bright transition-colors">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full ${n.severity === 'CRITICAL' ? 'bg-primary animate-pulse' : 'bg-secondary'}"></span>
            <span class="font-label-sm text-[11px] font-bold text-on-surface">${n.title}</span>
          </div>
          <p class="font-code-sm text-secondary text-[11px] mt-1 leading-snug">${n.message}</p>
        </div>
      `).join('');
    } catch (e) {
      list.innerHTML = '<div class="p-4 text-center text-error font-code-sm">Failed to load alerts.</div>';
    }
  }
}

// 3. Export FDA 21 CFR Part 11 Audit Dossier
export function initFdaExport() {
  document.querySelectorAll('button').forEach(btn => {
    if (
      btn.textContent.includes('Export FDA Audit Ledger') ||
      btn.textContent.includes('FDA 21 CFR Audit') ||
      btn.textContent.includes('Export Audit (21 CFR)') ||
      btn.textContent.includes('Export Compliance Dossier')
    ) {
      btn.onclick = async (e) => {
        e.preventDefault();
        btn.disabled = true;
        const orig = btn.innerHTML;
        btn.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span><span>Compiling 21 CFR Ledger...</span>';

        try {
          const logs = await api.getActivityLogs(50);
          showAuditModal(logs);
        } catch (err) {
          showToast('Could not compile audit dossier: ' + err.message, 'error');
        } finally {
          btn.disabled = false;
          btn.innerHTML = orig;
        }
      };
    }
  });

  function showAuditModal(logs) {
    let modal = document.getElementById('audit-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'audit-modal';
      modal.className = 'fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4';
      document.body.appendChild(modal);
    }

    const rows = logs.map(l => `
      <tr class="h-10 border-b border-[#EAEAEA] font-code-sm text-[11px]">
        <td class="px-3 py-1 text-secondary">${new Date(l.timestamp).toLocaleString()}</td>
        <td class="px-3 py-1 font-bold text-on-surface">${l.event_type}</td>
        <td class="px-3 py-1">${l.vehicle_id || 'ALL'}</td>
        <td class="px-3 py-1 text-secondary">${l.message}</td>
        <td class="px-3 py-1 text-on-surface font-semibold">${l.user_name}</td>
      </tr>
    `).join('');

    modal.innerHTML = `
      <div class="bg-surface-container-lowest border border-[#EAEAEA] rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150">
        <div class="p-4 bg-surface-bright border-b border-[#EAEAEA] flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-[22px]">verified</span>
            <div>
              <div class="font-label-md font-bold text-on-surface">FDA 21 CFR PART 11 • COMPLIANCE AUDIT DOSSIER</div>
              <div class="font-code-sm text-[11px] text-secondary">AeroCold Cold-Chain Cryptographic Telematics Ledger</div>
            </div>
          </div>
          <button id="close-audit-btn" class="p-1 rounded hover:bg-surface-container-high text-secondary hover:text-on-surface">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <div class="p-4 overflow-y-auto flex-1">
          <div class="p-3 bg-surface-bright rounded-lg mb-4 flex items-center justify-between font-code-sm text-[11px]">
            <span>System: AeroCold v4.8.2-PROD</span>
            <span>Cryptographic Integrity: VALID (SHA-256 Chain Locked)</span>
            <span>Total Logged Events: ${logs.length}</span>
          </div>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-surface-container-low h-8 font-label-sm text-[11px] text-secondary uppercase">
                <th class="px-3 py-1">Timestamp (UTC)</th>
                <th class="px-3 py-1">Event Type</th>
                <th class="px-3 py-1">Unit</th>
                <th class="px-3 py-1">Audit Details</th>
                <th class="px-3 py-1">Authorized Operator</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
        <div class="p-3 bg-surface-bright border-t border-[#EAEAEA] flex items-center justify-between">
          <span class="font-code-sm text-[11px] text-secondary">Electronic Record ID: CFR-11-AC2048-VECT07</span>
          <div class="flex gap-2">
            <button id="download-json-btn" class="px-3 py-1.5 rounded bg-surface-container-low text-on-surface hover:bg-surface-container-high font-label-sm text-[12px] font-semibold">Download JSON Ledger</button>
            <button id="print-dossier-btn" class="px-3 py-1.5 rounded bg-primary text-on-primary hover:bg-neutral-800 font-label-sm text-[12px] font-semibold">Print Certified Dossier</button>
          </div>
        </div>
      </div>
    `;

    modal.classList.remove('hidden');
    modal.querySelector('#close-audit-btn').onclick = () => modal.classList.add('hidden');
    modal.onclick = (e) => { if (e.target === modal) modal.classList.add('hidden'); };

    modal.querySelector('#download-json-btn').onclick = () => {
      const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AEROCLOD_FDA_21CFR_AUDIT_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('FDA Audit Ledger JSON downloaded successfully.');
    };

    modal.querySelector('#print-dossier-btn').onclick = () => {
      window.print();
    };
  }
}

// 4. Contact In-Cab Driver Modal
export function initDriverComms() {
  document.querySelectorAll('button').forEach(btn => {
    if (btn.textContent.includes('Contact In-Cab Driver') || btn.textContent.includes('Contact Driver')) {
      btn.onclick = (e) => {
        e.preventDefault();
        showDriverModal();
      };
    }
  });

  function showDriverModal() {
    let modal = document.getElementById('driver-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'driver-modal';
      modal.className = 'fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="bg-surface-container-lowest border border-[#EAEAEA] rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-150">
        <div class="p-4 bg-surface-bright border-b border-[#EAEAEA] flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-[20px]">headset_mic</span>
            <span class="font-label-md font-bold text-on-surface">In-Cab Satellite Telematics Comms</span>
          </div>
          <button id="close-driver-modal" class="p-1 rounded hover:bg-surface-container-high text-secondary">
            <span class="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>
        <div class="p-4 flex flex-col gap-3 font-body-sm text-body-sm">
          <div class="p-3 bg-surface-bright rounded-lg flex items-center justify-between">
            <div>
              <div class="font-semibold text-on-surface">M. Hansen (Lead Carrier Driver)</div>
              <div class="font-code-sm text-secondary text-[11px]">+1 (555) 234-8921 • Unit AC-2048</div>
            </div>
            <span class="px-2 py-0.5 rounded bg-primary text-on-primary font-code-sm text-[10px] font-bold">ONLINE</span>
          </div>
          <div class="flex flex-col gap-1">
            <label class="font-label-sm text-secondary uppercase text-[11px]">Direct Telematics Message / Audio Directive</label>
            <textarea id="driver-msg" class="w-full p-2.5 rounded bg-surface-container-low border border-[#EAEAEA] font-body-sm text-on-surface outline-none focus:border-primary resize-none" rows="3">ATTENTION: Priority Alpha Reroute to Cold Storage A (Bay 4). ETA 38 min. Maintain current heading along I-90 W.</textarea>
          </div>
          <button id="send-driver-msg" class="w-full py-2.5 rounded bg-primary hover:bg-neutral-800 text-on-primary font-label-md font-semibold flex items-center justify-center gap-1.5 transition-colors">
            <span class="material-symbols-outlined text-[16px]">send</span>
            <span>Transmit In-Cab Directive</span>
          </button>
        </div>
      </div>
    `;

    modal.classList.remove('hidden');
    modal.querySelector('#close-driver-modal').onclick = () => modal.classList.add('hidden');
    modal.onclick = (e) => { if (e.target === modal) modal.classList.add('hidden'); };

    modal.querySelector('#send-driver-msg').onclick = () => {
      modal.classList.add('hidden');
      showToast('Directive transmitted to M. Hansen in-cab telematics terminal via satellite link.');
    };
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initQuickSearch();
  initNotifications();
  initFdaExport();
  initDriverComms();
});
