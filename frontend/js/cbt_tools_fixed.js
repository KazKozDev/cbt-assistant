1: const API = window.location.origin;
2:         const SESSION_ID = 'session_' + Date.now().toString(36);
3:         let isProc = false;
4: 
5:         async function syncData(endpoint, storageKey) {
6:             let items = JSON.parse(localStorage.getItem(storageKey) || '[]');
7:             try {
8:                 await fetch(API + endpoint, {
9:                     method: 'POST',
10:                     headers: { 'Content-Type': 'application/json' },
11:                     body: JSON.stringify({ session_id: SESSION_ID, items })
12:                 });
13:             } catch (e) { console.error('Failed to sync', storageKey, e); }
14:         }
15: 
16:         async function syncTests() {
17:             let phq = JSON.parse(localStorage.getItem('phqHistory') || '[]').map(t => ({ ...t, name: 'PHQ-9' }));
18:             let gad = JSON.parse(localStorage.getItem('gadHistory') || '[]').map(t => ({ ...t, name: 'GAD-7' }));
19:             try {
20:                 await fetch(API + '/api/sync/tests', {
21:                     method: 'POST',
22:                     headers: { 'Content-Type': 'application/json' },
23:                     body: JSON.stringify({ session_id: SESSION_ID, items: phq.concat(gad) })
24:                 });
25:             } catch (e) { console.error('Failed to sync tests', e); }
26:         }
27: 
28:         document.addEventListener('DOMContentLoaded', () => {
29:             lucide.createIcons();
30:             checkH();
31:             updateWelcomeMsg();
32:             const msgInp = document.getElementById('msgInput');
33:             msgInp.addEventListener('input', function () {
34:                 this.style.height = 'auto';
35:                 this.style.height = Math.min(this.scrollHeight, 120) + 'px';
36:             });
37:             syncData('/api/sync/sleep', 'sleepLog');
38:             syncData('/api/sync/activities', 'activities');
39:             syncTests();
40:         });
41: 
42:         function updateWelcomeMsg() {
43:             let h = new Date().getHours();
44:             let msg = 'Добрый день';
45:             if (h >= 5 && h < 12) { msg = 'Доброе утро'; }
46:             else if (h >= 18 && h < 23) { msg = 'Добрый вечер'; }
47:             else if (h >= 23 || h < 5) { msg = 'Доброй ночи'; }
48: 
49:             let welText = document.getElementById('welcomeText');
50:             if (welText) welText.innerText = msg;
51:         }
52: 
53:         async function checkH() {
54:             try {
55:                 let r = await fetch(API + '/api/health').then(r => r.json());
56:                 let d = document.getElementById('dotStatus');
57:                 let t = document.getElementById('txtStatus');
58:                 if (r.ollama_connected) {
59:                     d.className = 'status-dot online';
60:                     t.innerText = r.model;
61:                 }
62:                 else { d.className = 'status-dot'; t.innerText = 'Ollama offline'; }
63:             } catch (e) { document.getElementById('txtStatus').innerText = 'Бекенд недоступен'; }
64:         }
65: 
66:         function toggleSuggestMenu(id) {
67:             document.querySelectorAll('.suggest-dropdown.open').forEach(el => {
68:                 if (el.id !== id) el.classList.remove('open');
69:             });
70:             let el = document.getElementById(id);
71:             if (el) el.classList.toggle('open');
72:         }
73: 
74:         document.addEventListener('click', (e) => {
75:             if (!e.target.closest('.suggest-dropdown')) {
76:                 document.querySelectorAll('.suggest-dropdown.open').forEach(el => el.classList.remove('open'));
77:             }
78:         });
79: 
80:         function openModal(id) { document.getElementById(id).style.display = 'flex'; }
81:         function closeModal(id) {
82:             document.getElementById(id).style.display = 'none';
83:             if (id === 'sosModal') stopBreathing();
84:         }
85: 
86:         function sendQuick(txt) {
87:             document.getElementById('msgInput').value = txt;
88:             sendMessage();
89:         }
90: 
91:         async function sendMessage() {
92:             let inEl = document.getElementById('msgInput');
93:             let txt = inEl.value.trim();
94:             if (!txt || isProc) return;
95:             isProc = true;
96:             inEl.value = ''; inEl.style.height = 'auto';
97: 
98:             document.getElementById('welcome')?.remove();
99:             document.getElementById('mainContainer')?.classList.remove('empty-state');
100: 
101:             addMsg('user', txt);
102:             addMsg('assistant', '<i data-lucide="loader-2" style="width:20px; animation: spin 1.5s linear infinite; color: var(--gray);"></i>', 'loading');
103: 
104:             try {
105:                 let res = await fetch(API + '/api/chat', {
106:                     method: 'POST', headers: { 'Content-Type': 'application/json' },
107:                     body: JSON.stringify({ message: txt, session_id: SESSION_ID })
108:                 });
109:                 let data = await res.json();
110:                 document.getElementById('loading').remove();
111:                 addMsg('assistant', data.response);
112:                 if (ttsEnabled && window.speechSynthesis) {
113:                     window.speechSynthesis.cancel();
114:                     let cleanText = data.response.replace(/<[^>]+>/g, '').replace(/\*/g, '').substring(0, 1000); // strip markdown and keep reasonable length
115:                     let utterance = new SpeechSynthesisUtterance(cleanText);
116:                     utterance.lang = 'ru-RU';
117:                     window.speechSynthesis.speak(utterance);
118:                 }
119:             } catch (e) {
120:                 document.getElementById('loading').remove();
121:                 addMsg('assistant', '⚠️ Ошибка запроса к серверу.');
122:             }
123:             isProc = false;
124:         }
125: 
126:         function addMsg(role, content, id = '') {
127:             let list = document.getElementById('messages');
128:             let div = document.createElement('div');
129:             div.className = 'msg ' + role;
130:             if (id) div.id = id;
131: 
132:             // Clean representation
133:             let avatarIcon = role === 'user' ? 'user' : 'sparkles';
134:             let parsed = content.replace(/\n\n/g, '</p><p>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
135:             if (!parsed.startsWith('<p>') && parsed.indexOf('<') !== 0) {
136:                 parsed = '<p>' + parsed + '</p>';
137:             }
138: 
139:             div.innerHTML = `
140:             <div class="msg-avatar"><i data-lucide="${avatarIcon}" style="width:18px;"></i></div>
141:             <div class="msg-content">${parsed}</div>
142:         `;
143:             list.appendChild(div);
144:             lucide.createIcons();
145:             list.scrollTop = list.scrollHeight;
146:         }
147: 
148:         async function logMood() {
149:             let s = document.getElementById('moodSlider').value;
150:             let btn = event.target;
151:             btn.innerText = 'Записываем...';
152:             await fetch(API + '/api/mood', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ score: parseInt(s), session_id: SESSION_ID }) });
153:             // Save locally for dashboard
154:             let ml = JSON.parse(localStorage.getItem('moodLog') || '[]');
155:             ml.push({ score: parseInt(s), date: new Date().toISOString() });
156:             if (ml.length > 90) ml = ml.slice(-90);
157:             localStorage.setItem('moodLog', JSON.stringify(ml));
158:             btn.innerText = 'Записано ✓';
159:             setTimeout(() => btn.innerText = 'Записать состояние', 2000);
160:             document.getElementById('moodHistory').innerText = `Последняя запись: ${s}/10`;
161:         }
162: 
163:         async function submitThought(e) {
164:             e.preventDefault();
165:             let b = document.getElementById('tSub'); b.disabled = true; b.innerText = 'Сохраняем...';
166:             let d = {
167:                 session_id: SESSION_ID,
168:                 situation: document.getElementById('tSit').value,
169:                 thought: document.getElementById('tThou').value,
170:                 emotion: document.getElementById('tEmo').value,
171:                 intensity: parseInt(document.getElementById('tInt').value),
172:                 distortion: document.getElementById('tDist').value,
173:                 rational_response: document.getElementById('tRat').value
174:             };
175:             try {
176:                 await fetch(API + '/api/thoughts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) });
177:                 closeModal('thoughtModal');
178:                 document.getElementById('tForm').reset();
179:                 addMsg('assistant', 'Запись в дневник добавлена. Формулируя дальнейшие ответы, я учту вашу новую мысль.');
180:             } catch (err) { alert('Ошибка при сохранении.'); }
181:             b.disabled = false; b.innerText = 'Сохранить запись';
182:         }
183: 
184:         async function openThoughtHistoryModal() {
185:             openModal('histModal');
186:             let c = document.getElementById('histContent');
187:             c.innerHTML = '<div style="color:var(--gray); text-align:center;">Загрузка...</div>';
188:             try {
189:                 let res = await fetch(API + '/api/thoughts/' + SESSION_ID).then(r => r.json());
190:                 let recs = res.thought_records || [];
191:                 if (!recs.length) { c.innerHTML = '<div style="color:var(--gray); text-align:center;">Вы еще не добавили ни одной записи.</div>'; return; }
192:                 let h = '';
193:                 recs.reverse().forEach(r => {
194:                     let t = new Date(r.timestamp);
195:                     let tStr = t.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }) + ' в ' + t.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
196:                     h += `
197:                 <div class="timeline-item">
198:                     <div class="ti-time"><i data-lucide="clock" style="width:12px;"></i> ${tStr}</div>
199:                     <div class="ti-field"><strong>Ситуация</strong> ${r.situation}</div>
200:                     <div class="ti-field"><strong>Мысль</strong> ${r.thought}</div>
201:                     <div class="ti-field"><strong>Эмоция</strong> ${r.emotion} (${r.intensity}/10)</div>
202:                     <div class="ti-field"><strong>Рациональный ответ</strong> ${r.rational_response}</div>
203:                     <div class="ti-distortion"><i data-lucide="brain-circuit" style="width:12px;"></i> ${r.distortion}</div>
204:                 </div>`;
205:                 });
206:                 c.innerHTML = h;
207:                 lucide.createIcons();
208:             } catch (e) { c.innerHTML = '<div style="color:var(--danger); text-align:center;">Ошибка загрузки истории</div>'; }
209:         }
210: 
211:         /* Minimalist STT */
212:         let rec = null, isRec = false;
213:         if (window.SpeechRecognition || window.webkitSpeechRecognition) {
214:             let SR = window.SpeechRecognition || window.webkitSpeechRecognition;
215:             rec = new SR(); rec.lang = 'ru-RU'; rec.continuous = true; rec.interimResults = true;
216:             rec.onresult = (e) => {
217:                 let t = '';
218:                 for (let i = e.resultIndex; i < e.results.length; i++) t += e.results[i][0].transcript;
219:                 let inp = document.getElementById('msgInput');
220:                 inp.value = t;
221:                 inp.dispatchEvent(new Event('input')); // trigger resize
222:             };
223:             rec.onend = () => { if (isRec) try { rec.start() } catch (e) { } };
224:         }
225:         function toggleMic() {
226:             if (!rec) return;
227:             let btn = document.getElementById('micBtn');
228:             if (isRec) { isRec = false; btn.style.color = ''; rec.stop(); document.getElementById('msgInput').placeholder = 'Задайте вопрос...'; }
229:             else { isRec = true; btn.style.color = 'var(--accent)'; rec.start(); document.getElementById('msgInput').placeholder = 'Слушаю...'; }
230:         }
231: 
232:         let ttsEnabled = false;
233:         function toggleTTS() {
234:             ttsEnabled = !ttsEnabled;
235:             let btn = document.getElementById('ttsBtn');
236:             if (ttsEnabled) {
237:                 btn.style.color = 'var(--accent)';
238:                 btn.innerHTML = '<i data-lucide="volume-2" style="width:18px;"></i>';
239:                 // optional: play short sound indicating enablement
240:                 if (window.speechSynthesis) {
241:                     let ut = new SpeechSynthesisUtterance("Голос включен");
242:                     ut.lang = 'ru-RU';
243:                     window.speechSynthesis.speak(ut);
244:                 }
245:             } else {
246:                 btn.style.color = '';
247:                 btn.innerHTML = '<i data-lucide="volume-x" style="width:18px;"></i>';
248:                 if (window.speechSynthesis) window.speechSynthesis.cancel();
249:             }
250:             lucide.createIcons();
251:         }
252: 
253:         /* Breathing Exercise */
254:         let breatheInterval = null;
255:         let breatheState = 0; // 0=in, 1=hold, 2=out, 3=hold
256:         function toggleBreathing() {
257:             let btn = document.getElementById('btnBreathe');
258:             if (breatheInterval) {
259:                 stopBreathing();
260:                 return;
261:             }
262:             btn.innerText = 'Остановить упражнение';
263:             btn.style.background = 'var(--danger)';
264:             breatheState = 0;
265:             stepBreathe();
266:             breatheInterval = setInterval(stepBreathe, 4000);
267:         }
268: 
269:         function stopBreathing() {
270:             let btn = document.getElementById('btnBreathe');
271:             let circle = document.getElementById('breatheCircle');
272:             if (breatheInterval) clearInterval(breatheInterval);
273:             breatheInterval = null;
274:             if (btn) {
275:                 btn.innerText = 'Начать упражнение';
276:                 btn.style.background = '#a87b8d';
277:             }
278:             if (circle) {
279:                 circle.style.transform = 'scale(1)';
280:                 circle.style.background = 'var(--border)';
281:                 circle.style.color = 'var(--text)';
282:                 circle.innerText = 'Дыхание';
283:             }
284:         }
285: 
286:         function stepBreathe() {
287:             let circle = document.getElementById('breatheCircle');
288:             if (breatheState === 0) {
289:                 circle.innerText = 'Вдох...';
290:                 circle.style.transform = 'scale(1.5)';
291:                 circle.style.background = 'var(--accent-light)';
292:                 circle.style.color = 'var(--accent)';
293:             } else if (breatheState === 1) {
294:                 circle.innerText = 'Задержка';
295:             } else if (breatheState === 2) {
296:                 circle.innerText = 'Выдох...';
297:                 circle.style.transform = 'scale(1)';
298:                 circle.style.background = 'var(--border)';
299:                 circle.style.color = 'var(--text)';
300:             } else if (breatheState === 3) {
301:                 circle.innerText = 'Задержка';
302:             }
303:             breatheState = (breatheState + 1) % 4;
304:         }
305: 
306:         /* PHQ-9 */
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

function addActivityFromAI(txt) {
    if (!txt) return;
    activities.unshift({ text: txt + ' 🤖', done: false, date: new Date().toLocaleDateString('ru-RU'), isoDate: new Date().toISOString() });
    localStorage.setItem('activities', JSON.stringify(activities));
    syncData('/api/sync/activities', 'activities');
    renderActivities();
    // Notify UI
    let btnMessage = document.getElementById('messages');
    let div = document.createElement('div');
    div.className = 'msg assistant';
    div.innerHTML = `
        <div class="msg-avatar"><i data-lucide="sparkles" style="width:18px;"></i></div>
        <div class="msg-content"><p>✅ Я добавил(а) задачу в ваш <a href="#" onclick="openModal('actModal'); return false;" style="color:var(--accent);text-decoration:underline;">Планировщик</a>: <b>${txt}</b></p></div>
    `;
    if(btnMessage) {
        btnMessage.appendChild(div);
        lucide.createIcons();
        btnMessage.scrollTop = btnMessage.scrollHeight;
    }
}
window.addActivityFromAI = addActivityFromAI;

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
