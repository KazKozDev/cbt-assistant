function sendQuick(txt) {
    document.getElementById('msgInput').value = txt;
    sendMessage();
}

function currentChatLanguage() {
    return (window.getCurrentLanguage && window.getCurrentLanguage()) || 'en';
}

async function sendMessage() {
    let inEl = document.getElementById('msgInput');
    let txt = inEl.value.trim();
    if (!txt || isProc) return;
    // Stop listening before the assistant can answer; otherwise speech
    // recognition may feed the assistant's TTS audio back into the input.
    if (window.stopMicInput) window.stopMicInput();
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
        addRagSources(data.context_used || [], data.rag_trace);
        if (data.client_events) {
            data.client_events.forEach(ev => {
                if (ev.type === 'add_activity' && window.addActivityFromAI) {
                    window.addActivityFromAI(ev.text);
                } else if (ev.type === 'add_thought_record' && window.addThoughtRecordFromAI) {
                    window.addThoughtRecordFromAI(ev.record);
                } else if (ev.type === 'add_sleep_log' && window.addSleepLogFromAI) {
                    window.addSleepLogFromAI(ev.log);
                } else if (ev.type === 'start_sos_exercise' && window.startSosExerciseFromAI) {
                    window.startSosExerciseFromAI(ev);
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

function addRagSources(context, trace) {
    if (!context.length) return;
    const list = document.getElementById('messages');
    const panel = document.createElement('div');
    panel.className = 'rag-sources';

    const heading = document.createElement('div');
    heading.className = 'rag-sources-title';
    heading.textContent = currentChatLanguage() === 'en' ? 'Knowledge sources' : 'Источники базы знаний';
    panel.appendChild(heading);

    context.forEach(item => {
        const source = document.createElement('div');
        source.className = 'rag-source';
        const label = document.createElement('span');
        label.className = 'rag-source-label';
        label.textContent = item.section_path || item.title;
        const meta = document.createElement('code');
        meta.textContent = `[KB:${item.chunk_id}] · ${item.source} · ${Number(item.score).toFixed(3)}`;
        source.append(label, meta);
        panel.appendChild(source);
    });

    if (trace?.trace_id) {
        panel.dataset.traceId = trace.trace_id;
        panel.title = `RAG trace ${trace.trace_id}, index ${trace.index_version}`;
    }
    list.appendChild(panel);
    list.scrollTop = list.scrollHeight;
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
