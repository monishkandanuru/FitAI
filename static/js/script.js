/**
 * FitAI Frontend Core Application Script
 * Handles system health checks, password toggles, flash alerts, Chart.js analytics, and goals checklist.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const healthDot = document.getElementById('health-dot');
    const healthText = document.getElementById('health-text');
    const btnCheckApi = document.getElementById('btn-check-api');
    const btnFetchHealth = document.getElementById('btn-fetch-health');
    const jsonContainer = document.getElementById('json-container');
    const jsonOutput = document.getElementById('json-output');
    const jsonCopyBtn = document.getElementById('json-copy-btn');
    const statLatency = document.getElementById('stat-latency');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navMenu = document.getElementById('nav-menu');

    /**
     * Poll system health status from Flask API
     */
    async function checkSystemHealth() {
        const startTime = performance.now();
        try {
            const response = await fetch('/health');
            const endTime = performance.now();
            const latency = Math.round(endTime - startTime);

            if (statLatency) {
                statLatency.textContent = `${latency}ms`;
            }

            if (response.ok) {
                const data = await response.json();
                if (healthDot && healthText) {
                    healthDot.classList.add('healthy');
                    healthText.textContent = `Online (${latency}ms)`;
                    healthText.style.color = '#10b981';
                }
                return data;
            } else {
                throw new Error(`Server returned ${response.status}`);
            }
        } catch (error) {
            console.error('FitAI Health Check Error:', error);
            if (healthDot && healthText) {
                healthDot.classList.remove('healthy');
                healthText.textContent = 'Offline / Error';
                healthText.style.color = '#ef4444';
            }
            return null;
        }
    }

    /**
     * Fetch and render JSON health response in audit box
     */
    async function toggleAndRenderJson() {
        if (!jsonContainer || !jsonOutput) return;

        if (jsonContainer.style.display === 'block') {
            jsonContainer.style.display = 'none';
            if (btnFetchHealth) btnFetchHealth.textContent = 'Fetch /health JSON';
            return;
        }

        if (btnFetchHealth) btnFetchHealth.textContent = 'Loading...';

        const data = await checkSystemHealth();

        if (data) {
            jsonOutput.textContent = JSON.stringify(data, null, 2);
            jsonContainer.style.display = 'block';
            if (btnFetchHealth) btnFetchHealth.textContent = 'Hide JSON Output';
        } else {
            jsonOutput.textContent = JSON.stringify({
                error: 'Could not connect to Flask backend endpoint',
                tip: 'Ensure python app.py is running'
            }, null, 2);
            jsonContainer.style.display = 'block';
            if (btnFetchHealth) btnFetchHealth.textContent = 'Hide Error Output';
        }
    }

    // Attach Event Listeners for API Tester
    if (btnCheckApi) {
        btnCheckApi.addEventListener('click', (e) => {
            e.preventDefault();
            const statusSection = document.getElementById('system-status');
            if (statusSection) {
                statusSection.scrollIntoView({ behavior: 'smooth' });
            }
            toggleAndRenderJson();
        });
    }

    if (btnFetchHealth) {
        btnFetchHealth.addEventListener('click', toggleAndRenderJson);
    }

    if (jsonCopyBtn && jsonOutput) {
        jsonCopyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(jsonOutput.textContent).then(() => {
                const originalText = jsonCopyBtn.textContent;
                jsonCopyBtn.textContent = 'Copied!';
                jsonCopyBtn.style.color = '#10b981';
                setTimeout(() => {
                    jsonCopyBtn.textContent = originalText;
                    jsonCopyBtn.style.color = '';
                }, 2000);
            });
        });
    }

    // Mobile menu toggle
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', () => {
            const isDisplayed = navMenu.style.display === 'flex';
            navMenu.style.display = isDisplayed ? 'none' : 'flex';
            if (!isDisplayed) {
                navMenu.style.flexDirection = 'column';
                navMenu.style.position = 'absolute';
                navMenu.style.top = '100%';
                navMenu.style.left = '0';
                navMenu.style.width = '100%';
                navMenu.style.background = 'rgba(9, 11, 17, 0.95)';
                navMenu.style.padding = '1.5rem';
                navMenu.style.borderBottom = '1px solid rgba(255, 255, 255, 0.1)';
            }
        });
    }

    /**
     * Show/Hide Password Visibility Toggle Logic
     */
    const passwordToggleBtns = document.querySelectorAll('.password-toggle-btn');
    passwordToggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);
            if (!targetInput) return;

            if (targetInput.type === 'password') {
                targetInput.type = 'text';
                btn.classList.add('visible');
                btn.innerHTML = `<svg class="eye-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
            } else {
                targetInput.type = 'password';
                btn.classList.remove('visible');
                btn.innerHTML = `<svg class="eye-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
            }
        });
    });

    /**
     * Registration Password Matching Real-Time Feedback
     */
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const matchErrorMsg = document.getElementById('password-match-error');

    function checkPasswordMatch() {
        if (!passwordInput || !confirmPasswordInput || !matchErrorMsg) return;

        if (confirmPasswordInput.value.length > 0 && passwordInput.value !== confirmPasswordInput.value) {
            matchErrorMsg.style.display = 'block';
            confirmPasswordInput.style.borderColor = '#f43f5e';
        } else {
            matchErrorMsg.style.display = 'none';
            confirmPasswordInput.style.borderColor = '';
        }
    }

    if (passwordInput && confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
        passwordInput.addEventListener('input', checkPasswordMatch);
    }

    /**
     * Flash Alert Dismissal Logic
     */
    const alertDismissBtns = document.querySelectorAll('.alert-dismiss-btn');
    alertDismissBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const alertElement = btn.closest('.flash-alert');
            if (alertElement) {
                alertElement.style.opacity = '0';
                alertElement.style.transform = 'translateY(-10px)';
                alertElement.style.transition = 'all 0.3s ease';
                setTimeout(() => alertElement.remove(), 300);
            }
        });
    });

    // Auto dismiss alerts after 6 seconds
    const flashAlerts = document.querySelectorAll('.flash-alert');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                alert.style.transition = 'all 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            }
        }, 6000);
    });

    /**
     * Chart.js Weekly Progress Chart Initialization
     */
    const chartCanvas = document.getElementById('weeklyProgressChart');
    if (chartCanvas && typeof Chart !== 'undefined') {
        const ctx = chartCanvas.getContext('2d');
        
        // Create Emerald Gradient Fill
        const emeraldGradient = ctx.createLinearGradient(0, 0, 0, 250);
        emeraldGradient.addColorStop(0, 'rgba(16, 185, 129, 0.4)');
        emeraldGradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

        // Create Cyan Gradient Fill
        const cyanGradient = ctx.createLinearGradient(0, 0, 0, 250);
        cyanGradient.addColorStop(0, 'rgba(6, 182, 212, 0.3)');
        cyanGradient.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [
                    {
                        label: 'Calories Burned (kcal)',
                        data: [1850, 2100, 1950, 2400, 2200, 2600, 2300],
                        borderColor: '#10b981',
                        backgroundColor: emeraldGradient,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#10b981',
                        pointBorderColor: '#ffffff',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Workout Time (min)',
                        data: [35, 45, 30, 60, 45, 75, 50],
                        borderColor: '#06b6d4',
                        backgroundColor: cyanGradient,
                        borderWidth: 2,
                        borderDash: [4, 4],
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#06b6d4',
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(11, 14, 23, 0.95)',
                        titleFont: { family: 'Outfit', size: 14 },
                        bodyFont: { family: 'Inter', size: 13 },
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: { color: '#9ca3af', font: { family: 'Inter', size: 12 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: { color: '#9ca3af', font: { family: 'Inter', size: 12 } }
                    }
                }
            }
        });
    }

    /**
     * Today's Goals Checklist Interactive Handler
     */
    const goalsChecklist = document.getElementById('goals-checklist');
    const goalsCompletedText = document.getElementById('goals-completed-text');
    const goalsPercentage = document.getElementById('goals-percentage');

    function updateGoalsProgress() {
        if (!goalsChecklist) return;
        const goalItems = goalsChecklist.querySelectorAll('.goal-item');
        let completedCount = 0;

        goalItems.forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox && checkbox.checked) {
                item.classList.add('completed');
                completedCount++;
            } else {
                item.classList.remove('completed');
            }
        });

        const total = goalItems.length;
        const percentage = total > 0 ? Math.round((completedCount / total) * 100) : 0;

        if (goalsCompletedText) {
            goalsCompletedText.textContent = `${completedCount} of ${total} Completed`;
        }

        if (goalsPercentage) {
            goalsPercentage.textContent = `${percentage}%`;
        }
    }

    if (goalsChecklist) {
        goalsChecklist.addEventListener('change', updateGoalsProgress);
        updateGoalsProgress();
    }

    // Run health check if health pill is present
    if (healthDot) {
        checkSystemHealth();
    }
});
