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

});
