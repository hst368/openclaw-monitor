/**
 * OpenClaw Monitor - Dashboard JavaScript
 */

// 全局状态
let currentTab = 'overview';
let autoRefreshInterval = null;
let usageChart = null;
let currentCurrency = 'CNY';
let pricingData = {};

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initTabs();
    initEventListeners();
    loadAllData();
    startAutoRefresh();
});

// ========== 主题切换 ==========
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.className = savedTheme;
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const isDark = document.body.classList.contains('dark');
    const newTheme = isDark ? 'light' : 'dark';
    document.body.className = newTheme;
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('theme-toggle');
    btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    btn.title = theme === 'dark' ? '切换亮色' : '切换暗色';
}

// ========== 标签页切换 ==========
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // 更新按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
    
    // 更新内容显示
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabId}`);
    });
    
    currentTab = tabId;
    
    // 根据标签页加载特定数据
    if (tabId === 'pricing') {
        loadPricingData();
    } else if (tabId === 'tasks') {
        loadTasksData();
    } else if (tabId === 'logs') {
        loadLogsData();
    }
}

// ========== 事件监听 ==========
function initEventListeners() {
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    document.getElementById('refresh-btn').addEventListener('click', () => {
        loadAllData();
        showToast('数据已刷新', 'success');
    });
    
    // 定价页面事件
    document.getElementById('add-model-btn').addEventListener('click', () => openPricingModal());
    document.getElementById('reset-pricing-btn').addEventListener('click', resetPricing);
    document.getElementById('save-pricing').addEventListener('click', savePricing);
    document.getElementById('cancel-edit').addEventListener('click', closePricingModal);
    document.getElementById('close-modal').addEventListener('click', closePricingModal);
    
    // 货币设置
    document.getElementById('display-currency').addEventListener('change', (e) => {
        setDisplayCurrency(e.target.value);
    });
    document.getElementById('update-rate-btn').addEventListener('click', updateExchangeRate);
    document.getElementById('auto-rate-btn').addEventListener('click', () => updateExchangeRate(true));
    
    // 日志筛选
    document.getElementById('log-days').addEventListener('change', loadLogsData);
}

// ========== 数据加载 ==========
async function loadAllData() {
    await Promise.all([
        loadSummaryData(),
        loadSystemData(),
        loadVersionData(),
        loadTokenUsageData()
    ]);
}

async function loadSummaryData() {
    try {
        const resp = await fetch('/api/summary');
        const data = await resp.json();
        
        if (data.error) {
            console.error('加载数据失败:', data.error);
            return;
        }
        
        // 更新 Gateway 状态
        const gatewayStatus = document.getElementById('gateway-status');
        if (data.gateway) {
            const online = data.gateway.online;
            gatewayStatus.textContent = online ? '🟢 在线' : '🔴 离线';
            gatewayStatus.className = online ? 'card-value online' : 'card-value offline';
            
            const uptime = formatDuration(data.gateway.uptime_seconds);
            document.getElementById('gateway-version').textContent = 
                `运行: ${uptime}`;
        }
        
        // 更新任务数
        if (data.tasks) {
            document.getElementById('running-tasks').textContent = data.tasks.running || 0;
            document.getElementById('completed-tasks').textContent = 
                data.tasks.completed_24h || 0;
        }
        
        // 更新 Token 统计
        if (data.token_usage) {
            const today = data.token_usage.today || {};
            const week = data.token_usage.week || {};
            
            document.getElementById('today-tokens').textContent = 
                formatTokens(today.total || 0);
            document.getElementById('week-tokens').textContent = 
                formatTokens(week.total || 0);
        }
        
        // 更新成本统计（需要定价数据）
        updateCostDisplay(data.token_usage);
        
        // 更新会话统计
        document.getElementById('total-sessions').textContent = 
            data.token_usage?.total_sessions || '-';
        document.getElementById('last-active').textContent = 
            data.gateway?.online ? '刚刚' : '未知';
        
    } catch (e) {
        console.error('加载摘要数据失败:', e);
    }
}

async function loadSystemData() {
    try {
        const resp = await fetch('/api/system');
        const data = await resp.json();
        
        if (data.error) return;
        
        document.getElementById('hostname').textContent = data.hostname || '-';
        document.getElementById('os-info').textContent = 
            `${data.os || '-'} ${data.architecture || ''}`;
        document.getElementById('ip-address').textContent = data.ip || '-';
        
        // CPU
        const cpuPercent = data.cpu?.percent || 0;
        document.getElementById('cpu-info').textContent = 
            `${data.cpu?.count || '-'}核 (${cpuPercent}%)`;
        document.getElementById('cpu-bar').style.width = `${cpuPercent}%`;
        
        // 内存
        const memPercent = data.memory?.percent || 0;
        document.getElementById('memory-info').textContent = 
            `${data.memory?.available_gb || '-'}GB / ${data.memory?.total_gb || '-'}GB`;
        document.getElementById('memory-bar').style.width = `${memPercent}%`;
        
        // 磁盘
        const diskPercent = ((data.disk?.total_gb - data.disk?.free_gb) / data.disk?.total_gb * 100) || 0;
        document.getElementById('disk-info').textContent = 
            `${data.disk?.free_gb || '-'}GB / ${data.disk?.total_gb || '-'}GB 可用`;
        document.getElementById('disk-bar').style.width = `${diskPercent}%`;
        
    } catch (e) {
        console.error('加载系统数据失败:', e);
    }
}

async function loadVersionData() {
    try {
        const resp = await fetch('/api/version');
        const data = await resp.json();
        
        if (data.openclaw) {
            document.getElementById('oc-version').textContent = 
                data.openclaw.current || '-';
            document.getElementById('latest-version').textContent = 
                data.openclaw.latest || '-';
            
            const badge = document.getElementById('update-badge');
            if (data.openclaw.update_available) {
                badge.textContent = `有更新: ${data.openclaw.latest}`;
                badge.className = 'badge warning';
            } else {
                badge.textContent = '已是最新';
                badge.className = 'badge success';
            }
        }
        
    } catch (e) {
        console.error('加载版本数据失败:', e);
    }
}

async function loadTokenUsageData() {
    try {
        const resp = await fetch('/api/token-usage?days=7');
        const data = await resp.json();
        
        // 渲染图表
        renderUsageChart(data.daily || []);
        
    } catch (e) {
        console.error('加载 Token 使用数据失败:', e);
    }
}

async function loadTasksData() {
    try {
        const resp = await fetch('/api/tasks');
        const data = await resp.json();
        
        document.getElementById('task-running-count').textContent = data.running || 0;
        document.getElementById('task-completed-count').textContent = data.completed_24h || 0;
        
        const taskList = document.getElementById('task-list');
        
        if (!data.tasks || data.tasks.length === 0) {
            taskList.innerHTML = '<div class="empty-state">暂无运行中的任务</div>';
            return;
        }
        
        taskList.innerHTML = data.tasks.map(task => `
            <div class="task-item">
                <span class="task-status ${task.status}"></span>
                <span class="task-id">${task.id}</span>
                <span class="task-model">${task.model}</span>
                <span class="task-time">${formatTime(task.last_active)}</span>
                <span class="task-duration">${task.duration_minutes}分钟</span>
            </div>
        `).join('');
        
    } catch (e) {
        console.error('加载任务数据失败:', e);
    }
}

async function loadLogsData() {
    try {
        const days = document.getElementById('log-days').value;
        const resp = await fetch(`/api/logs?days=${days}`);
        const data = await resp.json();
        
        const errorList = document.getElementById('error-list');
        
        if (!data || data.length === 0) {
            errorList.innerHTML = '<div class="empty-state">暂无错误日志</div>';
            return;
        }
        
        errorList.innerHTML = data.map(log => `
            <div class="log-item ${log.level}">
                <div class="log-level ${log.level}">${log.level}</div>
                <div class="log-message">${escapeHtml(log.message)}</div>
                <div class="log-meta">
                    <span>${formatTime(log.time)}</span>
                    <span>发生 ${log.count} 次</span>
                </div>
            </div>
        `).join('');
        
    } catch (e) {
        console.error('加载日志失败:', e);
    }
}

// ========== 定价管理 ==========
async function loadPricingData() {
    try {
        const resp = await fetch('/api/pricing');
        const data = await resp.json();
        
        pricingData = data;
        currentCurrency = data.currency || 'CNY';
        
        // 更新货币设置
        document.getElementById('display-currency').value = currentCurrency;
        
        // 更新汇率显示
        if (data.exchange_rate) {
            document.getElementById('exchange-rate').value = 
                data.exchange_rate.USD_TO_CNY || 7.25;
            const updated = data.exchange_rate.last_updated;
            document.getElementById('rate-last-updated').textContent = 
                `上次更新: ${updated ? formatTime(updated) : '-'}`;
        }
        
        // 渲染定价表格
        renderPricingTable(data.models || {});
        
        // 渲染历史
        renderPricingHistory(data.history || []);
        
    } catch (e) {
        console.error('加载定价数据失败:', e);
    }
}

function renderPricingTable(models) {
    const tbody = document.getElementById('pricing-tbody');
    
    const modelList = Object.entries(models).filter(([k]) => k !== 'default');
    
    if (modelList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">暂无定价配置</td></tr>';
        return;
    }
    
    tbody.innerHTML = modelList.map(([name, config]) => `
        <tr>
            <td><code>${escapeHtml(name)}</code></td>
            <td>${config.provider || '-'}</td>
            <td>${config.input_per_1k?.toFixed(4) || '-'}</td>
            <td>${config.output_per_1k?.toFixed(4) || '-'}</td>
            <td>${config.currency || 'USD'}</td>
            <td>
                <button class="btn small" onclick='editPricing("${name}")'>编辑</button>
                <button class="btn small secondary" onclick='deletePricing("${name}")'>删除</button>
            </td>
        </tr>
    `).join('');
}

function renderPricingHistory(history) {
    const container = document.getElementById('pricing-history');
    
    if (history.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无修改记录</div>';
        return;
    }
    
    container.innerHTML = history.map(h => `
        <div class="history-item">
            <div class="history-info">
                <div class="history-model">${escapeHtml(h.model)}</div>
                <div class="history-change">
                    ${h.action === 'reset_to_default' 
                        ? '重置为默认定价' 
                        : `输入: ${h.old_input} → ${h.new_input}, 输出: ${h.old_output} → ${h.new_output}`
                    }
                </div>
            </div>
            <div class="history-time">${formatTime(h.date)}</div>
        </div>
    `).join('');
}

function openPricingModal(modelName = '') {
    const modal = document.getElementById('edit-pricing-modal');
    modal.classList.add('active');
    
    if (modelName && pricingData.models && pricingData.models[modelName]) {
        const config = pricingData.models[modelName];
        document.getElementById('edit-model-name').value = modelName;
        document.getElementById('edit-model-display').value = modelName;
        document.getElementById('edit-provider').value = config.provider || '';
        document.getElementById('edit-input-price').value = config.input_per_1k || 0;
        document.getElementById('edit-output-price').value = config.output_per_1k || 0;
        document.getElementById('edit-currency').value = config.currency || 'CNY';
        document.getElementById('edit-reason').value = '';
    } else {
        // 新增模式
        document.getElementById('pricing-form').reset();
        document.getElementById('edit-model-name').value = '';
        document.getElementById('edit-model-display').value = '';
        document.getElementById('edit-model-display').readOnly = false;
    }
}

function closePricingModal() {
    document.getElementById('edit-pricing-modal').classList.remove('active');
}

async function savePricing() {
    const modelName = document.getElementById('edit-model-name').value || 
                      document.getElementById('edit-model-display').value;
    
    if (!modelName) {
        showToast('请输入模型名称', 'error');
        return;
    }
    
    const data = {
        model: modelName,
        input_per_1k: parseFloat(document.getElementById('edit-input-price').value) || 0,
        output_per_1k: parseFloat(document.getElementById('edit-output-price').value) || 0,
        currency: document.getElementById('edit-currency').value,
        provider: document.getElementById('edit-provider').value,
        reason: document.getElementById('edit-reason').value
    };
    
    try {
        const resp = await fetch('/api/pricing', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await resp.json();
        
        if (result.success) {
            showToast('定价已保存', 'success');
            closePricingModal();
            loadPricingData();
        } else {
            showToast(result.error || '保存失败', 'error');
        }
    } catch (e) {
        showToast('保存失败: ' + e.message, 'error');
    }
}

async function deletePricing(modelName) {
    if (!confirm(`确定要删除 ${modelName} 的定价配置吗？`)) {
        return;
    }
    
    try {
        const resp = await fetch(`/api/pricing/model/${encodeURIComponent(modelName)}`, {
            method: 'DELETE'
        });
        
        const result = await resp.json();
        
        if (result.success) {
            showToast('定价已删除', 'success');
            loadPricingData();
        } else {
            showToast('删除失败', 'error');
        }
    } catch (e) {
        showToast('删除失败: ' + e.message, 'error');
    }
}

async function resetPricing() {
    if (!confirm('确定要重置所有定价为默认值吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        const resp = await fetch('/api/pricing/reset', {method: 'POST'});
        const result = await resp.json();
        
        if (result.success) {
            showToast('已重置为默认定价', 'success');
            loadPricingData();
        } else {
            showToast('重置失败', 'error');
        }
    } catch (e) {
        showToast('重置失败: ' + e.message, 'error');
    }
}

async function setDisplayCurrency(currency) {
    try {
        const resp = await fetch('/api/pricing/currency', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({currency})
        });
        
        const result = await resp.json();
        if (result.success) {
            currentCurrency = currency;
            showToast(`显示货币已切换为 ${currency}`, 'success');
            loadPricingData();
            loadAllData(); // 刷新成本显示
        }
    } catch (e) {
        showToast('切换货币失败', 'error');
    }
}

async function updateExchangeRate(auto = false) {
    try {
        const rate = auto ? null : parseFloat(document.getElementById('exchange-rate').value);
        
        const resp = await fetch('/api/pricing/exchange-rate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({rate})
        });
        
        const result = await resp.json();
        
        if (result.success) {
            showToast(`汇率已更新: ${result.rate}`, 'success');
            document.getElementById('exchange-rate').value = result.rate;
            loadPricingData();
        } else {
            showToast(result.error || '更新失败', 'error');
        }
    } catch (e) {
        showToast('更新汇率失败: ' + e.message, 'error');
    }
}

// ========== 成本显示更新 ==========
function updateCostDisplay(tokenUsage) {
    if (!tokenUsage || !pricingData.models) return;
    
    // 使用默认模型计算成本示例
    const defaultPricing = pricingData.models.default || {input_per_1k: 0.003, output_per_1k: 0.015, currency: 'USD'};
    
    const calculateCost = (tokens) => {
        if (!tokens) return 0;
        const inputTokens = tokens * 0.6;
        const outputTokens = tokens * 0.4;
        const cost = (inputTokens / 1000) * defaultPricing.input_per_1k + 
                     (outputTokens / 1000) * defaultPricing.output_per_1k;
        return cost;
    };
    
    const todayCost = calculateCost(tokenUsage.today?.total);
    const weekCost = calculateCost(tokenUsage.week?.total);
    
    // 转换为显示货币
    const rate = currentCurrency === 'CNY' ? (pricingData.exchange_rate?.USD_TO_CNY || 7.25) : 1;
    
    document.getElementById('today-cost').textContent = 
        formatCurrency(todayCost * rate, currentCurrency);
    document.getElementById('week-cost').textContent = 
        formatCurrency(weekCost * rate, currentCurrency);
}

// ========== 图表渲染 ==========
function renderUsageChart(dailyData) {
    const ctx = document.getElementById('usage-chart');
    if (!ctx) return;
    
    const labels = dailyData.map(d => d.date.slice(5)); // MM-DD
    const inputData = dailyData.map(d => d.input || 0);
    const outputData = dailyData.map(d => d.output || 0);
    const costData = dailyData.map(d => d.cost || 0);
    
    if (usageChart) {
        usageChart.destroy();
    }
    
    const isDark = document.body.classList.contains('dark');
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? '#334155' : '#e2e8f0';
    
    usageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '输入 Tokens',
                    data: inputData,
                    backgroundColor: '#6366f1',
                    borderRadius: 4
                },
                {
                    label: '输出 Tokens',
                    data: outputData,
                    backgroundColor: '#f59e0b',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: { color: textColor }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    ticks: { color: textColor },
                    grid: { color: gridColor }
                },
                y: {
                    stacked: true,
                    ticks: { 
                        color: textColor,
                        callback: function(value) {
                            return formatTokens(value);
                        }
                    },
                    grid: { color: gridColor }
                }
            }
        }
    });
}

// ========== 自动刷新 ==========
function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        if (currentTab === 'overview') {
            loadSummaryData();
        } else if (currentTab === 'tasks') {
            loadTasksData();
        }
    }, 10000); // 10秒刷新
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// ========== 工具函数 ==========
function formatTokens(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(0) + 'K';
    return n.toString();
}

function formatCurrency(amount, currency = 'CNY') {
    const symbol = currency === 'CNY' ? '¥' : '$';
    if (amount >= 0.01) {
        return symbol + amount.toFixed(2);
    } else if (amount > 0) {
        return symbol + amount.toFixed(4);
    }
    return symbol + '0.00';
}

function formatDuration(seconds) {
    if (!seconds) return '-';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}天${hours}小时`;
    if (hours > 0) return `${hours}小时${minutes}分钟`;
    return `${minutes}分钟`;
}

function formatTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    const now = new Date();
    const diff = (now - date) / 1000; // seconds
    
    if (diff < 60) return '刚刚';
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
    
    return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// 全局函数（供 HTML 调用）
window.editPricing = function(modelName) {
    openPricingModal(modelName);
};

window.deletePricing = function(modelName) {
    deletePricing(modelName);
};
