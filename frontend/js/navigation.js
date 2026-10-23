// AeroCold Unified Header Navigation & Breadcrumbs Handler
document.addEventListener('DOMContentLoaded', () => {
  const navMap = {
    'operations-overview': 'overview.html',
    'overview': 'overview.html',
    'live-fleet': 'fleet.html',
    'incidents': 'incident.html',
    'recovery-planner': 'recovery.html',
    'analytics': 'analytics.html',
    'settings': 'settings.html'
  };

  // Wire all navigation links
  document.querySelectorAll('a[data-path]').forEach(link => {
    const path = link.getAttribute('data-path');
    if (navMap[path]) {
      link.href = navMap[path];
    }
  });

  // Wire Logo/Brand to landing
  const brandLogo = document.querySelector('header span.uppercase');
  if (brandLogo && brandLogo.textContent.includes('AEROCOLD')) {
    brandLogo.style.cursor = 'pointer';
    brandLogo.onclick = () => { window.location.href = 'index.html'; };
  }
});
