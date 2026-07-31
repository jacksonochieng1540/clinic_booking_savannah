// ========== DOCUMENT READY ==========
$(document).ready(function() {
    console.log('Clinic Booking System loaded!');
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add smooth transitions to cards
    $('.card').addClass('fade-in');
});

// ========== APPOINTMENT SLOT SELECTION ==========
function selectSlot(element) {
    // Remove selected class from all slots
    $('.slot-item').removeClass('selected');
    // Add selected class to clicked slot
    $(element).addClass('selected');
}

// ========== FORM VALIDATION ==========
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return true;
    
    var isValid = true;
    var inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// ========== DATE FORMATTING ==========
function formatDate(dateString) {
    if (!dateString) return '';
    var date = new Date(dateString);
    var options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
}

// ========== CONFIRMATION DIALOGS ==========
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ========== LOADING SPINNER ==========
function showLoading(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
        element.disabled = true;
    }
}

function hideLoading(elementId, originalText) {
    var element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// ========== API HELPERS ==========
const API_BASE = '/accounts/api/';

function apiRequest(endpoint, method, data) {
    return $.ajax({
        url: API_BASE + endpoint,
        method: method,
        contentType: 'application/json',
        data: data ? JSON.stringify(data) : null,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// ========== AVAILABILITY CHECK ==========
function checkAvailability(doctorId, date) {
    return $.ajax({
        url: `/schedules/api/doctors/${doctorId}/availability/?date=${date}`,
        method: 'GET'
    });
}

// ========== BOOK APPOINTMENT ==========
function bookAppointment(data) {
    return apiRequest('create/', 'POST', data);
}

// ========== CANCEL APPOINTMENT ==========
function cancelAppointment(id, reason) {
    return apiRequest(`${id}/cancel/`, 'PATCH', { reason: reason });
}

// ========== RESCHEDULE APPOINTMENT ==========
function rescheduleAppointment(id, newStartTime) {
    return apiRequest(`${id}/reschedule/`, 'PATCH', { new_start_time: newStartTime });
}

// ========== NOTIFICATION ==========
function showNotification(message, type) {
    var colors = {
        success: '#10B981',
        error: '#EF4444',
        warning: '#F59E0B',
        info: '#3B82F6'
    };
    
    // You can integrate with a toast library here
    alert(message);
}