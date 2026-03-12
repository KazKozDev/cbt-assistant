document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    checkH();
    updateWelcomeMsg();
    const msgInp = document.getElementById('msgInput');
    msgInp.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    syncData('/api/sync/sleep', 'sleepLog');
    syncData('/api/sync/activities', 'activities');
    syncTests();

    // Restore notification schedules
    const ns = JSON.parse(localStorage.getItem('notifSettings') || '{}');
    if (ns.morning || ns.evening) scheduleNotifications(ns);
    // Update bell icon if notifications are active
    if (ns.morning || ns.evening) {
        const bell = document.getElementById('notifSidebarBtn');
        if (bell) bell.style.color = 'var(--accent)';
    }

    // Inject welcome heading into chat-box
    const messages = document.getElementById('messages');
    const welcome = document.createElement('div');
    welcome.id = 'welcome';
    welcome.style.cssText = 'display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; padding: 60px 0 32px; text-align:center;';
    welcome.innerHTML = `
                <div style="display:flex; align-items:center; gap:12px;">
                    <i data-lucide="sparkle" id="welcomeIcon" style="width:32px; height:32px; color:var(--accent);"></i>
                    <h1 id="welcomeText" style="font-family: Georgia, 'Times New Roman', serif; font-size:30px; font-weight:normal; color:var(--text); letter-spacing:-0.5px;">Добрый день</h1>
                </div>`;
    messages.prepend(welcome);
    lucide.createIcons();
    updateWelcomeMsg();
    if (window.applyTranslations) window.applyTranslations();
});
