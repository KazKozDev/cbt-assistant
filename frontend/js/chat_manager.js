function sendQuick(txt) {
    document.getElementById('msgInput').value = txt;
    sendMessage();
}

function currentChatLanguage() {
    return (window.getCurrentLanguage && window.getCurrentLanguage()) || 'ru';
}

async function sendMessage() {
    let inEl = document.getElementById('msgInput');
    let txt = inEl.value.trim();
    if (!txt || isProc) return;
    isProc = true;
    inEl.value = ''; inEl.style.height = 'auto';

    document.getElementById('welcome')?.remove();
    document.getElementById('mainContainer')?.classList.remove('empty-state');

    addMsg('user', txt);
    addMsg('assistant', '<i data-lucide="loader-2" style="width:20px; animation: spin 1.5s linear infinite; color: var(--gray);"></i>', 'loading');

    try {
        let res = await fetch(API + '/api/chat', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: txt, session_id: SESSION_ID, language: currentChatLanguage() })
        });
        let data = await res.json();
        document.getElementById('loading').remove();
        addMsg('assistant', data.response);
        if (data.client_events) {
            data.client_events.forEach(ev => {
                if (ev.type === 'add_activity' && window.addActivityFromAI) {
                    window.addActivityFromAI(ev.text);
                } else if (ev.type === 'start_breathing' && window.startBreathingFromAI) {
                    window.startBreathingFromAI();
                } else if (ev.type === 'open_test' && window.openTestFromAI) {
                    window.openTestFromAI(ev.test_type);
                }
            });
        }
        if (ttsEnabled && window.playAssistantSpeech) {
            await window.playAssistantSpeech(data.response, currentChatLanguage());
        }
    } catch (e) {
        document.getElementById('loading').remove();
        addMsg('assistant', currentChatLanguage() === 'en' ? '⚠️ Request to the server failed.' : '⚠️ Ошибка запроса к серверу.');
    }
    isProc = false;
}

function addMsg(role, content, id = '') {
    let list = document.getElementById('messages');
    let div = document.createElement('div');
    div.className = 'msg ' + role;
    if (id) div.id = id;

    // Clean representation
    let avatarIcon = role === 'user' ? 'user' : 'sparkles';
    let parsed = content.replace(/\n\n/g, '</p><p>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    if (!parsed.startsWith('<p>') && parsed.indexOf('<') !== 0) {
        parsed = '<p>' + parsed + '</p>';
    }

    div.innerHTML = `
            <div class="msg-avatar"><i data-lucide="${avatarIcon}" style="width:18px;"></i></div>
            <div class="msg-content">${parsed}</div>
        `;
    list.appendChild(div);
    lucide.createIcons();
    list.scrollTop = list.scrollHeight;
}
