// API Base URL
const API_BASE = '/api/v1';

// Global state
let currentWeekId = null;
let currentProfile = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    try {
        initTabs();
        initWelcomeBanner();
        console.log('About to call loadStatus and loadProfile...');
        loadStatus();
        loadProfile();
        
        // Setup event listeners
        document.getElementById('profileForm').addEventListener('submit', handleProfileSubmit);
        document.getElementById('generatePlanBtn').addEventListener('click', handleGeneratePlan);
        document.getElementById('checkinForm').addEventListener('submit', handleCheckinSubmit);
        console.log('App initialization complete');
    } catch (error) {
        console.error('Error during app initialization:', error);
    }
});

// Welcome Banner Management
function initWelcomeBanner() {
    const getStartedBtn = document.getElementById('getStartedBtn');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', () => {
            hideWelcomeBanner();
            switchTab('setup');
        });
    }
    
    // Hide welcome banner if profile exists
    checkAndHideWelcomeBanner();
}

function hideWelcomeBanner() {
    const banner = document.getElementById('welcomeBanner');
    if (banner) {
        banner.classList.add('hidden');
        localStorage.setItem('welcomeBannerDismissed', 'true');
    }
}

async function checkAndHideWelcomeBanner() {
    // Check if banner was previously dismissed
    if (localStorage.getItem('welcomeBannerDismissed') === 'true') {
        hideWelcomeBanner();
        return;
    }
    
    // Check if profile exists
    try {
        const response = await fetch(`${API_BASE}/profile`);
        if (response.ok) {
            hideWelcomeBanner();
        }
    } catch (error) {
        console.log('Profile check failed, showing welcome banner');
    }
}

// Tab Management
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'status') {
        loadStatus();
    } else if (tabName === 'history') {
        loadHistory();
    } else if (tabName === 'plan') {
        loadLatestPlan();
    } else if (tabName === 'checkin') {
        loadWeekProgressForCheckin();
    } else if (tabName === 'setup') {
        loadProfile();
    }
}

// Profile Management
async function loadProfile() {
    console.log('loadProfile() called');
    try {
        console.log('Fetching profile from:', `${API_BASE}/profile`);
        const response = await fetch(`${API_BASE}/profile`);
        console.log('Profile response:', response.status);
        if (response.ok) {
            currentProfile = await response.json();
            console.log('Profile loaded:', currentProfile);
            displayProfileStatus('Profile loaded successfully', 'success');
            populateProfileForm(currentProfile);
        } else {
            displayProfileStatus('No profile found. Please create one.', 'warning');
        }
    } catch (error) {
        displayProfileStatus('Error loading profile', 'error');
        console.error('Error loading profile:', error);
    }
}

function populateProfileForm(profile) {
    const fields = {
        'objective': profile.objective.description,
        'duration': profile.objective.duration_weeks,
        'availableHours': profile.hard_constraints.available_hours_per_week,
        'fixedCommitments': profile.hard_constraints.fixed_commitments.join('\n'),
        'physicalConstraints': profile.hard_constraints.physical_constraints.join('\n'),
        'minFrequency': profile.non_negotiables.minimum_training_frequency,
        'restDays': profile.non_negotiables.rest_days.join(', '),
        'otherRules': profile.non_negotiables.other_rules.join('\n')
    };
    
    for (const [id, value] of Object.entries(fields)) {
        const element = document.getElementById(id);
        if (element) {
            element.value = value;
        } else {
            console.warn(`Element with id '${id}' not found`);
        }
    }
}

async function handleProfileSubmit(e) {
    e.preventDefault();
    
    const profileData = {
        objective_description: document.getElementById('objective').value,
        duration_weeks: parseInt(document.getElementById('duration').value),
        available_hours_per_week: parseFloat(document.getElementById('availableHours').value),
        fixed_commitments: parseLines(document.getElementById('fixedCommitments').value),
        physical_constraints: parseLines(document.getElementById('physicalConstraints').value),
        minimum_training_frequency: parseInt(document.getElementById('minFrequency').value),
        rest_days: document.getElementById('restDays').value.split(',').map(s => s.trim()),
        other_rules: parseLines(document.getElementById('otherRules').value)
    };
    
    try {
        const response = await fetch(`${API_BASE}/profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData)
        });
        
        if (response.ok) {
            currentProfile = await response.json();
            displayProfileStatus('Profile saved successfully!', 'success');
        } else {
            const error = await response.json();
            displayProfileStatus(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        displayProfileStatus('Error saving profile', 'error');
        console.error('Error saving profile:', error);
    }
}

function displayProfileStatus(message, type) {
    const statusBox = document.getElementById('profileStatus');
    statusBox.textContent = message;
    statusBox.className = `status-box ${type}`;
}

// Weekly Plan Management
async function loadLatestPlan() {
    const loading = document.getElementById('planLoading');
    const content = document.getElementById('planContent');
    
    loading.style.display = 'block';
    content.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/plans/latest`);
        
        if (response.ok) {
            const plan = await response.json();
            displayPlan(plan);
            currentWeekId = plan.week_id;
            document.getElementById('weekId').value = plan.week_id;
        } else if (response.status === 404) {
            content.innerHTML = `<div class="status-box warning">No plan generated yet. Click "Generate New Plan" to create your first weekly plan.</div>`;
        } else {
            content.innerHTML = `<div class="status-box error">Error loading plan</div>`;
        }
    } catch (error) {
        console.error('Error loading plan:', error);
        content.innerHTML = `<div class="status-box error">Error loading plan</div>`;
    } finally {
        loading.style.display = 'none';
    }
}

async function handleGeneratePlan() {
    const btn = document.getElementById('generatePlanBtn');
    const loading = document.getElementById('planLoading');
    const content = document.getElementById('planContent');
    
    const weekStartDate = document.getElementById('weekStartDate').value;
    
    btn.disabled = true;
    loading.style.display = 'block';
    content.innerHTML = '';
    
    try {
        const body = weekStartDate ? { week_start_date: weekStartDate } : {};
        
        const response = await fetch(`${API_BASE}/plans/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        if (response.ok) {
            const plan = await response.json();
            displayPlan(plan);
            currentWeekId = plan.week_id;
            document.getElementById('weekId').value = plan.week_id;
        } else {
            const error = await response.json();
            content.innerHTML = `<div class="status-box error">Error: ${error.detail}</div>`;
        }
    } catch (error) {
        content.innerHTML = `<div class="status-box error">Error generating plan: ${error.message}</div>`;
        console.error('Error generating plan:', error);
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

function displayPlan(plan) {
    const content = document.getElementById('planContent');
    
    const html = `
        <div class="plan-card">
            <h3>Week ${plan.week_id}</h3>
            <p><strong>Start Date:</strong> ${plan.start_date}</p>
            <p><strong>Version:</strong> ${plan.version}</p>
        </div>
        
        <div class="plan-card">
            <h3>🎯 Priorities (${plan.priorities.length})</h3>
            <ul class="priorities-list">
                ${plan.priorities.map(p => `<li>${p}</li>`).join('')}
            </ul>
        </div>
        
        ${plan.excluded.length > 0 ? `
        <div class="plan-card">
            <h3>❌ Explicitly Excluded</h3>
            <ul class="excluded-list">
                ${plan.excluded.map(e => `<li>${e}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
        
        <div class="plan-card">
            <h3>⚖️ Trade-Off Rationale</h3>
            <p>${plan.trade_off_rationale}</p>
        </div>
        
        ${plan.assumptions.length > 0 ? `
        <div class="plan-card">
            <h3>📋 Assumptions</h3>
            <ul>
                ${plan.assumptions.map(a => `<li>${a}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
        
        <div class="plan-card">
            <h3>📅 Daily Actions</h3>
            <p class="info-text">Click on any day to see the detailed training plan</p>
            <div class="daily-actions">
                ${plan.daily_actions.map((action, index) => `
                    <div class="day-card ${action.detailed_plan ? 'clickable' : ''}" onclick="showDetailedPlan(${index}, '${action.day}', ${JSON.stringify(action).replace(/"/g, '&quot;')})">
                        <h4>${action.day}</h4>
                        <div class="action">${action.action}</div>
                        <div class="time">⏱️ ${action.time_estimate_minutes} minutes</div>
                        ${action.detailed_plan ? '<div class="detail-indicator">👆 Click for details</div>' : ''}
                    </div>
                `).join('')}
            </div>
        </div>
        
        <!-- Modal for detailed plan -->
        <div id="detailModal" class="modal" onclick="closeDetailModal(event)">
            <div class="modal-content" onclick="event.stopPropagation()">
                <span class="close" onclick="closeDetailModal()">&times;</span>
                <div id="modalBody"></div>
            </div>
        </div>
    `;
    
    content.innerHTML = html;
}

// Reality Check Management
let currentPlanForCheck = null;

function getCurrentDayOfWeek() {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[new Date().getDay()];
}

function getDayStatus(dayName) {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const currentDay = getCurrentDayOfWeek();
    const currentIndex = days.indexOf(currentDay);
    const dayIndex = days.indexOf(dayName);
    
    if (dayIndex < currentIndex) return 'past';
    if (dayIndex === currentIndex) return 'today';
    return 'future';
}

async function loadWeekProgressForCheckin() {
    try {
        const response = await fetch(`${API_BASE}/plans/latest`);
        if (!response.ok) {
            document.getElementById('weekProgress').style.display = 'none';
            return;
        }
        
        currentPlanForCheck = await response.json();
        document.getElementById('weekId').value = currentPlanForCheck.week_id;
        
        const currentDay = getCurrentDayOfWeek();
        const progressDiv = document.getElementById('weekProgress');
        const indicatorP = progressDiv.querySelector('.current-day-indicator');
        const checkboxesDiv = document.getElementById('dailyCheckboxes');
        
        indicatorP.innerHTML = `Today is <strong>${currentDay}</strong>. Check off the actions you've completed:`;
        
        let checkboxesHTML = '';
        currentPlanForCheck.daily_actions.forEach((action, index) => {
            const status = getDayStatus(action.day);
            const statusClass = status === 'today' ? 'today' : status === 'past' ? 'past' : 'future';
            const isDisabled = status === 'future' ? 'disabled' : '';
            const checked = action.completed ? 'checked' : '';
            const actualNotes = action.actual_notes || '';
            
            checkboxesHTML += `
                <div class="day-checkbox-item ${status}-day">
                    <input type="checkbox" 
                           id="day-${index}" 
                           ${isDisabled} 
                           ${checked}
                           data-day="${action.day}"
                           data-index="${index}">
                    <div class="day-checkbox-content">
                        <div class="day-checkbox-header">
                            <span class="day-name">${action.day}</span>
                            <span class="day-status ${statusClass}">${status === 'today' ? 'Today' : status === 'past' ? 'Past' : 'Future'}</span>
                        </div>
                        <div class="day-action"><strong>Planned:</strong> ${action.action}</div>
                        <div class="day-time">${action.time_estimate_minutes} minutes</div>
                    </div>
                    <div class="day-actual-notes">
                        <label for="notes-${index}">What you actually did:</label>
                        <textarea 
                            id="notes-${index}" 
                            ${isDisabled}
                            placeholder="Describe what you actually did on ${action.day}..."
                            data-index="${index}">${actualNotes}</textarea>
                    </div>
                </div>
            `;
        });
        
        checkboxesDiv.innerHTML = checkboxesHTML;
        progressDiv.style.display = 'block';
    } catch (error) {
        console.error('Error loading week progress:', error);
        document.getElementById('weekProgress').style.display = 'none';
    }
}

async function handleCheckinSubmit(e) {
    e.preventDefault();
    
    if (!currentPlanForCheck) {
        alert('Please generate a plan first');
        return;
    }
    
    // Count completed actions from checkboxes
    const checkboxes = document.querySelectorAll('#dailyCheckboxes input[type="checkbox"]:not([disabled])');
    const completedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
    const plannedCount = checkboxes.length;
    
    // Collect actual execution notes
    const actualExecutionNotes = [];
    
    // Update completion status in current plan
    currentPlanForCheck.daily_actions.forEach((action, index) => {
        const checkbox = document.getElementById(`day-${index}`);
        const notesTextarea = document.getElementById(`notes-${index}`);
        
        if (checkbox && !checkbox.disabled) {
            action.completed = checkbox.checked;
            action.actual_notes = notesTextarea ? notesTextarea.value : '';
            
            // Collect notes for reality check analysis
            if (notesTextarea && notesTextarea.value.trim()) {
                actualExecutionNotes.push(`${action.day}: ${notesTextarea.value.trim()}`);
            }
        }
    });
    
    const checkinData = {
        week_id: currentPlanForCheck.week_id,
        sessions_completed: completedCount,
        sessions_planned: plannedCount,
        energy_level: document.getElementById('energyLevel').value,
        unexpected_events: parseLines(document.getElementById('unexpectedEvents').value),
        notes: actualExecutionNotes.length > 0 ? actualExecutionNotes.join('\n') : null
    };
    
    try {
        const response = await fetch(`${API_BASE}/reality-checks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(checkinData)
        });
        
        if (response.ok) {
            const report = await response.json();
            await displayDeviationReport(report);
            
            // If significant deviation, generate adapted plan
            if (report.deviation_detected || report.completion_rate < 0.7) {
                await generateAdaptedPlan(report);
            }
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert('Error submitting check-in');
        console.error('Error submitting check-in:', error);
    }
}

async function displayDeviationReport(report) {
    const reportBox = document.getElementById('deviationReport');
    
    const completionPct = (report.completion_rate * 100).toFixed(0);
    const confidencePct = (report.confidence_score * 100).toFixed(0);
    
    const html = `
        <h3>📊 Analysis Results</h3>
        <p><strong>Week:</strong> ${report.week_id}</p>
        <p><strong>Completion Rate:</strong> ${completionPct}%</p>
        <p><strong>Deviation Detected:</strong> ${report.deviation_detected ? '⚠️ Yes' : '✅ No'}</p>
        <p><strong>Confidence in Plan:</strong> ${confidencePct}%</p>
        <p><strong>Summary:</strong> ${report.deviation_summary}</p>
        <p><strong>Recommended Action:</strong> <strong>${report.recommended_action === 'adjust' ? '🔄 Adjust remaining days' : '✅ Stay the course'}</strong></p>
    `;
    
    reportBox.innerHTML = html;
    reportBox.style.display = 'block';
}

async function generateAdaptedPlan(report) {
    const adaptedBox = document.getElementById('adaptedPlan');
    adaptedBox.innerHTML = '<div class="loading">🔄 Adapting remaining days based on your progress...</div>';
    adaptedBox.style.display = 'block';
    
    try {
        // Get remaining days
        const currentDay = getCurrentDayOfWeek();
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const currentIndex = days.indexOf(currentDay);
        const remainingDays = currentPlanForCheck.daily_actions.filter((_, idx) => {
            const dayIndex = days.indexOf(currentPlanForCheck.daily_actions[idx].day);
            return dayIndex >= currentIndex;
        });
        
        if (remainingDays.length === 0) {
            adaptedBox.innerHTML = '<p>✅ Week is complete - no remaining days to adapt.</p>';
            return;
        }
        
        const adjustmentData = {
            week_id: currentPlanForCheck.week_id,
            reason: `Reality check shows ${(report.completion_rate * 100).toFixed(0)}% completion. ${report.deviation_summary}. Adapting remaining ${remainingDays.length} days.`,
            requested_changes: `Focus on ${remainingDays.length} remaining days starting from ${currentDay}. Current energy: ${document.getElementById('energyLevel').value}.`
        };
        
        const response = await fetch(`${API_BASE}/plans/adjust`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(adjustmentData)
        });
        
        if (response.ok) {
            const adaptedPlan = await response.json();
            displayAdaptedPlan(adaptedPlan, remainingDays);
        } else {
            adaptedBox.innerHTML = '<p>⚠️ Could not generate adapted plan. Try generating a fresh plan for next week.</p>';
        }
    } catch (error) {
        console.error('Error generating adapted plan:', error);
        adaptedBox.innerHTML = '<p>⚠️ Error adapting plan. The original plan remains active.</p>';
    }
}

function displayAdaptedPlan(plan, remainingDays) {
    const adaptedBox = document.getElementById('adaptedPlan');
    
    let daysHTML = '';
    plan.daily_actions.forEach(action => {
        daysHTML += `
            <div class="day-card">
                <strong>${action.day}:</strong> ${action.action}
                <div class="day-time">${action.time_estimate_minutes} min</div>
            </div>
        `;
    });
    
    const html = `
        <h3>✨ Adapted Plan for Remaining Days</h3>
        <p><strong>Focus:</strong> ${plan.priorities.join(', ')}</p>
        <p><strong>Why these changes:</strong> ${plan.trade_off_rationale}</p>
        <div class="daily-actions-grid">
            ${daysHTML}
        </div>
        <p style="margin-top: 1rem;"><em>This adapted plan is saved and will guide the rest of your week.</em></p>
    `;
    
    adaptedBox.innerHTML = html;
}

// Status Management
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        if (response.ok) {
            const status = await response.json();
            displayStatus(status);
            
            if (status.current_week_id) {
                currentWeekId = status.current_week_id;
                document.getElementById('weekId').value = status.current_week_id;
            }
        }
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

function displayStatus(status) {
    const content = document.getElementById('statusContent');
    
    const html = `
        <div class="status-box ${status.profile_exists ? 'success' : 'warning'}">
            <strong>Profile:</strong> ${status.profile_exists ? '✅ Configured' : '⚠️ Not configured'}
        </div>
        
        <div class="plan-card">
            <h3>Current Week</h3>
            <p><strong>Week ID:</strong> ${status.current_week_id}</p>
            <p><strong>Active Plan:</strong> ${status.active_plan ? '✅ Yes' : '❌ No'}</p>
        </div>
        
        ${status.active_plan ? displayPlan(status.active_plan) : ''}
        
        <div class="plan-card">
            <h3>📈 Statistics</h3>
            <ul>
                <li>Total Plans: ${status.statistics.total_plans}</li>
                <li>Reality Checks: ${status.statistics.total_reality_checks}</li>
                <li>Deviation Reports: ${status.statistics.total_deviation_reports}</li>
                <li>History Entries: ${status.statistics.total_history_entries}</li>
            </ul>
        </div>
    `;
    
    content.innerHTML = html;
}

// History Management
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/reality-checks/history?limit=10`);
        if (response.ok) {
            const history = await response.json();
            displayHistory(history);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(history) {
    const content = document.getElementById('historyContent');
    
    if (history.length === 0) {
        content.innerHTML = '<p>No history available yet.</p>';
        return;
    }
    
    const html = history.map(entry => {
        const completionRate = entry.final_completion_rate !== null 
            ? (entry.final_completion_rate * 100).toFixed(0)
            : 'N/A';
        
        const rateClass = completionRate >= 75 ? 'high' : completionRate >= 50 ? 'medium' : 'low';
        
        return `
            <div class="history-item">
                <div class="history-header">
                    <div>
                        <h3>${entry.week_id}</h3>
                        <p>${entry.plan.start_date}</p>
                    </div>
                    <div class="completion-rate ${completionRate !== 'N/A' ? rateClass : ''}">
                        ${completionRate}${completionRate !== 'N/A' ? '%' : ''}
                    </div>
                </div>
                
                <div>
                    <strong>Priorities:</strong>
                    <ul>
                        ${entry.plan.priorities.slice(0, 3).map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
                
                ${entry.deviation_report ? `
                    <div style="margin-top: 10px;">
                        <strong>Deviation:</strong> ${entry.deviation_report.deviation_detected ? '⚠️ Yes' : '✅ No'}
                        <br>
                        <strong>Summary:</strong> ${entry.deviation_report.deviation_summary}
                    </div>
                ` : ''}
                
                ${entry.adjustments.length > 0 ? `
                    <div style="margin-top: 10px;">
                        <strong>Adjustments:</strong> ${entry.adjustments.length} version(s)
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
    
    container.innerHTML = historyHTML;
}

// Modal functions for detailed plan
function showDetailedPlan(index, day, action) {
    const modal = document.getElementById('detailModal');
    const modalBody = document.getElementById('modalBody');
    
    if (!action.detailed_plan) return;
    
    const detailedPlanFormatted = action.detailed_plan.replace(/\n/g, '<br>');
    
    modalBody.innerHTML = `
        <h2>📋 ${day} - Detailed Plan</h2>
        <div class="detail-section">
            <h3>Overview</h3>
            <p><strong>${action.action}</strong></p>
            <p>⏱️ Estimated time: ${action.time_estimate_minutes} minutes</p>
        </div>
        <div class="detail-section">
            <h3>Step-by-Step Plan</h3>
            <div class="detailed-content">${detailedPlanFormatted}</div>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeDetailModal(event) {
    const modal = document.getElementById('detailModal');
    if (!event || event.target === modal || event.target.className === 'close') {
        modal.style.display = 'none';
    }
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeDetailModal();
    }
});

// Utility Functions
function parseLines(text) {
    return text.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
}
