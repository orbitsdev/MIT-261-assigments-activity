// Show loading indicator when form is submitted or page loads
document.addEventListener('DOMContentLoaded', function() {
  // Handle form submission
  const filterForm = document.getElementById('filterForm');
  if (filterForm) {
    filterForm.addEventListener('submit', function() {
      showLoading();
    });
    
    // Handle select changes
    const semesterSelect = document.getElementById('semester');
    const subjectSelect = document.getElementById('subject');
    
    if (semesterSelect) {
      semesterSelect.addEventListener('change', showLoading);
    }
    
    if (subjectSelect) {
      subjectSelect.addEventListener('change', showLoading);
    }
  }
  
  // Handle pagination links
  const paginationLinks = document.querySelectorAll('.pagination .page-link');
  paginationLinks.forEach(link => {
    if (!link.parentElement.classList.contains('disabled') && link.hasAttribute('href')) {
      link.addEventListener('click', showLoading);
    }
  });
});

function showLoading() {
  const loadingIndicator = document.getElementById('loading-indicator');
  const dataTable = document.getElementById('data-table');
  
  if (loadingIndicator) {
    loadingIndicator.style.display = 'block';
  }
  
  if (dataTable) {
    dataTable.style.display = 'none';
  }
}
