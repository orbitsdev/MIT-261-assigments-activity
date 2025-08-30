/**
 * Enhanced loading indicator for MongoDB data fetching
 * This script handles showing/hiding the loading indicator during AJAX requests
 */
document.addEventListener('DOMContentLoaded', function() {
  // Cache DOM elements
  const loadingIndicator = document.getElementById('loading-indicator');
  const dataTable = document.getElementById('data-table');
  
  // Show loading indicator before form submission
  const filterForm = document.getElementById('filterForm');
  if (filterForm) {
    // Show loading on form submit
    filterForm.addEventListener('submit', function() {
      showLoading();
    });
    
    // Show loading when select elements change (which triggers form submission)
    const selectElements = filterForm.querySelectorAll('select');
    selectElements.forEach(select => {
      select.addEventListener('change', function() {
        showLoading();
      });
    });
  }
  
  // Show loading indicator before pagination links are clicked
  const paginationLinks = document.querySelectorAll('a[href*="page="]');
  paginationLinks.forEach(link => {
    if (!link.getAttribute('aria-disabled')) {
      link.addEventListener('click', function() {
        showLoading();
      });
    }
  });
  
  // Function to show loading indicator
  function showLoading() {
    if (loadingIndicator && dataTable) {
      dataTable.style.display = 'none';
      loadingIndicator.style.display = 'block';
    }
  }
  
  // Add global AJAX event listeners if using fetch or XMLHttpRequest
  const originalFetch = window.fetch;
  window.fetch = function() {
    showLoading();
    return originalFetch.apply(this, arguments)
      .finally(() => {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (dataTable) dataTable.style.display = 'block';
      });
  };
  
  // For XMLHttpRequest
  const originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function() {
    this.addEventListener('loadstart', () => showLoading());
    this.addEventListener('loadend', () => {
      if (loadingIndicator) loadingIndicator.style.display = 'none';
      if (dataTable) dataTable.style.display = 'block';
    });
    originalOpen.apply(this, arguments);
  };
});
