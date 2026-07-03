// Main JavaScript for Intelligent Student Risk Monitoring & Decision Support System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const sidebar = document.querySelector('.sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebar && sidebarToggle && !sidebar.contains(event.target) && !sidebarToggle.contains(event.target) && sidebar.classList.contains('toggled')) {
            document.body.classList.remove('sidebar-toggled');
            sidebar.classList.remove('toggled');
        }
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Date picker initialization (if using flatpickr or similar)
    // This would be implemented based on the actual date picker library used

    // Chart initialization would be handled in charts.js
    // This file focuses on general UI interactions and utilities

    // Notification handling
    const notificationContainer = document.getElementById('notificationContainer');
    if (notificationContainer) {
        // Auto-dismiss notifications after 5 seconds
        setTimeout(function() {
            const notifications = notificationContainer.querySelectorAll('.alert');
            notifications.forEach(function(notification) {
                const bsAlert = new bootstrap.Alert(notification);
                bsAlert.close();
            });
        }, 5000);
    }

    // Table sorting enhancement (if needed)
    // This could be enhanced with a library like DataTables

    // Responsive video embeds
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(function(iframe) {
        if (iframe.src.includes('youtube.com') || iframe.src.includes('vimeo.com')) {
            iframe.style.width = '100%';
            iframe.style.height = '400px';
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Back to top button functionality
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });

        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Initialize any charts that might be in the initial view
    // This would typically be done in charts.js, but we can call a function if needed
    if (typeof initCharts === 'function') {
        initCharts();
    }
});

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function getRiskBadgeClass(riskLevel) {
    switch (riskLevel.toLowerCase()) {
        case 'low':
            return 'badge bg-success';
        case 'medium':
            return 'badge bg-warning text-dark';
        case 'high':
            return 'badge bg-danger';
        default:
            return 'badge bg-secondary';
    }
}

function getRiskText(riskLevel) {
    switch (riskLevel.toLowerCase()) {
        case 'low':
            return 'Low Risk';
        case 'medium':
            return 'Medium Risk';
        case 'high':
            return 'High Risk';
        default:
            return 'Unknown';
    }
}

// AJAX helper function
function ajaxRequest(url, method = 'GET', data = null, successCallback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status >= 200 && xhr.status < 300) {
                if (successCallback) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        successCallback(response);
                    } catch (e) {
                        successCallback(xhr.responseText);
                    }
                }
            } else {
                if (errorCallback) {
                    errorCallback(xhr.status, xhr.responseText);
                }
            }
        }
    };
    
    xhr.send(data ? JSON.stringify(data) : null);
}

// Show loading spinner
function showLoading(spinnerId = 'loadingSpinner') {
    const spinner = document.getElementById(spinnerId);
    if (spinner) {
        spinner.style.display = 'flex';
    }
}

// Hide loading spinner
function hideLoading(spinnerId = 'loadingSpinner') {
    const spinner = document.getElementById(spinnerId);
    if (spinner) {
        spinner.style.display = 'none';
    }
}