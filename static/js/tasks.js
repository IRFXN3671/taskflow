// Tasks page JavaScript functionality

// Auto-refresh for tasks list
let tasksRefreshInterval;

function refreshTasksList() {
    // Get current URL with all filters
    const currentUrl = window.location.href;
    
    fetch(currentUrl, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Parse the response and update only the table
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTable = doc.querySelector('.table-responsive');
        const currentTable = document.querySelector('.table-responsive');
        
        if (newTable && currentTable) {
            currentTable.innerHTML = newTable.innerHTML;
            feather.replace();
            showRefreshIndicator();
        }
    })
    .catch(error => {
        console.error('Error refreshing tasks:', error);
    });
}

function showRefreshIndicator() {
    let indicator = document.getElementById('tasks-refresh-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'tasks-refresh-indicator';
        indicator.className = 'refresh-indicator position-fixed top-0 end-0 m-3 p-2 bg-info text-white rounded';
        indicator.innerHTML = '<i data-feather="refresh-cw"></i> Tasks Updated';
        document.body.appendChild(indicator);
        feather.replace();
    }
    
    indicator.classList.add('active');
    setTimeout(() => {
        indicator.classList.remove('active');
    }, 1500);
}

// Filter management
function clearAllFilters() {
    const form = document.querySelector('form');
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type === 'text' || input.type === 'search') {
            input.value = '';
        } else if (input.tagName === 'SELECT') {
            input.selectedIndex = 0;
        }
    });
    form.submit();
}

// Quick filter buttons
function createQuickFilters() {
    const filterContainer = document.querySelector('.card-body');
    if (!filterContainer) return;
    
    const quickFiltersDiv = document.createElement('div');
    quickFiltersDiv.className = 'mb-3';
    quickFiltersDiv.innerHTML = `
        <div class="d-flex flex-wrap gap-2">
            <span class="text-muted me-2">Quick filters:</span>
            <button class="btn btn-outline-warning btn-sm" onclick="filterByStatus('pending')">
                <i data-feather="clock"></i> Pending
            </button>
            <button class="btn btn-outline-info btn-sm" onclick="filterByStatus('in_progress')">
                <i data-feather="play-circle"></i> In Progress
            </button>
            <button class="btn btn-outline-success btn-sm" onclick="filterByStatus('completed')">
                <i data-feather="check-circle"></i> Completed
            </button>
            <button class="btn btn-outline-danger btn-sm" onclick="filterByPriority('high')">
                <i data-feather="alert-circle"></i> High Priority
            </button>
            <button class="btn btn-outline-warning btn-sm" onclick="filterOverdue()">
                <i data-feather="alert-triangle"></i> Overdue
            </button>
        </div>
    `;
    
    filterContainer.insertBefore(quickFiltersDiv, filterContainer.firstChild);
    feather.replace();
}

function filterByStatus(status) {
    document.getElementById('status').value = status;
    document.querySelector('form').submit();
}

function filterByPriority(priority) {
    document.getElementById('priority').value = priority;
    document.querySelector('form').submit();
}

function filterOverdue() {
    // This would require backend support to filter overdue tasks
    // For now, we'll sort by due date and show pending/in_progress
    document.getElementById('status').value = '';
    document.getElementById('sort').value = 'due_date';
    document.getElementById('order').value = 'asc';
    document.querySelector('form').submit();
}

// Task row interactions
function initializeTaskRows() {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        // Add click handler to expand/collapse task details
        row.addEventListener('click', function(e) {
            if (e.target.closest('.btn-group')) return; // Ignore button clicks
            
            const detailsRow = row.nextElementSibling;
            if (detailsRow && detailsRow.classList.contains('task-details')) {
                detailsRow.style.display = detailsRow.style.display === 'none' ? '' : 'none';
            }
        });
        
        // Add hover effects
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'var(--bs-secondary-bg)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

// Bulk actions
function initializeBulkActions() {
    const tableContainer = document.querySelector('.table-responsive');
    if (!tableContainer) return;
    
    const bulkActionsDiv = document.createElement('div');
    bulkActionsDiv.className = 'mb-3 d-none';
    bulkActionsDiv.id = 'bulk-actions';
    bulkActionsDiv.innerHTML = `
        <div class="alert alert-info">
            <span id="selected-count">0</span> tasks selected
            <div class="btn-group ms-3">
                <button class="btn btn-sm btn-outline-primary" onclick="bulkUpdateStatus('in_progress')">
                    Mark as In Progress
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="bulkUpdateStatus('completed')">
                    Mark as Completed
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="bulkDelete()">
                    Delete Selected
                </button>
            </div>
        </div>
    `;
    
    tableContainer.insertBefore(bulkActionsDiv, tableContainer.firstChild);
}

// Search functionality enhancements
function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            // Auto-submit search after 500ms of no typing
            if (this.value.length >= 3 || this.value.length === 0) {
                this.form.submit();
            }
        }, 500);
    });
    
    // Add search suggestions
    const suggestions = ['bug', 'feature', 'urgent', 'client', 'testing', 'documentation'];
    const datalist = document.createElement('datalist');
    datalist.id = 'search-suggestions';
    suggestions.forEach(suggestion => {
        const option = document.createElement('option');
        option.value = suggestion;
        datalist.appendChild(option);
    });
    searchInput.setAttribute('list', 'search-suggestions');
    searchInput.parentNode.appendChild(datalist);
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + F: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Ctrl/Cmd + N: New task (if manager)
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            const createButton = document.querySelector('a[href*="create_task"]');
            if (createButton) {
                e.preventDefault();
                window.location.href = createButton.href;
            }
        }
        
        // R: Refresh
        if (e.key === 'r' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                refreshTasksList();
            }
        }
    });
}

// Export functionality
function exportTasksToCSV() {
    const table = document.querySelector('.table');
    if (!table) return;
    
    const rows = Array.from(table.rows);
    const csvContent = rows.map(row => {
        const cells = Array.from(row.cells);
        return cells.map(cell => {
            const text = cell.textContent.trim().replace(/\s+/g, ' ');
            return `"${text.replace(/"/g, '""')}"`;
        }).join(',');
    }).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `tasks_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize all functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create quick filters
    createQuickFilters();
    
    // Initialize task row interactions
    initializeTaskRows();
    
    // Initialize bulk actions
    initializeBulkActions();
    
    // Initialize search enhancements
    initializeSearch();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Set up auto-refresh
    tasksRefreshInterval = setInterval(refreshTasksList, 30000);
    
    // Add export button
    const titleDiv = document.querySelector('h1').parentNode;
    const exportButton = document.createElement('button');
    exportButton.className = 'btn btn-outline-secondary btn-sm ms-2';
    exportButton.innerHTML = '<i data-feather="download"></i> Export CSV';
    exportButton.onclick = exportTasksToCSV;
    titleDiv.appendChild(exportButton);
    feather.replace();
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        if (tasksRefreshInterval) {
            clearInterval(tasksRefreshInterval);
        }
    });
});

// Form validation for task operations
function validateTaskForm(form) {
    const title = form.querySelector('input[name="title"]');
    const assignee = form.querySelector('select[name="assignee_id"]');
    
    let isValid = true;
    
    // Clear previous validation states
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
    
    // Validate title
    if (!title.value.trim()) {
        showFieldError(title, 'Task title is required');
        isValid = false;
    } else if (title.value.trim().length < 3) {
        showFieldError(title, 'Task title must be at least 3 characters');
        isValid = false;
    }
    
    // Validate assignee (for create form)
    if (assignee && !assignee.value) {
        showFieldError(assignee, 'Please select an assignee');
        isValid = false;
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    field.parentNode.appendChild(feedback);
}

// Progress tracking
function updateTaskProgress() {
    const progressBars = document.querySelectorAll('.task-progress');
    progressBars.forEach(bar => {
        const current = parseInt(bar.dataset.current);
        const total = parseInt(bar.dataset.total);
        const percentage = total > 0 ? (current / total) * 100 : 0;
        
        bar.style.width = percentage + '%';
        bar.setAttribute('aria-valuenow', current);
        bar.textContent = `${current}/${total}`;
    });
}
