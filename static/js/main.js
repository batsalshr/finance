/* =====================================================
   Personal Finance Tracker - Main JavaScript
   ===================================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    // =====================================================
    // Sidebar Toggle (Mobile)
    // =====================================================
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        // Create overlay element
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
        
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        });
        
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }
    
    // =====================================================
    // Auto-dismiss alerts after 5 seconds
    // =====================================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // =====================================================
    // Confirm delete dialogs
    // =====================================================
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
    
    // =====================================================
    // Format currency inputs
    // =====================================================
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
    
    // =====================================================
    // Set default date to today for date inputs
    // =====================================================
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });
    
    // =====================================================
    // Transaction type styling
    // =====================================================
    const transactionTypeSelect = document.getElementById('id_transaction_type');
    if (transactionTypeSelect) {
        transactionTypeSelect.addEventListener('change', function() {
            const amountInput = document.getElementById('id_amount');
            if (amountInput) {
                if (this.value === 'credit') {
                    amountInput.classList.remove('text-danger');
                    amountInput.classList.add('text-success');
                } else {
                    amountInput.classList.remove('text-success');
                    amountInput.classList.add('text-danger');
                }
            }
        });
    }
    
    // =====================================================
    // Search functionality
    // =====================================================
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Could implement live search here
            }, 300);
        });
    }
    
    // =====================================================
    // Tooltips initialization
    // =====================================================
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // =====================================================
    // Number formatting helper
    // =====================================================
    window.formatCurrency = function(amount, symbol = 'रू') {
        return symbol + parseFloat(amount).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    };
    
});
