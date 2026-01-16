/**
 * Log Viewer - Frontend Application
 *
 * Provides filtering, searching, and display of unified logs from:
 * - orchestrator_chat: User/orchestrator/agent conversations
 * - agent_logs: Subagent hook events and response blocks
 * - system_logs: Orchestrator thinking blocks and tool use
 */

const API_BASE = '';

// State
let currentLogs = [];
let filterOptions = {};

// DOM Elements
const logBody = document.getElementById('log-body');
const sourceFilter = document.getElementById('source-filter');
const eventTypeFilter = document.getElementById('event-type-filter');
const levelFilter = document.getElementById('level-filter');
const senderFilter = document.getElementById('sender-filter');
const hoursFilter = document.getElementById('hours-filter');
const searchFilter = document.getElementById('search-filter');
const limitFilter = document.getElementById('limit-filter');
const refreshBtn = document.getElementById('refresh-btn');
const detailModal = document.getElementById('detail-modal');
const modalClose = document.getElementById('modal-close');
const modalBody = document.getElementById('modal-body');
const modalTitle = document.getElementById('modal-title');

// Stats elements
const statTotal = document.getElementById('stat-total');
const statAgent = document.getElementById('stat-agent');
const statSystem = document.getElementById('stat-system');
const statChat = document.getElementById('stat-chat');

/**
 * Fetch logs from API with current filters
 */
async function fetchLogs() {
    try {
        const params = new URLSearchParams();

        const limit = limitFilter.value || '100';
        params.append('limit', limit);

        if (sourceFilter.value) params.append('source', sourceFilter.value);
        if (eventTypeFilter.value) params.append('event_type', eventTypeFilter.value);
        if (levelFilter.value) params.append('level', levelFilter.value);
        if (senderFilter.value) params.append('sender_type', senderFilter.value);
        if (hoursFilter.value) params.append('hours', hoursFilter.value);
        if (searchFilter.value) params.append('search', searchFilter.value);

        const response = await fetch(`${API_BASE}/api/logs?${params}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        currentLogs = data.logs || [];
        renderLogs();

    } catch (error) {
        console.error('Error fetching logs:', error);
        logBody.innerHTML = `
            <tr class="error-row">
                <td colspan="6">Error loading logs: ${error.message}</td>
            </tr>
        `;
    }
}

/**
 * Fetch stats from API
 */
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE}/api/logs/stats`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        statTotal.textContent = formatNumber(data.total_count);
        statAgent.textContent = formatNumber(data.agent_logs_count);
        statSystem.textContent = formatNumber(data.system_logs_count);
        statChat.textContent = formatNumber(data.chat_count);

    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

/**
 * Fetch filter options from API
 */
async function fetchFilterOptions() {
    try {
        const response = await fetch(`${API_BASE}/api/logs/filter-options`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        filterOptions = await response.json();

        // Populate event type dropdown
        eventTypeFilter.innerHTML = '<option value="">All Types</option>';
        (filterOptions.event_types || []).forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            eventTypeFilter.appendChild(option);
        });

    } catch (error) {
        console.error('Error fetching filter options:', error);
    }
}

/**
 * Render logs to table
 */
function renderLogs() {
    if (currentLogs.length === 0) {
        logBody.innerHTML = `
            <tr class="empty-row">
                <td colspan="6">No logs found matching filters</td>
            </tr>
        `;
        return;
    }

    logBody.innerHTML = currentLogs.map((log, index) => {
        const timestamp = formatTimestamp(log.timestamp);
        const source = log.source || '-';
        const eventType = log.event_type || log.event_category || '-';
        const sender = formatSender(log);
        const message = truncateMessage(log.message || log.summary || '-', 200);

        return `
            <tr class="log-row source-${source}" data-index="${index}">
                <td class="col-timestamp">${timestamp}</td>
                <td class="col-source">
                    <span class="source-badge ${source}">${formatSource(source)}</span>
                </td>
                <td class="col-type">
                    <span class="type-badge">${eventType}</span>
                </td>
                <td class="col-sender">${sender}</td>
                <td class="col-message">${escapeHtml(message)}</td>
                <td class="col-actions">
                    <button class="btn btn-small" onclick="showDetails(${index})">View</button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Show log details in modal
 */
function showDetails(index) {
    const log = currentLogs[index];
    if (!log) return;

    modalTitle.textContent = `${formatSource(log.source)} - ${log.event_type || 'Details'}`;

    const details = [
        { label: 'ID', value: log.id },
        { label: 'Timestamp', value: log.timestamp },
        { label: 'Source', value: log.source },
        { label: 'Event Type', value: log.event_type },
        { label: 'Event Category', value: log.event_category },
        { label: 'Level', value: log.level },
        { label: 'Sender', value: log.sender_type },
        { label: 'Receiver', value: log.receiver_type },
        { label: 'Agent ID', value: log.agent_id },
        { label: 'Agent Name', value: log.agent_name },
        { label: 'Orchestrator Agent ID', value: log.orchestrator_agent_id },
    ].filter(d => d.value);

    let html = '<div class="detail-grid">';
    details.forEach(d => {
        html += `
            <div class="detail-item">
                <span class="detail-label">${d.label}:</span>
                <span class="detail-value">${escapeHtml(String(d.value))}</span>
            </div>
        `;
    });
    html += '</div>';

    // Message
    if (log.message) {
        html += `
            <div class="detail-section">
                <h3>Message</h3>
                <pre class="detail-content">${escapeHtml(log.message)}</pre>
            </div>
        `;
    }

    // Summary
    if (log.summary) {
        html += `
            <div class="detail-section">
                <h3>Summary</h3>
                <pre class="detail-content">${escapeHtml(log.summary)}</pre>
            </div>
        `;
    }

    // Metadata
    if (log.metadata && Object.keys(log.metadata).length > 0) {
        html += `
            <div class="detail-section">
                <h3>Metadata</h3>
                <pre class="detail-json">${escapeHtml(JSON.stringify(log.metadata, null, 2))}</pre>
            </div>
        `;
    }

    // Payload
    if (log.payload && Object.keys(log.payload).length > 0) {
        html += `
            <div class="detail-section">
                <h3>Payload</h3>
                <pre class="detail-json">${escapeHtml(JSON.stringify(log.payload, null, 2))}</pre>
            </div>
        `;
    }

    modalBody.innerHTML = html;
    detailModal.classList.add('open');
}

/**
 * Close modal
 */
function closeModal() {
    detailModal.classList.remove('open');
}

// Helper functions

function formatTimestamp(ts) {
    if (!ts) return '-';
    try {
        const date = new Date(ts);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    } catch {
        return ts;
    }
}

function formatSource(source) {
    const names = {
        'agent_logs': 'Agent',
        'system_logs': 'System',
        'orchestrator_chat': 'Chat'
    };
    return names[source] || source;
}

function formatSender(log) {
    if (log.sender_type && log.receiver_type) {
        const senderIcon = getSenderIcon(log.sender_type);
        const receiverIcon = getSenderIcon(log.receiver_type);
        return `${senderIcon} ${log.sender_type} → ${receiverIcon} ${log.receiver_type}`;
    }
    if (log.agent_name) {
        return `Agent: ${log.agent_name}`;
    }
    return '-';
}

function getSenderIcon(type) {
    const icons = {
        'user': '👤',
        'orchestrator': '🎯',
        'agent': '🤖'
    };
    return icons[type] || '';
}

function truncateMessage(msg, maxLen) {
    if (!msg) return '';
    if (msg.length <= maxLen) return msg;
    return msg.substring(0, maxLen) + '...';
}

function formatNumber(num) {
    if (typeof num !== 'number') return '-';
    return num.toLocaleString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Debounce helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Event listeners
refreshBtn.addEventListener('click', () => {
    fetchLogs();
    fetchStats();
});

sourceFilter.addEventListener('change', fetchLogs);
eventTypeFilter.addEventListener('change', fetchLogs);
levelFilter.addEventListener('change', fetchLogs);
senderFilter.addEventListener('change', fetchLogs);
hoursFilter.addEventListener('change', fetchLogs);
limitFilter.addEventListener('change', fetchLogs);
searchFilter.addEventListener('input', debounce(fetchLogs, 300));

modalClose.addEventListener('click', closeModal);
detailModal.addEventListener('click', (e) => {
    if (e.target === detailModal) closeModal();
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    fetchFilterOptions();
    fetchStats();
    fetchLogs();

    // Auto-refresh every 30 seconds
    setInterval(() => {
        fetchStats();
    }, 30000);
});
