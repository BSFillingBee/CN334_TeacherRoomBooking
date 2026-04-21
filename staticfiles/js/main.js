// Main JavaScript for Room Booking System

document.addEventListener('DOMContentLoaded', function() {
    console.log('Room Booking System Initialized');

    // Theme Toggle Logic
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    const updateToggleIcon = (theme) => {
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    };

    // Initial icon state
    updateToggleIcon(html.getAttribute('data-theme'));

    themeToggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateToggleIcon(newTheme);
        
        console.log(`Theme switched to: ${newTheme}`);
    });

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
