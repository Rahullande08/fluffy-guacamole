// AeroCold Centralized API Client
const API_BASE_URL = window.location.origin.includes(':5173') || window.location.origin.includes(':3000')
  ? 'http://127.0.0.1:8000/api/v1'
  : '/api/v1';

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch('/health');
    return res.json();
  },

  // Dashboard
  getDashboardOverview: async () => {
    const res = await fetch(`${API_BASE_URL}/dashboard/overview`);
    if (!res.ok) throw new Error('Failed to fetch dashboard overview');
    return res.json();
  },

  // Fleet
  getFleet: async (status = '', cargo = '') => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (cargo) params.append('cargo', cargo);
    const res = await fetch(`${API_BASE_URL}/fleet?${params}`);
    if (!res.ok) throw new Error('Failed to fetch fleet');
    return res.json();
  },

  getVehicle: async (vehicleId) => {
    const res = await fetch(`${API_BASE_URL}/fleet/${vehicleId}`);
    if (!res.ok) throw new Error(`Failed to fetch vehicle ${vehicleId}`);
    return res.json();
  },

  getVehicleReadings: async (vehicleId, limit = 40) => {
    const res = await fetch(`${API_BASE_URL}/fleet/${vehicleId}/readings?limit=${limit}`);
    if (!res.ok) throw new Error(`Failed to fetch readings for ${vehicleId}`);
    return res.json();
  },

  // Incidents
  getIncidents: async () => {
    const res = await fetch(`${API_BASE_URL}/incidents`);
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  getIncident: async (incidentId) => {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}`);
    if (!res.ok) throw new Error(`Failed to fetch incident ${incidentId}`);
    return res.json();
  },

  analyzeIncident: async (incidentId, notes = '') => {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trigger_source: 'dispatcher_ui', notes })
    });
    if (!res.ok) throw new Error(`Failed to analyze incident ${incidentId}`);
    return res.json();
  },

  simulateSpike: async (incidentId) => {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/simulate-spike`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to simulate thermal spike');
    return res.json();
  },

  resetDemo: async (incidentId = 'INC-8921-TH') => {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/reset-demo`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to reset demo');
    return res.json();
  },

  // Recovery
  getFacilities: async () => {
    const res = await fetch(`${API_BASE_URL}/recovery/facilities`);
    if (!res.ok) throw new Error('Failed to fetch recovery facilities');
    return res.json();
  },

  getRecoveryPlans: async (incidentId) => {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/recovery-plans`);
    if (!res.ok) throw new Error('Failed to fetch recovery plans');
    return res.json();
  },

  approvePlan: async (planId, authorizedBy = 'Sarah Jenkins', role = 'Lead Dispatcher') => {
    const res = await fetch(`${API_BASE_URL}/recovery-plans/${planId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ authorized_by: authorizedBy, role })
    });
    if (!res.ok) throw new Error('Failed to approve recovery plan');
    return res.json();
  },

  rejectPlan: async (planId, reason = 'Operator override') => {
    const res = await fetch(`${API_BASE_URL}/recovery-plans/${planId}/reject?reason=${encodeURIComponent(reason)}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to reject plan');
    return res.json();
  },

  // Logs & Notifications
  getActivityLogs: async (limit = 20) => {
    const res = await fetch(`${API_BASE_URL}/activity-logs?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch activity logs');
    return res.json();
  },

  getNotifications: async () => {
    const res = await fetch(`${API_BASE_URL}/notifications`);
    if (!res.ok) throw new Error('Failed to fetch notifications');
    return res.json();
  },

  // Analytics & Settings
  getAnalytics: async () => {
    const res = await fetch(`${API_BASE_URL}/analytics/overview`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  getSettings: async () => {
    const res = await fetch(`${API_BASE_URL}/settings`);
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  }
};

window.aerocoldApi = api;
