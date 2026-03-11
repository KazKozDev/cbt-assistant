const API = window.location.origin;

let sessionId = localStorage.getItem('SESSION_ID');
if (!sessionId) {
    sessionId = 'session_' + Date.now().toString(36);
    localStorage.setItem('SESSION_ID', sessionId);
}
const SESSION_ID = sessionId;
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
    let esteem = JSON.parse(localStorage.getItem('esteemHistory') || '[]').map(t => ({ ...t, name: 'Rosenberg' }));
    try {
        await fetch(API + '/api/sync/tests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: SESSION_ID, items: phq.concat(gad, esteem) })
        });
    } catch (e) { console.error('Failed to sync tests', e); }
}
