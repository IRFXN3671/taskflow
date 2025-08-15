// Dashboard JavaScript functionality

// Auto-refresh functionality
let refreshInterval;

function refreshDashboard() {
    fetch('/api/dashboard-stats')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
            showRefreshIndicator();
        })
        .catch(error => {
            console.error('Error refreshing dashboard:', error);
        });
}

function updateDashboardStats(data) {
    document.getElementById('total-tasks').textContent = data.total_tasks;
    document.getElementById('pending-tasks').textContent = data.pending_tasks;
    document.getElementById('in-progress-tasks').textContent = data.in_progress_tasks;
    document.getElementById('completed-tasks').textContent = data.completed_tasks;
    document.getElementById('overdue-tasks').textContent = data.overdue_tasks;
}

function showRefreshIndicator() {
    // Create a subtle refresh indicator
    let indicator = document.getElementById('refresh-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'refresh-indicator';
        indicator.className = 'refresh-indicator position-fixed top-0 end-0 m-3 p-2 bg-success text-white rounded';
        indicator.innerHTML = '<i data-feather="refresh-cw"></i> Updated';
        document.body.appendChild(indicator);
        feather.replace();
    }
    
    indicator.classList.add('active');
    setTimeout(() => {
        indicator.classList.remove('active');
    }, 2000);
}

// Chart animations and interactions
function animateCounters() {
    const counters = document.querySelectorAll('.card-title');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        const increment = target / 20;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 50);
    });
}

// Initialize dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Animate counters on load
    animateCounters();
    
    // Set up auto-refresh
    refreshInterval = setInterval(refreshDashboard, 30000);
    
    // Add refresh button functionality
    const refreshButton = document.createElement('button');
    refreshButton.className = 'btn btn-outline-secondary btn-sm position-fixed bottom-0 end-0 m-3';
    refreshButton.innerHTML = '<i data-feather="refresh-cw"></i>';
    refreshButton.title = 'Refresh Dashboard';
    refreshButton.onclick = refreshDashboard;
    document.body.appendChild(refreshButton);
    feather.replace();
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
    });
});

// Chart color schemes
const chartColors = {
    primary: '#0d6efd',
    secondary: '#6c757d',
    success: '#198754',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
    light: '#f8f9fa',
    dark: '#212529'
};

// Utility function to format numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Utility function to format percentages
function formatPercentage(value, total) {
    if (total === 0) return '0%';
    return ((value / total) * 100).toFixed(1) + '%';
}

// Export functionality for charts
function exportChartAsPNG(chartId, filename) {
    const canvas = document.getElementById(chartId);
    const link = document.createElement('a');
    link.download = filename || 'chart.png';
    link.href = canvas.toDataURL();
    link.click();
}

// Responsive chart configurations
function getResponsiveChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: window.innerWidth < 768 ? 'bottom' : 'top'
            }
        }
    };
}

// Task status color mapping
function getStatusColor(status) {
    const colors = {
        'pending': chartColors.warning,
        'in_progress': chartColors.info,
        'completed': chartColors.success,
        'overdue': chartColors.danger
    };
    return colors[status] || chartColors.secondary;
}

// Priority color mapping
function getPriorityColor(priority) {
    const colors = {
        'low': chartColors.success,
        'medium': chartColors.warning,
        'high': chartColors.danger
    };
    return colors[priority] || chartColors.secondary;
}
