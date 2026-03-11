const API = window.location.origin;
        const SESSION_ID = 'session_' + Date.now().toString(36);
        let isProc = false;

        async function syncData(endpoint, storageKey) {
            let items = JSON.parse(localStorage.getItem(storageKey) || '[]');
            try {
                await fetch(API + endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: SESSION_ID, items })
                });
            } catch (e) { console.error('Failed to sync', storageKey, e); }
        }

        async function syncTests() {
            let phq = JSON.parse(localStorage.getItem('phqHistory') || '[]').map(t => ({ ...t, name: 'PHQ-9' }));
            let gad = JSON.parse(localStorage.getItem('gadHistory') || '[]').map(t => ({ ...t, name: 'GAD-7' }));
            try {
                await fetch(API + '/api/sync/tests', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: SESSION_ID, items: phq.concat(gad) })
                });
            } catch (e) { console.error('Failed to sync tests', e); }
        }

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
        });

        function updateWelcomeMsg() {
            let h = new Date().getHours();
            let msg = 'Добрый день';
            if (h >= 5 && h < 12) { msg = 'Доброе утро'; }
            else if (h >= 18 && h < 23) { msg = 'Добрый вечер'; }
            else if (h >= 23 || h < 5) { msg = 'Доброй ночи'; }

            let welText = document.getElementById('welcomeText');
            if (welText) welText.innerText = msg + ', Артем';
        }

        async function checkH() {
            try {
                let r = await fetch(API + '/api/health').then(r => r.json());
                let d = document.getElementById('dotStatus');
                let t = document.getElementById('txtStatus');
                if (r.ollama_connected) {
                    d.className = 'status-dot online';
                    t.innerText = r.model;
                }
                else { d.className = 'status-dot'; t.innerText = 'Ollama offline'; }
            } catch (e) { document.getElementById('txtStatus').innerText = 'Бекенд недоступен'; }
        }

        function toggleSuggestMenu(id) {
            document.querySelectorAll('.suggest-dropdown.open').forEach(el => {
                if (el.id !== id) el.classList.remove('open');
            });
            let el = document.getElementById(id);
            if (el) el.classList.toggle('open');
        }

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.suggest-dropdown')) {
                document.querySelectorAll('.suggest-dropdown.open').forEach(el => el.classList.remove('open'));
            }
        });

        function openModal(id) { document.getElementById(id).style.display = 'flex'; }
        function closeModal(id) {
            document.getElementById(id).style.display = 'none';
            if (id === 'sosModal') stopBreathing();
        }

        function sendQuick(txt) {
            document.getElementById('msgInput').value = txt;
            sendMessage();
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
                    body: JSON.stringify({ message: txt, session_id: SESSION_ID })
                });
                let data = await res.json();
                document.getElementById('loading').remove();
                addMsg('assistant', data.response);
                if (ttsEnabled && window.speechSynthesis) {
                    window.speechSynthesis.cancel();
                    let cleanText = data.response.replace(/<[^>]+>/g, '').replace(/\*/g, '').substring(0, 1000); // strip markdown and keep reasonable length
                    let utterance = new SpeechSynthesisUtterance(cleanText);
                    utterance.lang = 'ru-RU';
                    window.speechSynthesis.speak(utterance);
                }
            } catch (e) {
                document.getElementById('loading').remove();
                addMsg('assistant', '⚠️ Ошибка запроса к серверу.');
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

        async function logMood() {
            let s = document.getElementById('moodSlider').value;
            let btn = event.target;
            btn.innerText = 'Записываем...';
            await fetch(API + '/api/mood', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ score: parseInt(s), session_id: SESSION_ID }) });
            // Save locally for dashboard
            let ml = JSON.parse(localStorage.getItem('moodLog') || '[]');
            ml.push({ score: parseInt(s), date: new Date().toISOString() });
            if (ml.length > 90) ml = ml.slice(-90);
            localStorage.setItem('moodLog', JSON.stringify(ml));
            btn.innerText = 'Записано ✓';
            setTimeout(() => btn.innerText = 'Записать состояние', 2000);
            document.getElementById('moodHistory').innerText = `Последняя запись: ${s}/10`;
        }

        async function submitThought(e) {
            e.preventDefault();
            let b = document.getElementById('tSub'); b.disabled = true; b.innerText = 'Сохраняем...';
            let d = {
                session_id: SESSION_ID,
                situation: document.getElementById('tSit').value,
                thought: document.getElementById('tThou').value,
                emotion: document.getElementById('tEmo').value,
                intensity: parseInt(document.getElementById('tInt').value),
                distortion: document.getElementById('tDist').value,
                rational_response: document.getElementById('tRat').value
            };
            try {
                await fetch(API + '/api/thoughts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) });
                closeModal('thoughtModal');
                document.getElementById('tForm').reset();
                addMsg('assistant', 'Запись в дневник добавлена. Формулируя дальнейшие ответы, я учту вашу новую мысль.');
            } catch (err) { alert('Ошибка при сохранении.'); }
            b.disabled = false; b.innerText = 'Сохранить запись';
        }

        async function openThoughtHistoryModal() {
            openModal('histModal');
            let c = document.getElementById('histContent');
            c.innerHTML = '<div style="color:var(--gray); text-align:center;">Загрузка...</div>';
            try {
                let res = await fetch(API + '/api/thoughts/' + SESSION_ID).then(r => r.json());
                let recs = res.thought_records || [];
                if (!recs.length) { c.innerHTML = '<div style="color:var(--gray); text-align:center;">Вы еще не добавили ни одной записи.</div>'; return; }
                let h = '';
                recs.reverse().forEach(r => {
                    let t = new Date(r.timestamp);
                    let tStr = t.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }) + ' в ' + t.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                    h += `
                <div class="timeline-item">
                    <div class="ti-time"><i data-lucide="clock" style="width:12px;"></i> ${tStr}</div>
                    <div class="ti-field"><strong>Ситуация</strong> ${r.situation}</div>
                    <div class="ti-field"><strong>Мысль</strong> ${r.thought}</div>
                    <div class="ti-field"><strong>Эмоция</strong> ${r.emotion} (${r.intensity}/10)</div>
                    <div class="ti-field"><strong>Рациональный ответ</strong> ${r.rational_response}</div>
                    <div class="ti-distortion"><i data-lucide="brain-circuit" style="width:12px;"></i> ${r.distortion}</div>
                </div>`;
                });
                c.innerHTML = h;
                lucide.createIcons();
            } catch (e) { c.innerHTML = '<div style="color:var(--danger); text-align:center;">Ошибка загрузки истории</div>'; }
        }

        /* Minimalist STT */
        let rec = null, isRec = false;
        if (window.SpeechRecognition || window.webkitSpeechRecognition) {
            let SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            rec = new SR(); rec.lang = 'ru-RU'; rec.continuous = true; rec.interimResults = true;
            rec.onresult = (e) => {
                let t = '';
                for (let i = e.resultIndex; i < e.results.length; i++) t += e.results[i][0].transcript;
                let inp = document.getElementById('msgInput');
                inp.value = t;
                inp.dispatchEvent(new Event('input')); // trigger resize
            };
            rec.onend = () => { if (isRec) try { rec.start() } catch (e) { } };
        }
        function toggleMic() {
            if (!rec) return;
            let btn = document.getElementById('micBtn');
            if (isRec) { isRec = false; btn.style.color = ''; rec.stop(); document.getElementById('msgInput').placeholder = 'Задайте вопрос...'; }
            else { isRec = true; btn.style.color = 'var(--accent)'; rec.start(); document.getElementById('msgInput').placeholder = 'Слушаю...'; }
        }

        let ttsEnabled = false;
        function toggleTTS() {
            ttsEnabled = !ttsEnabled;
            let btn = document.getElementById('ttsBtn');
            if (ttsEnabled) {
                btn.style.color = 'var(--accent)';
                btn.innerHTML = '<i data-lucide="volume-2" style="width:18px;"></i>';
                // optional: play short sound indicating enablement
                if (window.speechSynthesis) {
                    let ut = new SpeechSynthesisUtterance("Голос включен");
                    ut.lang = 'ru-RU';
                    window.speechSynthesis.speak(ut);
                }
            } else {
                btn.style.color = '';
                btn.innerHTML = '<i data-lucide="volume-x" style="width:18px;"></i>';
                if (window.speechSynthesis) window.speechSynthesis.cancel();
            }
            lucide.createIcons();
        }

        /* Breathing Exercise */
        let breatheInterval = null;
        let breatheState = 0; // 0=in, 1=hold, 2=out, 3=hold
        function toggleBreathing() {
            let btn = document.getElementById('btnBreathe');
            if (breatheInterval) {
                stopBreathing();
                return;
            }
            btn.innerText = 'Остановить упражнение';
            btn.style.background = 'var(--danger)';
            breatheState = 0;
            stepBreathe();
            breatheInterval = setInterval(stepBreathe, 4000);
        }

        function stopBreathing() {
            let btn = document.getElementById('btnBreathe');
            let circle = document.getElementById('breatheCircle');
            if (breatheInterval) clearInterval(breatheInterval);
            breatheInterval = null;
            if (btn) {
                btn.innerText = 'Начать упражнение';
                btn.style.background = '#a87b8d';
            }
            if (circle) {
                circle.style.transform = 'scale(1)';
                circle.style.background = 'var(--border)';
                circle.style.color = 'var(--text)';
                circle.innerText = 'Дыхание';
            }
        }

        function stepBreathe() {
            let circle = document.getElementById('breatheCircle');
            if (breatheState === 0) {
                circle.innerText = 'Вдох...';
                circle.style.transform = 'scale(1.5)';
                circle.style.background = 'var(--accent-light)';
                circle.style.color = 'var(--accent)';
            } else if (breatheState === 1) {
                circle.innerText = 'Задержка';
            } else if (breatheState === 2) {
                circle.innerText = 'Выдох...';
                circle.style.transform = 'scale(1)';
                circle.style.background = 'var(--border)';
                circle.style.color = 'var(--text)';
            } else if (breatheState === 3) {
                circle.innerText = 'Задержка';
            }
            breatheState = (breatheState + 1) % 4;
        }

        /* PHQ-9 */
        const PHQ9_Q = [
            'Отсутствие интереса или удовольствия от дел, которые раньше нравились',
            'Подавленное настроение, ощущение безнадёжности или депрессии',
            'Нарушения сна (трудно заснуть, частые пробуждения или, наоборот, слишком много сплю)',
            'Усталость или ощущение нехватки сил',
            'Плохой аппетит или переедание',
            'Ощущение себя неудачником или чувство вины',
            'Трудности с концентрацией внимания (чтение, телевизор, работа)',
            'Заметно замедленные движения или речь — или, наоборот, суетливость и трудно успокоиться',
            'Мысли о том, что лучше было бы умереть, или желание причинить себе вред'
        ];
        const PHQ9_OPTS = ['Совсем нет', 'Несколько дней', 'Больше половины дней', 'Почти каждый день'];

        function initPHQ() {
            let c = document.getElementById('phqQuestions');
            if (c.children.length > 0) return;
            PHQ9_Q.forEach((q, i) => {
                let div = document.createElement('div');
                div.style = 'margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 16px;';
                div.innerHTML = `<p style="font-size:14px; margin-bottom: 10px; font-weight: 500;">${i + 1}. ${q}</p>
                <div style="display:flex; flex-direction:column; gap:6px;">
                ${PHQ9_OPTS.map((opt, j) => `
                  <label style="display:flex; align-items:center; gap:8px; font-size:13px; color: var(--gray); cursor:pointer;">
                    <input type="radio" name="phq${i}" value="${j}" required style="accent-color: var(--accent);"> ${opt}
                  </label>`).join('')}
                </div>`;
                c.appendChild(div);
            });
        }

        document.getElementById('phqModal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('phqModal')) return;
            initPHQ();
        });
        document.querySelector('[onclick*="phqModal"]')?.addEventListener('click', initPHQ);

        function submitPHQ(e) {
            e.preventDefault();
            let total = 0;
            PHQ9_Q.forEach((_, i) => {
                let val = document.querySelector(`input[name="phq${i}"]:checked`);
                if (val) total += parseInt(val.value);
            });
            let level, color, advice;
            if (total <= 4) { level = 'Минимальная или отсутствующая'; color = 'var(--success)'; advice = 'Ваши результаты указывают на отсутствие значимых признаков депрессии. Продолжайте заботиться о себе.'; }
            else if (total <= 9) { level = 'Лёгкая депрессия'; color = 'var(--warning)'; advice = 'Возможны признаки лёгкой депрессии. Обратите внимание на сон, активность и социальные связи. Поговорите с ассистентом о своём состоянии.'; }
            else if (total <= 14) { level = 'Умеренная депрессия'; color = 'var(--warning)'; advice = 'Результаты указывают на умеренную депрессию. Рекомендуется обратиться к специалисту для дополнительной оценки.'; }
            else if (total <= 19) { level = 'Умеренно-тяжёлая депрессия'; color = 'var(--danger)'; advice = 'Признаки выраженной депрессии. Настоятельно рекомендуется консультация врача или психотерапевта.'; }
            else { level = 'Тяжёлая депрессия'; color = 'var(--danger)'; advice = 'Тяжёлая депрессия. Пожалуйста, обратитесь к специалисту как можно скорее. Горячая линия: 8-800-333-44-34.'; }

            let r = document.getElementById('phqResult');
            r.style.display = 'block';
            r.innerHTML = `
                <div style="font-size: 36px; font-weight: 700; color: ${color}; margin-bottom: 4px;">${total} / 27</div>
                <div style="font-size: 15px; font-weight: 600; color: ${color}; margin-bottom: 12px;">${level}</div>
                <p style="font-size: 13px; color: var(--gray); line-height: 1.6;">${advice}</p>
                <button onclick="sendQuick('Мой PHQ-9 показал ${total} баллов (${level}). Помоги мне понять, что с этим делать.')" 
                  style="margin-top:16px; padding:10px 16px; border-radius:8px; border: 1px solid var(--border); background:transparent; cursor:pointer; font-size:13px; color: var(--text);">
                  Обсудить результат с ассистентом
                </button>
            `;
            r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            // Save PHQ result for dashboard
            let phqHist = JSON.parse(localStorage.getItem('phqHistory') || '[]');
            phqHist.push({ score: total, level, date: new Date().toISOString() });
            localStorage.setItem('phqHistory', JSON.stringify(phqHist));
            syncTests();
        }

        /* ── GAD-7 ── */
        const GAD7_Q = [
            'Нервозность, тревожность или ощущение напряжения',
            'Невозможность остановить или контролировать беспокойство',
            'Чрезмерное беспокойство о разных вещах',
            'Трудности с расслаблением',
            'Такое беспокойство, что трудно усидеть на месте',
            'Лёгкая раздражительность или нервозность',
            'Страх, что может случиться что-то плохое'
        ];

        function initGAD() {
            let c = document.getElementById('gadQuestions');
            if (c.children.length > 0) return;
            GAD7_Q.forEach((q, i) => {
                let div = document.createElement('div');
                div.style = 'margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 16px;';
                div.innerHTML = `<p style="font-size:14px; margin-bottom: 10px; font-weight: 500;">${i + 1}. ${q}</p>
                <div style="display:flex; flex-direction:column; gap:6px;">
                ${['Совсем нет', 'Несколько дней', 'Больше половины дней', 'Почти каждый день'].map((opt, j) => `
                  <label style="display:flex; align-items:center; gap:8px; font-size:13px; color: var(--gray); cursor:pointer;">
                    <input type="radio" name="gad${i}" value="${j}" required style="accent-color: var(--accent);"> ${opt}
                  </label>`).join('')}
                </div>`;
                c.appendChild(div);
            });
        }
        document.getElementById('gadModal').addEventListener('click', () => initGAD());

        function submitGAD(e) {
            e.preventDefault();
            let total = 0;
            GAD7_Q.forEach((_, i) => {
                let v = document.querySelector(`input[name="gad${i}"]:checked`);
                if (v) total += parseInt(v.value);
            });
            let level, color, advice;
            if (total <= 4) { level = 'Минимальная тревожность'; color = 'var(--success)'; advice = 'Признаки тревоги минимальны или отсутствуют. Продолжайте придерживаться здоровых привычек.'; }
            else if (total <= 9) { level = 'Лёгкая тревожность'; color = 'var(--warning)'; advice = 'Слабая тревога. Попробуйте дыхательные упражнения, ограничьте кофеин и стрессовые ситуации.'; }
            else if (total <= 14) { level = 'Умеренная тревожность'; color = 'var(--warning)'; advice = 'Умеренная тревога. Рекомендуется обратиться к специалисту. КПТ-техники могут существенно помочь.'; }
            else { level = 'Тяжёлая тревожность'; color = 'var(--danger)'; advice = 'Выраженная тревога. Пожалуйста, обратитесь к врачу или психотерапевту. Горячая линия: 8-800-333-44-34.'; }
            let r = document.getElementById('gadResult');
            r.style.display = 'block';
            r.innerHTML = `
                <div style="font-size:36px;font-weight:700;color:${color};margin-bottom:4px;">${total} / 21</div>
                <div style="font-size:15px;font-weight:600;color:${color};margin-bottom:12px;">${level}</div>
                <p style="font-size:13px;color:var(--gray);line-height:1.6;">${advice}</p>
                <button onclick="sendQuick('Мой GAD-7 показал ${total} баллов (${level}). Как мне справиться с этим?')"
                  style="margin-top:16px;padding:10px 16px;border-radius:8px;border:1px solid var(--border);background:transparent;cursor:pointer;font-size:13px;color:var(--text);">
                  Обсудить с ассистентом
                </button>`;
            r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            // Save GAD result for dashboard
            let gadHist = JSON.parse(localStorage.getItem('gadHistory') || '[]');
            gadHist.push({ score: total, level, date: new Date().toISOString() });
            localStorage.setItem('gadHistory', JSON.stringify(gadHist));
            syncTests();
        }

        /* ── Sleep Diary ── */
        let sleepLog = JSON.parse(localStorage.getItem('sleepLog') || '[]');

        function submitSleep(e) {
            e.preventDefault();
            let bed = document.getElementById('slBed').value;
            let wake = document.getElementById('slWake').value;
            let awk = parseInt(document.getElementById('slAwk').value) || 0;
            let qual = parseInt(document.getElementById('slQual').value);
            let notes = document.getElementById('slNotes').value;

            // Calculate total sleep hours (simple)
            let [bh, bm] = bed.split(':').map(Number);
            let [wh, wm] = wake.split(':').map(Number);
            let bedMins = bh * 60 + bm;
            let wakeMins = wh * 60 + wm;
            if (wakeMins < bedMins) wakeMins += 24 * 60;
            let durHrs = ((wakeMins - bedMins) / 60).toFixed(1);

            let entry = { date: new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }), bed, wake, awk, qual, notes, durHrs, isoDate: new Date().toISOString() };
            sleepLog.unshift(entry);
            if (sleepLog.length > 30) sleepLog.pop();
            localStorage.setItem('sleepLog', JSON.stringify(sleepLog));
            syncData('/api/sync/sleep', 'sleepLog');
            renderSleepHistory();
            e.target.reset();
            document.getElementById('slQualLabel').innerText = '6';
        }

        function renderSleepHistory() {
            let c = document.getElementById('sleepHistory');
            if (!sleepLog.length) { c.innerHTML = ''; return; }
            let avgQual = (sleepLog.slice(0, 7).reduce((a, e) => a + e.qual, 0) / Math.min(sleepLog.length, 7)).toFixed(1);
            let avgDur = (sleepLog.slice(0, 7).reduce((a, e) => a + parseFloat(e.durHrs), 0) / Math.min(sleepLog.length, 7)).toFixed(1);
            c.innerHTML = `<h3 style="font-size:14px;margin-bottom:12px;">История (последние записи)</h3>
            <div style="display:flex;gap:16px;margin-bottom:16px;">
              <div style="flex:1;background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:var(--accent);">${avgDur}ч</div><div style="font-size:12px;color:var(--gray);">Среднее время сна</div>
              </div>
              <div style="flex:1;background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:var(--accent);">${avgQual}/10</div><div style="font-size:12px;color:var(--gray);">Среднее качество</div>
              </div>
            </div>
            ${sleepLog.slice(0, 5).map(e => `
              <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);font-size:13px;">
                <span style="color:var(--gray);">${e.date}</span>
                <span>${e.bed} → ${e.wake} (<strong>${e.durHrs}ч</strong>)</span>
                <span style="color:var(--accent);">⭐ ${e.qual}/10</span>
              </div>`).join('')}`;
        }

        document.getElementById('sleepModal').addEventListener('click', () => renderSleepHistory());

        /* ── Activity Planner ── */
        let activities = JSON.parse(localStorage.getItem('activities') || '[]');

        function renderActivities() {
            let list = document.getElementById('actList');
            let stats = document.getElementById('actStats');
            if (!activities.length) { list.innerHTML = '<div style="color:var(--gray);text-align:center;padding:20px 0;">Нет активностей. Добавьте первую!</div>'; stats.style.display = 'none'; return; }
            let done = activities.filter(a => a.done).length;
            list.innerHTML = activities.map((a, i) => `
                <div style="display:flex;align-items:center;gap:12px;padding:12px;background:var(--bg);border:1px solid var(--border);border-radius:10px;${a.done ? 'opacity:0.6;' : ''}">
                    <input type="checkbox" ${a.done ? 'checked' : ''} onchange="toggleActivity(${i})" style="width:18px;height:18px;accent-color:var(--accent);cursor:pointer;flex-shrink:0;">
                    <span style="flex:1;font-size:14px;${a.done ? 'text-decoration:line-through;color:var(--gray);' : ''}">${a.text}</span>
                    ${a.done ? `<span style="font-size:12px;color:var(--success);">+настроение</span>` : ''}
                    <button onclick="removeActivity(${i})" style="background:none;border:none;cursor:pointer;color:var(--gray);font-size:16px;padding:0 4px;line-height:1;">×</button>
                </div>`).join('');
            if (done > 0) {
                stats.style.display = 'block';
                stats.innerHTML = `Выполнено: <strong>${done} из ${activities.length}</strong>. ${done >= 3 ? '🎉 Отличный прогресс сегодня!' : 'Каждый маленький шаг важен.'}`;
            } else { stats.style.display = 'none'; }
        }

        function addActivity() {
            let inp = document.getElementById('actInput');
            let txt = inp.value.trim();
            if (!txt) return;
            activities.unshift({ text: txt, done: false, date: new Date().toLocaleDateString('ru-RU'), isoDate: new Date().toISOString() });
            localStorage.setItem('activities', JSON.stringify(activities));
            syncData('/api/sync/activities', 'activities');
            inp.value = '';
            renderActivities();
        }
        document.getElementById('actInput').addEventListener('keydown', e => { if (e.key === 'Enter') addActivity(); });

        function toggleActivity(i) {
            activities[i].done = !activities[i].done;
            localStorage.setItem('activities', JSON.stringify(activities));
            syncData('/api/sync/activities', 'activities');
            renderActivities();
        }

        function removeActivity(i) {
            activities.splice(i, 1);
            localStorage.setItem('activities', JSON.stringify(activities));
            syncData('/api/sync/activities', 'activities');
            renderActivities();
        }

        document.getElementById('actModal').addEventListener('click', () => renderActivities());

        /* ── Calendar ── */
        let calYear = new Date().getFullYear();
        let calMonth = new Date().getMonth();
        let calThoughtsCache = [];

        const MONTHS_RU = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
        const DAYS_RU = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

        async function openCalendar() {
            openModal('calModal');
            // Fetch thought records once
            try {
                let res = await fetch(API + '/api/thoughts/' + SESSION_ID).then(r => r.json());
                calThoughtsCache = res.thought_records || [];
            } catch (e) { calThoughtsCache = []; }
            renderCalendar();
            lucide.createIcons();
        }

        // Helper to get local date key "YYYY-MM-DD" from ISO string or Date
        function getDateKey(dStr) {
            if (!dStr) return null;
            try {
                let d = new Date(dStr);
                return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
            } catch (e) { return null; }
        }

        function renderCalendar() {
            document.getElementById('calTitle').innerText = MONTHS_RU[calMonth] + ' ' + calYear;

            let moodLog = JSON.parse(localStorage.getItem('moodLog') || '[]');
            let slLog = JSON.parse(localStorage.getItem('sleepLog') || '[]');
            let actLog = JSON.parse(localStorage.getItem('activities') || '[]');
            let phqLog = JSON.parse(localStorage.getItem('phqHistory') || '[]');
            let gadLog = JSON.parse(localStorage.getItem('gadHistory') || '[]');

            // Build day map: 'YYYY-MM-DD' → {thoughts:[], sleep:[], mood:[], acts:[], tests:[]}
            let dayMap = {};

            function addData(arr, type, getDateFn) {
                arr.forEach(item => {
                    let dStr = getDateFn(item);
                    let key = getDateKey(dStr);
                    if (!key) return;
                    let d = new Date(dStr);
                    if (d.getFullYear() === calYear && d.getMonth() === calMonth) {
                        if (!dayMap[key]) dayMap[key] = { thoughts: [], sleep: [], mood: [], acts: [], tests: [] };
                        dayMap[key][type].push(item);
                    }
                });
            }

            addData(calThoughtsCache, 'thoughts', t => t.timestamp);
            addData(moodLog, 'mood', m => m.date); // mood log saves date as ISO string
            addData(slLog, 'sleep', s => s.isoDate || new Date().toISOString()); // fallback if old data
            addData(actLog, 'acts', a => a.isoDate || new Date().toISOString());
            addData(phqLog, 'tests', p => p.date);
            addData(gadLog, 'tests', g => g.date);

            // Render day-of-week header
            let gridEl = document.getElementById('calGrid');
            let headEl = gridEl.previousElementSibling;
            if (!headEl || !headEl.classList.contains('cal-head')) {
                let head = document.createElement('div');
                head.className = 'cal-head';
                head.innerHTML = DAYS_RU.map(d => `<div class="cal-head-day">${d}</div>`).join('');
                gridEl.parentNode.insertBefore(head, gridEl);
            }

            let first = new Date(calYear, calMonth, 1);
            let startDow = (first.getDay() + 6) % 7; // 0=Mon
            let daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
            let today = new Date();

            let cells = '';
            for (let i = 0; i < startDow; i++) cells += `<div class="cal-day empty"></div>`;
            for (let d = 1; d <= daysInMonth; d++) {
                let key = `${calYear}-${String(calMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
                let isToday = d === today.getDate() && calMonth === today.getMonth() && calYear === today.getFullYear();
                let data = dayMap[key] || {};

                let dots = '';
                if (data.thoughts && data.thoughts.length) dots += `<span class="cal-dot" style="background:var(--accent)" title="Дневник мыслей"></span>`;
                if (data.mood && data.mood.length) dots += `<span class="cal-dot" style="background:#f59e0b" title="Трекер настроения"></span>`;
                if (data.sleep && data.sleep.length) dots += `<span class="cal-dot" style="background:#8b5cf6" title="Сон"></span>`;
                if (data.acts && data.acts.length) dots += `<span class="cal-dot" style="background:#10b981" title="Активности"></span>`;
                if (data.tests && data.tests.length) dots += `<span class="cal-dot" style="background:#ef4444" title="Тесты"></span>`;

                cells += `<div class="cal-day${isToday ? ' today' : ''}" onclick="calSelectDay('${key}', ${d})" data-key="${key}">
                    ${d}
                    <div class="cal-dots">${dots}</div>
                </div>`;
            }
            gridEl.innerHTML = cells;

            document.getElementById('calDayTitle').innerText = 'Выберите день';
            document.getElementById('calDayContent').innerHTML = '';
        }

        function calSelectDay(key, day) {
            document.querySelectorAll('.cal-day').forEach(el => el.classList.remove('selected'));
            document.querySelector(`.cal-day[data-key="${key}"]`)?.classList.add('selected');

            let dMatch = new Date(key);
            let label = dMatch.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' });
            document.getElementById('calDayTitle').innerText = label.charAt(0).toUpperCase() + label.slice(1);

            let html = '';

            let thoughts = calThoughtsCache.filter(t => getDateKey(t.timestamp) === key);
            if (thoughts.length) {
                html += `<div style="font-size:12px;text-transform:uppercase;color:var(--gray);letter-spacing:0.5px;margin-bottom:10px;margin-top:16px;">Дневник мыслей (${thoughts.length})</div>`;
                thoughts.forEach(t => {
                    let time = new Date(t.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                    html += `<div style="border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px;background:var(--bg);">
                        <div style="font-size:11px;color:var(--gray);margin-bottom:8px;">${time}</div>
                        <div style="margin-bottom:6px;"><span style="font-size:11px;text-transform:uppercase;color:var(--gray);">Ситуация</span><br>${t.situation}</div>
                        <div style="margin-bottom:6px;"><span style="font-size:11px;text-transform:uppercase;color:var(--gray);">Эмоция</span><br>${t.emotion} — ${t.intensity}/10</div>
                        <div style="margin-bottom:6px;"><span style="font-size:11px;text-transform:uppercase;color:var(--gray);">Ответ</span><br>${t.rational_response}</div>
                    </div>`;
                });
            }

            let moodLog = JSON.parse(localStorage.getItem('moodLog') || '[]').filter(m => getDateKey(m.date) === key);
            if (moodLog.length) {
                html += `<div style="font-size:12px;text-transform:uppercase;color:var(--gray);letter-spacing:0.5px;margin-bottom:10px;margin-top:16px;">Настроение</div>`;
                moodLog.forEach(m => {
                    let time = new Date(m.date).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                    html += `<div style="border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px;background:var(--bg);">
                        <div style="font-size:11px;color:var(--gray);margin-bottom:8px;">${time}</div>
                        <div style="display:flex; align-items:center; gap:8px; font-weight:500;">
                            <span style="font-size:20px">${['😭', '😟', '😐', '🙂', '😁'][m.score - 1] || '😐'}</span>
                            <span>Оценка: ${m.score}/5</span>
                        </div>
                    </div>`;
                });
            }

            let slLog = JSON.parse(localStorage.getItem('sleepLog') || '[]').filter(s => getDateKey(s.isoDate) === key);
            if (slLog.length) {
                html += `<div style="font-size:12px;text-transform:uppercase;color:var(--gray);letter-spacing:0.5px;margin-bottom:10px;margin-top:16px;">Дневник сна</div>`;
                slLog.forEach(s => {
                    html += `<div style="border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px;background:var(--bg);">
                        <div style="display:flex; justify-content:space-between; margin-bottom: 6px;">
                            <span>Отбой: <b>${s.bed}</b></span>
                            <span>Подъём: <b>${s.wake}</b></span>
                        </div>
                        <div style="margin-bottom: 6px; font-size:13px;">Продолжительность: <b>${s.durHrs} ч.</b>, Качество: <b>${s.qual}/10</b></div>
                        ${s.notes ? `<div style="font-size:12px;color:var(--gray);">${s.notes}</div>` : ''}
                    </div>`;
                });
            }

            let actLog = JSON.parse(localStorage.getItem('activities') || '[]').filter(a => getDateKey(a.isoDate) === key);
            if (actLog.length) {
                html += `<div style="font-size:12px;text-transform:uppercase;color:var(--gray);letter-spacing:0.5px;margin-bottom:10px;margin-top:16px;">Активности</div>`;
                html += `<div style="border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px;background:var(--bg);">`;
                actLog.forEach(a => {
                    html += `<div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; font-size:14px; ${a.done ? 'color:var(--gray);text-decoration:line-through;' : ''}">
                        <div style="width:14px;height:14px;border-radius:3px;border:1px solid ${a.done ? 'var(--success)' : 'var(--border)'};background:${a.done ? 'var(--success)' : 'transparent'};"></div>
                        <span>${a.text}</span>
                    </div>`;
                });
                html += `</div>`;
            }

            let phqLog = JSON.parse(localStorage.getItem('phqHistory') || '[]').filter(p => getDateKey(p.date) === key);
            let gadLog = JSON.parse(localStorage.getItem('gadHistory') || '[]').filter(g => getDateKey(g.date) === key);
            let tests = phqLog.map(p => ({ ...p, name: 'PHQ-9' })).concat(gadLog.map(g => ({ ...g, name: 'GAD-7' })));

            if (tests.length) {
                html += `<div style="font-size:12px;text-transform:uppercase;color:var(--gray);letter-spacing:0.5px;margin-bottom:10px;margin-top:16px;">Результаты тестов</div>`;
                tests.forEach(t => {
                    html += `<div style="border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px;background:var(--bg);">
                        <div style="font-weight:600;margin-bottom:4px;">${t.name}: ${t.score} баллов</div>
                        <div style="font-size:13px;color:var(--gray);">${t.level}</div>
                    </div>`;
                });
            }

            if (!html) {
                html = `<div style="color:var(--gray);text-align:center;padding:40px 0;">
                    <div style="font-size:32px;margin-bottom:12px;">📅</div>
                    <div>В этот день нет записей</div>
                </div>`;
            }

            document.getElementById('calDayContent').innerHTML = html;
        }

        function calPrev() {
            calMonth--;
            if (calMonth < 0) { calMonth = 11; calYear--; }
            renderCalendar();
        }
        function calNext() {
            calMonth++;
            if (calMonth > 11) { calMonth = 0; calYear++; }
            renderCalendar();
        }

        /* ── Dashboard ── */
        function openDashboard() {
            openModal('dashModal');
            renderDashboard();
            lucide.createIcons();
        }

        function renderDashboard() {
            let moodLog = JSON.parse(localStorage.getItem('moodLog') || '[]');
            let phqHist = JSON.parse(localStorage.getItem('phqHistory') || '[]');
            let gadHist = JSON.parse(localStorage.getItem('gadHistory') || '[]');
            let sl = JSON.parse(localStorage.getItem('sleepLog') || '[]');
            let acts = JSON.parse(localStorage.getItem('activities') || '[]');

            // Summary cards
            let avgMood = moodLog.length ? (moodLog.slice(-14).reduce((a, e) => a + e.score, 0) / Math.min(moodLog.length, 14)).toFixed(1) : '—';
            let avgSleep = sl.length ? (sl.slice(0, 7).reduce((a, e) => a + parseFloat(e.durHrs), 0) / Math.min(sl.length, 7)).toFixed(1) : '—';
            let doneActs = acts.filter(a => a.done).length;
            let lastPHQ = phqHist.length ? phqHist[phqHist.length - 1].score : '—';
            let lastGAD = gadHist.length ? gadHist[gadHist.length - 1].score : '—';
            let trackedDays = new Set(moodLog.map(e => e.date.slice(0, 10))).size;

            document.getElementById('dashCards').innerHTML = `
                <div class="dash-card" style="border-left: 3px solid var(--accent);">
                    <div class="dash-card-val">${avgMood}</div>
                    <div class="dash-card-label">Ср. настроение (14 д.)</div>
                </div>
                <div class="dash-card" style="border-left: 3px solid #5eba7d;">
                    <div class="dash-card-val">${avgSleep}${avgSleep !== '—' ? 'ч' : ''}</div>
                    <div class="dash-card-label">Ср. время сна</div>
                </div>
                <div class="dash-card" style="border-left: 3px solid #7b9cf5;">
                    <div class="dash-card-val">${doneActs}</div>
                    <div class="dash-card-label">Активностей выполнено</div>
                </div>
                <div class="dash-card" style="border-left: 3px solid var(--gray);">
                    <div class="dash-card-val">${trackedDays}</div>
                    <div class="dash-card-label">Дней отслеживания</div>
                </div>`;

            // Mood chart (last 14 days)
            let moodContainer = document.getElementById('dashMoodChart');
            if (moodLog.length >= 2) {
                moodContainer.innerHTML = '<canvas id="moodCanvas" style="width:100%;height:140px;"></canvas>';
                let ctx = document.getElementById('moodCanvas').getContext('2d');
                if (window.dashMoodChartInstance) window.dashMoodChartInstance.destroy();
                let last14 = moodLog.slice(-14);

                // Ensure chart.js is ready
                if (window.Chart) {
                    window.dashMoodChartInstance = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: last14.map(e => new Date(e.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })),
                            datasets: [{
                                label: 'Настроение (1-10)',
                                data: last14.map(e => e.score),
                                borderColor: '#a87b8d',
                                backgroundColor: 'rgba(168, 123, 141, 0.2)',
                                fill: true,
                                tension: 0.3,
                                pointBackgroundColor: '#a87b8d',
                                pointRadius: 4,
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    min: 0,
                                    max: 10,
                                    grid: { color: 'rgba(0,0,0,0.05)' }
                                },
                                x: {
                                    grid: { display: false }
                                }
                            },
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: {
                                        label: function (context) { return 'Настроение: ' + context.parsed.y + '/10'; }
                                    }
                                }
                            }
                        }
                    });
                }
            } else {
                moodContainer.innerHTML = '<div style="text-align:center;color:var(--gray);padding:40px 0;">Недостаточно данных. Запишите хотя бы 2 записи настроения.</div>';
            }

            // Sleep quality chart (last 7)
            let slContainer = document.getElementById('dashSleepChart');
            if (sl.length >= 2) {
                slContainer.innerHTML = '<canvas id="sleepCanvas" style="width:100%;height:140px;"></canvas>';
                let ctx = document.getElementById('sleepCanvas').getContext('2d');
                if (window.dashSleepChartInstance) window.dashSleepChartInstance.destroy();
                let last7 = sl.slice(0, 7).reverse();

                if (window.Chart) {
                    window.dashSleepChartInstance = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: last7.map(e => new Date(e.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })),
                            datasets: [{
                                label: 'Длительность сна (часы)',
                                data: last7.map(e => parseFloat(e.durHrs)),
                                backgroundColor: 'rgba(94, 186, 125, 0.7)',
                                borderRadius: 4,
                                order: 2
                            },
                            {
                                label: 'Качество (1-10)',
                                data: last7.map(e => e.qual),
                                type: 'line',
                                borderColor: '#d68f3a',
                                backgroundColor: '#d68f3a',
                                tension: 0.3,
                                borderWidth: 2,
                                fill: false,
                                pointRadius: 4,
                                order: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    min: 0,
                                    max: 12,
                                    grid: { color: 'rgba(0,0,0,0.05)' }
                                },
                                x: {
                                    grid: { display: false }
                                }
                            },
                            plugins: {
                                legend: { position: 'bottom', labels: { boxWidth: 12, usePointStyle: true } }
                            }
                        }
                    });
                }
            } else {
                slContainer.innerHTML = '<div style="text-align:center;color:var(--gray);padding:30px 0;">Нет данных о сне</div>';
            }

            // PHQ/GAD history
            let testHtml = '';
            if (phqHist.length) {
                let last = phqHist[phqHist.length - 1];
                let prev = phqHist.length > 1 ? phqHist[phqHist.length - 2].score : null;
                let trend = prev !== null ? (last.score < prev ? '↓ улучшение' : last.score > prev ? '↑ ухудшение' : '→ без изменений') : '';
                let col = last.score <= 4 ? '#5eba7d' : last.score <= 9 ? '#d68f3a' : '#df5858';
                testHtml += `<div style="display:flex;justify-content:space-between;align-items:center;padding:12px;border-radius:10px;border:1px solid var(--border);margin-bottom:8px;">
                    <div><div style="font-weight:600;margin-bottom:2px;">PHQ-9 (депрессия)</div><div style="font-size:12px;color:var(--gray);">${last.level} · ${new Date(last.date).toLocaleDateString('ru-RU')}</div></div>
                    <div style="text-align:right;"><div style="font-size:22px;font-weight:700;color:${col};">${last.score}<span style="font-size:13px;font-weight:400;color:var(--gray)">/27</span></div>
                    ${prev !== null ? `<div style="font-size:11px;color:${last.score < prev ? '#5eba7d' : '#df5858'}">${trend}</div>` : ''}</div></div>`;
            }
            if (gadHist.length) {
                let last = gadHist[gadHist.length - 1];
                let prev = gadHist.length > 1 ? gadHist[gadHist.length - 2].score : null;
                let trend = prev !== null ? (last.score < prev ? '↓ улучшение' : last.score > prev ? '↑ ухудшение' : '→ без изменений') : '';
                let col = last.score <= 4 ? '#5eba7d' : last.score <= 9 ? '#d68f3a' : '#df5858';
                testHtml += `<div style="display:flex;justify-content:space-between;align-items:center;padding:12px;border-radius:10px;border:1px solid var(--border);">
                    <div><div style="font-weight:600;margin-bottom:2px;">GAD-7 (тревога)</div><div style="font-size:12px;color:var(--gray);">${last.level} · ${new Date(last.date).toLocaleDateString('ru-RU')}</div></div>
                    <div style="text-align:right;"><div style="font-size:22px;font-weight:700;color:${col};">${last.score}<span style="font-size:13px;font-weight:400;color:var(--gray)">/21</span></div>
                    ${prev !== null ? `<div style="font-size:11px;color:${last.score < prev ? '#5eba7d' : '#df5858'}">${trend}</div>` : ''}</div></div>`;
            }
            if (!testHtml) testHtml = '<div style="color:var(--gray);font-size:13px;">Пройдите PHQ-9 или GAD-7, чтобы отслеживать динамику.</div>';
            document.getElementById('dashTests').innerHTML = testHtml;
        }