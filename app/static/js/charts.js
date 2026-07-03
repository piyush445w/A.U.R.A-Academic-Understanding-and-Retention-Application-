// Chart.js visualizations for Intelligent Student Risk Monitoring & Decision Support System

// Global chart instances to prevent memory leaks
let chartInstances = {};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts that should load on page load
    initRiskDistributionChart();
    initAttendanceTrendsChart();
    initPerformanceChart();
});

// Function to destroy existing chart if it exists
function destroyChart(chartKey) {
    if (chartInstances[chartKey]) {
        chartInstances[chartKey].destroy();
        chartInstances[chartKey] = null;
    }
}

// Risk Distribution Chart (Pie/Doughnut)
function initRiskDistributionChart() {
    const ctx = document.getElementById('riskDistributionChart');
    if (!ctx) return;
    
    destroyChart('riskDistributionChart');
    
    // Sample data - in real implementation, this would come from AJAX or embedded data
    const riskData = {
        labels: ['Low Risk', 'Medium Risk', 'High Risk'],
        datasets: [{
            data: [65, 25, 10],
            backgroundColor: [
                '#28a745', // Success green
                '#ffc107', // Warning yellow
                '#dc3545'  // Danger red
            ],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };
    
    const riskOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = Math.round((value / total) * 100);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };
    
    chartInstances['riskDistributionChart'] = new Chart(ctx, {
        type: 'doughnut',
        data: riskData,
        options: riskOptions
    });
}

// Attendance Trends Chart (Line)
function initAttendanceTrendsChart() {
    const ctx = document.getElementById('attendanceTrendsChart');
    if (!ctx) return;
    
    destroyChart('attendanceTrendsChart');
    
    // Sample data for attendance trends over weeks
    const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'];
    const attendanceData = {
        labels: weeks,
        datasets: [{
            label: 'Average Attendance (%)',
            data: [85, 82, 78, 80, 75, 78],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            tension: 0.3,
            fill: true,
            borderWidth: 2,
            pointBackgroundColor: '#007bff',
            pointBorderColor: '#fff',
            pointBorderWidth: 2
        }]
    };
    
    const attendanceOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                    callback: function(value) {
                        return value + '%';
                    }
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.parsed.y + '%';
                    }
                }
            }
        }
    };
    
    chartInstances['attendanceTrendsChart'] = new Chart(ctx, {
        type: 'line',
        data: attendanceData,
        options: attendanceOptions
    });
}

// Performance Chart (Bar)
function initPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    destroyChart('performanceChart');
    
    // Sample data for subject-wise performance
    const subjects = ['Math', 'Physics', 'Chemistry', 'English', 'Computer Science'];
    const performanceData = {
        labels: subjects,
        datasets: [{
            label: 'Average Marks (%)',
            data: [78, 82, 75, 85, 90],
            backgroundColor: [
                'rgba(0, 123, 255, 0.5)',
                'rgba(40, 167, 69, 0.5)',
                'rgba(255, 193, 7, 0.5)',
                'rgba(23, 162, 184, 0.5)',
                'rgba(110, 66, 192, 0.5)'
            ],
            borderColor: [
                '#007bff',
                '#28a745',
                '#ffc107',
                '#17a2b8',
                '#6f42c1'
            ],
            borderWidth: 1
        }]
    };
    
    const performanceOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                    callback: function(value) {
                        return value + '%';
                    }
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.parsed.y + '%';
                    }
                }
            }
        }
    };
    
    chartInstances['performanceChart'] = new Chart(ctx, {
        type: 'bar',
        data: performanceData,
        options: performanceOptions
    });
}

// Function to update charts with new data (called via AJAX)
function updateRiskDistributionChart(data) {
    const ctx = document.getElementById('riskDistributionChart');
    if (!ctx || !chartInstances['riskDistributionChart']) return;
    
    chartInstances['riskDistributionChart'].data.labels = data.labels;
    chartInstances['riskDistributionChart'].data.datasets[0].data = data.values;
    chartInstances['riskDistributionChart'].update();
}

function updateAttendanceTrendsChart(data) {
    const ctx = document.getElementById('attendanceTrendsChart');
    if (!ctx || !chartInstances['attendanceTrendsChart']) return;
    
    chartInstances['attendanceTrendsChart'].data.labels = data.labels;
    chartInstances['attendanceTrendsChart'].data.datasets[0].data = data.values;
    chartInstances['attendanceTrendsChart'].update();
}

function updatePerformanceChart(data) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx || !chartInstances['performanceChart']) return;
    
    chartInstances['performanceChart'].data.labels = data.labels;
    chartInstances['performanceChart'].data.datasets[0].data = data.values;
    chartInstances['performanceChart'].update();
}

// Responsive chart resizing
window.addEventListener('resize', function() {
    // Debounce resize event
    if (window.resizeTimeout) {
        clearTimeout(window.resizeTimeout);
    }
    window.resizeTimeout = setTimeout(function() {
        Object.keys(chartInstances).forEach(function(key) {
            if (chartInstances[key]) {
                chartInstances[key].resize();
            }
        });
    }, 250);
});

// Export functions for use in other scripts
window.ChartUtils = {
    initRiskDistributionChart: initRiskDistributionChart,
    initAttendanceTrendsChart: initAttendanceTrendsChart,
    initPerformanceChart: initPerformanceChart,
    updateRiskDistributionChart: updateRiskDistributionChart,
    updateAttendanceTrendsChart: updateAttendanceTrendsChart,
    updatePerformanceChart: updatePerformanceChart,
    destroyChart: destroyChart
};