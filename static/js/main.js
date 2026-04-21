// Main JavaScript for Room Booking System

document.addEventListener('DOMContentLoaded', function() {
    console.log('Room Booking System Initialized');

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.messages .card');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
