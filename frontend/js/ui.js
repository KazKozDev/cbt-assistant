const UI_TRANSLATIONS = {
    ru: {
        document_title: 'КПТ Ассистент',
        app_title: 'КПТ Ассистент',
        sos_button: 'SOS',
        sidebar_thoughts: 'Дневник мыслей',
        sidebar_sleep: 'Журнал сна',
        sidebar_assessment: 'Самооценка',
        sidebar_calendar: 'Календарь записей',
        sidebar_dashboard: 'Дашборд прогресса',
        sidebar_articles: 'Библиотека статей',
        sidebar_videos: 'Видео-библиотека',
        sidebar_reminders: 'Напоминания',
        sidebar_settings: 'Настройки',
        sidebar_download: 'Скачать выписку',
        tts_title: 'Озвучка ассистента',
        mic_title: 'Голосовой ввод',
        status_connecting: 'Подключение...',
        status_offline: 'Ollama offline',
        status_backend_down: 'Бекенд недоступен',
        input_placeholder: 'Как я могу помочь вам сегодня?',
        input_placeholder_idle: 'Задайте вопрос...',
        input_placeholder_listening: 'Слушаю...',
        assistant_disclaimer: 'Ассистент может ошибаться. При остром состоянии обратитесь к специалисту.',
        welcome_morning: 'Доброе утро',
        welcome_day: 'Добрый день',
        welcome_evening: 'Добрый вечер',
        welcome_night: 'Доброй ночи',
        assessment_title: 'Самооценка',
        assessment_phq_title: 'Депрессия (PHQ-9)',
        assessment_phq_desc: 'Скрининг выраженности симптомов депрессии и снижения настроения',
        assessment_gad_title: 'Тревожность (GAD-7)',
        assessment_gad_desc: 'Оценка общего уровня тревоги и беспокойства',
        assessment_esteem_title: 'Самооценка (Розенберг)',
        assessment_esteem_desc: 'Оценка отношения к себе, самоуважения и внутренней опоры',
        mood_modal_title: 'Настроение',
        mood_log_button: 'Записать состояние',
        thought_modal_title: 'Мысли и действия',
        thought_tab_diary: 'Дневник мыслей',
        thought_tab_gratitude: 'Благодарность',
        thought_tab_rhythm: 'Ритм дня',
        thought_modal_hint: 'Запишите ситуацию, мысль и более бережный взгляд на неё.',
        thought_label_situation: 'Ситуация (Что произошло?)',
        thought_label_thought: 'Автоматическая мысль (О чем подумали?)',
        thought_label_emotion: 'Эмоция',
        thought_placeholder_emotion: 'Например: тревога',
        thought_label_intensity: 'Сила (0-10)',
        thought_label_distortion: 'Когнитивное искажение',
        distortion_catastrophizing: 'Катастрофизация',
        distortion_mind_reading: 'Чтение мыслей',
        distortion_fortune_telling: 'Предсказание будущего',
        distortion_overgeneralization: 'Сверхобобщение',
        distortion_black_white: 'Чёрно-белое мышление',
        distortion_discounting_positive: 'Обесценивание позитивного',
        distortion_personalization: 'Персонализация',
        distortion_unsure: 'Не знаю',
        thought_label_response: 'Рациональный ответ',
        gratitude_prompt: 'Запишите 3 вещи, за которые вы благодарны сегодня — большие или маленькие.',
        gratitude_label: 'За что я благодарен(а)?',
        gratitude_placeholder: '1. \n2. \n3. ',
        thought_save: 'Сохранить мысль',
        rhythm_mood_after: 'Как настроение после?',
        skip: 'Пропустить',
        phq_modal_title: 'PHQ-9 — Скрининг депрессии',
        phq_modal_desc: 'На протяжении последних двух недель, как часто вас беспокоили следующие проблемы?',
        gad_modal_title: 'GAD-7 — Скрининг тревожности',
        gad_modal_desc: 'За последние две недели, как часто вас беспокоили следующие проблемы?',
        esteem_modal_title: 'Самооценка — шкала Розенберга',
        esteem_modal_desc: 'Насколько вы согласны со следующими утверждениями о себе?',
        get_result: 'Получить результат',
        assessment_dashboard_title: 'Самооценка (PHQ-9 / GAD-7 / Розенберг)',
        calendar_legend_thoughts: 'Мысли',
        calendar_legend_mood: 'Настроение',
        calendar_legend_sleep: 'Сон',
        calendar_legend_activities: 'Активности',
        calendar_legend_assessment: 'Самооценка',
        calendar_pick_day: 'Выберите день',
        dashboard_title: 'Дашборд прогресса',
        dashboard_insights: 'Наблюдения',
        refresh: 'обновить',
        loading: 'Загрузка…',
        dashboard_mood_14: 'Настроение за последние 14 дней',
        dashboard_sleep_7: 'Качество сна (7 дней)',
        history_title: 'Дневник мыслей',
        new_entry: 'Новая запись',
        sleep_history_title: 'Журнал сна',
        sleep_add_title: 'Добавить запись о сне',
        sleep_bedtime: 'Лёг спать',
        sleep_wake: 'Встал',
        sleep_awake_count: 'Сколько раз просыпался за ночь',
        sleep_quality: 'Качество сна (0 — ужасно, 10 — отлично)',
        sleep_notes: 'Заметки (сны, причины плохого сна)',
        sleep_notes_placeholder: 'Что могло повлиять на сон?',
        save_entry: 'Сохранить запись',
        sos_title: 'Экстренная помощь (SOS)',
        sos_tab_breathing: 'Дыхание',
        sos_tab_grounding: 'Заземление',
        sos_tab_muscles: 'Мышцы',
        sos_tab_stop: 'СТОП',
        start_exercise: 'Начать упражнение',
        settings_title: 'Настройки',
        language_title: 'Язык',
        language_ru: 'Русский',
        language_en: 'English',
        tts_settings_title: 'Microsoft TTS',
        tts_voice_ru_label: 'Русский голос',
        tts_voice_en_label: 'English voice',
        tts_preview: 'Прослушать',
        reminders_title: 'Напоминания',
        reminders_desc: 'Браузерные уведомления напомнят записать настроение или практику. Страница должна быть открыта в браузере.',
        reminders_morning: 'Утреннее',
        reminders_evening: 'Вечернее',
        save: 'Сохранить',
        article_library_title: 'Библиотека статей',
        article_library_subtitle: 'Подборка статей о депрессии, КПТ и доказательных подходах к самопомощи.',
        video_library_title: 'Видео-библиотека',
        video_library_subtitle: 'Отобранные материалы от специалистов: механизмы депрессии, тревоги и полезные практики.',
        back_to_list: 'Назад к списку',
        download_title: 'Скачать выписку',
        download_desc: 'Выберите формат экспорта данных',
        download_pdf_desc: 'Красивый отчёт\nс графиками',
        download_txt_desc: 'Текстовый файл\nсо всеми данными',
        skip_arrow: 'Пропустить →',
        done_arrow: 'Готово →',
        breathe_phase: 'Дыхание',
        cycle_one: 'Цикл 1',
        follow_circle: 'Следуйте за кругом'
    },
    en: {
        document_title: 'CBT Assistant',
        app_title: 'CBT Assistant',
        sos_button: 'SOS',
        sidebar_thoughts: 'Thought Diary',
        sidebar_sleep: 'Sleep Journal',
        sidebar_assessment: 'Self-Assessment',
        sidebar_calendar: 'Records Calendar',
        sidebar_dashboard: 'Progress Dashboard',
        sidebar_articles: 'Article Library',
        sidebar_videos: 'Video Library',
        sidebar_reminders: 'Reminders',
        sidebar_settings: 'Settings',
        sidebar_download: 'Download Summary',
        tts_title: 'Assistant voice',
        mic_title: 'Voice input',
        status_connecting: 'Connecting...',
        status_offline: 'Ollama offline',
        status_backend_down: 'Backend unavailable',
        input_placeholder: 'How can I help you today?',
        input_placeholder_idle: 'Ask a question...',
        input_placeholder_listening: 'Listening...',
        assistant_disclaimer: 'The assistant may be mistaken. In an acute state, contact a professional.',
        welcome_morning: 'Good morning',
        welcome_day: 'Good afternoon',
        welcome_evening: 'Good evening',
        welcome_night: 'Good night',
        assessment_title: 'Self-Assessment',
        assessment_phq_title: 'Depression (PHQ-9)',
        assessment_phq_desc: 'Screening for depressive symptoms and lowered mood severity',
        assessment_gad_title: 'Anxiety (GAD-7)',
        assessment_gad_desc: 'Assessment of general anxiety and worry level',
        assessment_esteem_title: 'Self-Esteem (Rosenberg)',
        assessment_esteem_desc: 'Assessment of self-attitude, self-respect, and inner support',
        mood_modal_title: 'Mood',
        mood_log_button: 'Save mood',
        thought_modal_title: 'Thoughts and Actions',
        thought_tab_diary: 'Thought Diary',
        thought_tab_gratitude: 'Gratitude',
        thought_tab_rhythm: 'Daily Rhythm',
        thought_modal_hint: 'Write down the situation, the thought, and a gentler response to it.',
        thought_label_situation: 'Situation (What happened?)',
        thought_label_thought: 'Automatic thought (What went through your mind?)',
        thought_label_emotion: 'Emotion',
        thought_placeholder_emotion: 'For example: anxiety',
        thought_label_intensity: 'Intensity (0-10)',
        thought_label_distortion: 'Cognitive distortion',
        distortion_catastrophizing: 'Catastrophizing',
        distortion_mind_reading: 'Mind reading',
        distortion_fortune_telling: 'Fortune telling',
        distortion_overgeneralization: 'Overgeneralization',
        distortion_black_white: 'Black-and-white thinking',
        distortion_discounting_positive: 'Discounting the positive',
        distortion_personalization: 'Personalization',
        distortion_unsure: 'Not sure',
        thought_label_response: 'Balanced response',
        gratitude_prompt: 'Write down 3 things you feel grateful for today, big or small.',
        gratitude_label: 'What am I grateful for?',
        gratitude_placeholder: '1. \n2. \n3. ',
        thought_save: 'Save thought',
        rhythm_mood_after: 'How do you feel after it?',
        skip: 'Skip',
        phq_modal_title: 'PHQ-9 - Depression Screen',
        phq_modal_desc: 'Over the past two weeks, how often have you been bothered by the following problems?',
        gad_modal_title: 'GAD-7 - Anxiety Screen',
        gad_modal_desc: 'Over the past two weeks, how often have you been bothered by the following problems?',
        esteem_modal_title: 'Self-Esteem - Rosenberg Scale',
        esteem_modal_desc: 'How strongly do you agree with the following statements about yourself?',
        get_result: 'Get result',
        assessment_dashboard_title: 'Self-Assessment (PHQ-9 / GAD-7 / Rosenberg)',
        calendar_legend_thoughts: 'Thoughts',
        calendar_legend_mood: 'Mood',
        calendar_legend_sleep: 'Sleep',
        calendar_legend_activities: 'Activities',
        calendar_legend_assessment: 'Assessment',
        calendar_pick_day: 'Pick a day',
        dashboard_title: 'Progress Dashboard',
        dashboard_insights: 'Insights',
        refresh: 'refresh',
        loading: 'Loading…',
        dashboard_mood_14: 'Mood over the last 14 days',
        dashboard_sleep_7: 'Sleep quality (7 days)',
        history_title: 'Thought Diary',
        new_entry: 'New entry',
        sleep_history_title: 'Sleep Journal',
        sleep_add_title: 'Add sleep entry',
        sleep_bedtime: 'Went to bed',
        sleep_wake: 'Woke up',
        sleep_awake_count: 'How many times did you wake up at night',
        sleep_quality: 'Sleep quality (0 = awful, 10 = excellent)',
        sleep_notes: 'Notes (dreams, reasons for poor sleep)',
        sleep_notes_placeholder: 'What might have affected your sleep?',
        save_entry: 'Save entry',
        sos_title: 'Emergency Help (SOS)',
        sos_tab_breathing: 'Breathing',
        sos_tab_grounding: 'Grounding',
        sos_tab_muscles: 'Muscles',
        sos_tab_stop: 'STOP',
        start_exercise: 'Start exercise',
        settings_title: 'Settings',
        language_title: 'Language',
        language_ru: 'Russian',
        language_en: 'English',
        tts_settings_title: 'Microsoft TTS',
        tts_voice_ru_label: 'Russian voice',
        tts_voice_en_label: 'English voice',
        tts_preview: 'Preview',
        reminders_title: 'Reminders',
        reminders_desc: 'Browser notifications can remind you to log your mood or do a practice. Keep this page open in your browser.',
        reminders_morning: 'Morning',
        reminders_evening: 'Evening',
        save: 'Save',
        article_library_title: 'Article Library',
        article_library_subtitle: 'A curated collection about depression, CBT, and evidence-based self-help.',
        video_library_title: 'Video Library',
        video_library_subtitle: 'Selected materials from specialists on depression, anxiety, and useful practices.',
        back_to_list: 'Back to list',
        download_title: 'Download Summary',
        download_desc: 'Choose an export format',
        download_pdf_desc: 'Styled report\nwith charts',
        download_txt_desc: 'Plain text file\nwith all data',
        skip_arrow: 'Skip →',
        done_arrow: 'Done →',
        breathe_phase: 'Breathing',
        cycle_one: 'Cycle 1',
        follow_circle: 'Follow the circle'
    }
};

function getCurrentLanguage() {
    return localStorage.getItem('APP_LANG') || 'ru';
}
window.getCurrentLanguage = getCurrentLanguage;

function getCurrentLocale() {
    return getCurrentLanguage() === 'en' ? 'en-US' : 'ru-RU';
}
window.getCurrentLocale = getCurrentLocale;

function escapeInlineJsString(value) {
    return String(value).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}
window.escapeInlineJsString = escapeInlineJsString;

function t(key) {
    const lang = getCurrentLanguage();
    return (UI_TRANSLATIONS[lang] && UI_TRANSLATIONS[lang][key]) || UI_TRANSLATIONS.ru[key] || key;
}
window.t = t;

function updateLanguageButtons() {
    const lang = getCurrentLanguage();
    document.getElementById('settingsLangRu')?.classList.toggle('active', lang === 'ru');
    document.getElementById('settingsLangEn')?.classList.toggle('active', lang === 'en');
}

const TTS_VOICE_OPTIONS = {
    ru: [
        { value: 'ru-RU-SvetlanaNeural', label: 'Svetlana' },
        { value: 'ru-RU-DmitryNeural', label: 'Dmitry' }
    ],
    en: [
        { value: 'en-US-JennyNeural', label: 'Jenny' },
        { value: 'en-US-GuyNeural', label: 'Guy' }
    ]
};

function getTtsSettings() {
    const raw = JSON.parse(localStorage.getItem('ttsSettings') || '{}');
    return {
        ruVoice: raw.ruVoice || 'ru-RU-SvetlanaNeural',
        enVoice: raw.enVoice || 'en-US-JennyNeural'
    };
}

function getPreferredTtsVoice(language) {
    const settings = getTtsSettings();
    return language === 'en' ? settings.enVoice : settings.ruVoice;
}

function populateTtsVoiceControls() {
    const settings = getTtsSettings();
    [
        ['ttsVoiceRu', 'ru', settings.ruVoice],
        ['ttsVoiceEn', 'en', settings.enVoice]
    ].forEach(function ([id, lang, selected]) {
        const select = document.getElementById(id);
        if (!select) return;
        select.innerHTML = TTS_VOICE_OPTIONS[lang]
            .map(function (voice) {
                return '<option value="' + voice.value + '"' + (voice.value === selected ? ' selected' : '') + '>' + voice.label + '</option>';
            })
            .join('');
    });
}
window.populateTtsVoiceControls = populateTtsVoiceControls;

const QUICK_SUGGESTIONS = {
    ru: [
        {
            id: 'ddMood',
            icon: 'smile-plus',
            label: 'Настроение',
            items: [
                { type: 'mood', score: 10, icon: 'laugh', label: 'Отлично (10)' },
                { type: 'mood', score: 8, icon: 'smile', label: 'Хорошо (8)' },
                { type: 'mood', score: 5, icon: 'meh', label: 'Нормально (5)' },
                { type: 'mood', score: 3, icon: 'annoyed', label: 'Плохо (3)' },
                { type: 'mood', score: 1, icon: 'frown', label: 'Ужасно (1)' }
            ]
        },
        {
            id: 'ddSad',
            icon: 'frown',
            label: 'Грусть',
            items: [
                { text: 'Мне одиноко и тоскливо', label: 'Мне одиноко и тоскливо' },
                { text: 'Чувствую безысходность', label: 'Чувствую безысходность' },
                { text: 'Хочется плакать без причины', label: 'Хочется плакать без причины' },
                { text: 'Всё кажется бессмысленным', label: 'Всё кажется бессмысленным' },
                { text: 'Кажется, я в тупике', label: 'Кажется, я в тупике' }
            ]
        },
        {
            id: 'ddAnxious',
            icon: 'wind',
            label: 'Тревога',
            items: [
                { text: 'Я предчувствую что-то плохое', label: 'Предчувствую что-то плохое' },
                { text: 'Не могу перестать беспокоиться', label: 'Не могу перестать беспокоиться' },
                { text: 'У меня физические симптомы паники', label: 'Физические симптомы паники' },
                { text: 'Страх перед предстоящим событием', label: 'Страх перед событием' },
                { text: 'Много мыслей, не могу сосредоточиться', label: 'Много мыслей, не могу сосредоточиться' }
            ]
        },
        {
            id: 'ddAngry',
            icon: 'flame',
            label: 'Злость',
            items: [
                { text: 'Меня всё раздражает', label: 'Меня всё раздражает' },
                { text: 'Я злюсь на конкретного человека', label: 'Злюсь на конкретного человека' },
                { text: 'Не могу сдержать агрессию', label: 'Не могу сдержать агрессию' },
                { text: 'Чувствую несправедливость', label: 'Чувствую несправедливость' },
                { text: 'Сложно понять свои эмоции', label: 'Сложно понять свои эмоции' }
            ]
        },
        {
            id: 'ddTired',
            icon: 'battery-low',
            label: 'Усталость',
            items: [
                { text: 'Сил нет совсем, даже на простые дела', label: 'Сил нет совсем' },
                { text: 'Чувствую эмоциональное выгорание', label: 'Эмоциональное выгорание' },
                { text: 'Прокрастинирую и не могу начать', label: 'Прокрастинирую' },
                { text: 'Плохо сплю и не высыпаюсь', label: 'Плохо сплю' },
                { text: 'Не знаю, какое решение принять', label: 'Не знаю, какое решение принять' }
            ]
        },
        {
            id: 'ddCalm',
            icon: 'sun',
            label: 'Спокойствие',
            items: [
                { text: 'Сегодня отличный день!', label: 'Сегодня отличный день!' },
                { text: 'Удалось справиться с трудной задачей', label: 'Справился с трудной задачей' },
                { text: 'Хочу закрепить хорошее состояние', label: 'Закрепить хорошее состояние' },
                { text: 'Я благодарен за то, что сейчас имею', label: 'Чувствую благодарность' }
            ]
        }
    ],
    en: [
        {
            id: 'ddMood',
            icon: 'smile-plus',
            label: 'Mood',
            items: [
                { type: 'mood', score: 10, icon: 'laugh', label: 'Excellent (10)' },
                { type: 'mood', score: 8, icon: 'smile', label: 'Good (8)' },
                { type: 'mood', score: 5, icon: 'meh', label: 'Okay (5)' },
                { type: 'mood', score: 3, icon: 'annoyed', label: 'Bad (3)' },
                { type: 'mood', score: 1, icon: 'frown', label: 'Awful (1)' }
            ]
        },
        {
            id: 'ddSad',
            icon: 'frown',
            label: 'Sadness',
            items: [
                { text: 'I feel lonely and low', label: 'I feel lonely and low' },
                { text: 'I feel hopeless', label: 'I feel hopeless' },
                { text: 'I want to cry for no clear reason', label: 'I want to cry for no clear reason' },
                { text: 'Everything feels meaningless', label: 'Everything feels meaningless' },
                { text: 'I feel stuck', label: 'I feel stuck' }
            ]
        },
        {
            id: 'ddAnxious',
            icon: 'wind',
            label: 'Anxiety',
            items: [
                { text: 'I feel like something bad is about to happen', label: 'Something bad feels close' },
                { text: 'I cannot stop worrying', label: 'I cannot stop worrying' },
                { text: 'I have physical panic symptoms', label: 'Physical panic symptoms' },
                { text: 'I feel afraid of an upcoming event', label: 'Fear of an upcoming event' },
                { text: 'My mind is racing and I cannot focus', label: 'Too many thoughts to focus' }
            ]
        },
        {
            id: 'ddAngry',
            icon: 'flame',
            label: 'Anger',
            items: [
                { text: 'Everything irritates me right now', label: 'Everything irritates me' },
                { text: 'I am angry at a specific person', label: 'I am angry at someone' },
                { text: 'I cannot hold back my aggression', label: 'I cannot hold back my aggression' },
                { text: 'Something feels unfair', label: 'Something feels unfair' },
                { text: 'It is hard to understand my emotions', label: 'I cannot sort out my emotions' }
            ]
        },
        {
            id: 'ddTired',
            icon: 'battery-low',
            label: 'Fatigue',
            items: [
                { text: 'I have no energy even for simple tasks', label: 'No energy at all' },
                { text: 'I feel emotionally burned out', label: 'Emotional burnout' },
                { text: 'I keep procrastinating and cannot start', label: 'I keep procrastinating' },
                { text: 'I sleep badly and never feel rested', label: 'I sleep badly' },
                { text: 'I do not know what decision to make', label: 'I cannot decide what to do' }
            ]
        },
        {
            id: 'ddCalm',
            icon: 'sun',
            label: 'Calm',
            items: [
                { text: 'Today feels like a really good day', label: 'Today is a good day' },
                { text: 'I managed to handle a difficult task', label: 'I handled a difficult task' },
                { text: 'I want to reinforce this good state', label: 'I want to reinforce this state' },
                { text: 'I feel grateful for what I have right now', label: 'I feel grateful' }
            ]
        }
    ]
};

function renderQuickSuggestions() {
    const wrap = document.getElementById('quickSuggestions');
    if (!wrap) return;
    const lang = getCurrentLanguage();
    const groups = QUICK_SUGGESTIONS[lang] || QUICK_SUGGESTIONS.ru;
    wrap.innerHTML = groups.map((group) => {
        const items = group.items.map((item) => {
            if (item.type === 'mood') {
                return `<button class="suggest-item" onclick="logMoodFromWelcome(${item.score}); toggleSuggestMenu('${group.id}')"><i data-lucide="${item.icon}" style="width:14px; vertical-align:middle; margin-right:6px;"></i>${item.label}</button>`;
            }
            return `<button class="suggest-item" onclick="sendQuick('${escapeInlineJsString(item.text)}'); toggleSuggestMenu('${group.id}')">${item.label}</button>`;
        }).join('');
        return `
            <div class="suggest-dropdown" id="${group.id}">
                <button class="suggest-btn" onclick="toggleSuggestMenu('${group.id}')"><i data-lucide="${group.icon}" style="width:14px;color:var(--gray)"></i> ${group.label}</button>
                <div class="suggest-menu">${items}</div>
            </div>
        `;
    }).join('');
    if (window.lucide) lucide.createIcons();
}

function localizeStaticUi() {
    document.title = t('document_title');
    renderQuickSuggestions();
    refreshLocalizedExercises();
    if (document.getElementById('articleModal')?.style.display === 'flex') {
        if (document.getElementById('articleReaderContainer')?.style.display === 'block' && typeof window._articleReaderIndex === 'number') {
            openArticleReader(window._articleReaderIndex);
        } else {
            renderArticleList();
        }
    }
    if (document.getElementById('videoModal')?.style.display === 'flex' && document.getElementById('videoListContainer')?.style.display !== 'none') {
        renderVideoList();
    }
}

function applyTranslations() {
    document.documentElement.lang = getCurrentLanguage();
    localizeStaticUi();
    document.querySelectorAll('[data-i18n]').forEach((el) => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
        el.setAttribute('placeholder', t(el.dataset.i18nPlaceholder));
    });
    document.querySelectorAll('[data-i18n-title]').forEach((el) => {
        el.setAttribute('title', t(el.dataset.i18nTitle));
    });
    document.querySelectorAll('[data-i18n-html]').forEach((el) => {
        el.innerHTML = t(el.dataset.i18nHtml).replace(/\n/g, '<br>');
    });
    updateLanguageButtons();
    if (rec) rec.lang = getCurrentLanguage() === 'en' ? 'en-US' : 'ru-RU';
    updateWelcomeMsg();
    if (typeof window.refreshLocalizedTests === 'function') window.refreshLocalizedTests();
    if (typeof window.refreshLocalizedCBT === 'function') window.refreshLocalizedCBT();
    if (typeof checkH === 'function') checkH();
}
window.applyTranslations = applyTranslations;

function setLanguage(lang) {
    localStorage.setItem('APP_LANG', lang);
    applyTranslations();
}
window.setLanguage = setLanguage;

function updateWelcomeMsg() {
    let h = new Date().getHours();
    let msg = t('welcome_day');
    if (h >= 5 && h < 12) { msg = t('welcome_morning'); }
    else if (h >= 18 && h < 23) { msg = t('welcome_evening'); }
    else if (h >= 23 || h < 5) { msg = t('welcome_night'); }

    let welText = document.getElementById('welcomeText');
    if (welText) welText.innerText = msg + ', Artem';
}

async function checkH() {
    try {
        let r = await fetch(API + '/api/health').then(r => r.json());
        let d = document.getElementById('dotStatus');
        let statusEl = document.getElementById('txtStatus');
        if (r.ollama_connected) {
            d.className = 'status-dot online';
            statusEl.innerText = r.model;
        }
        else { d.className = 'status-dot'; statusEl.innerText = t('status_offline'); }
    } catch (e) { document.getElementById('txtStatus').innerText = t('status_backend_down'); }
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

function openModal(id) {
    document.getElementById(id).style.display = 'flex';
    if (id === 'thoughtModal' && typeof window.renderActivities === 'function') {
        window.renderActivities();
    }
    if (window.lucide) lucide.createIcons();
    if (id === 'sosModal') { loadSosPlan(); if (window.switchSos) switchSos(0); }
}
function closeModal(id) {
    document.getElementById(id).style.display = 'none';
    if (id === 'sosModal') stopBreathing();
    if (id === 'thoughtModal' && typeof window.resetThoughtEditor === 'function') window.resetThoughtEditor();
    if (id === 'sleepModal' && typeof window.resetSleepEditor === 'function') window.resetSleepEditor();
}

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
    if (isRec) { isRec = false; btn.style.color = ''; rec.stop(); document.getElementById('msgInput').placeholder = t('input_placeholder_idle'); }
    else { isRec = true; btn.style.color = 'var(--accent)'; rec.start(); document.getElementById('msgInput').placeholder = t('input_placeholder_listening'); }
}

let ttsEnabled = false;
let ttsAudio = null;
let ttsRequestController = null;

function stopTTSPlayback() {
    if (ttsRequestController) {
        ttsRequestController.abort();
        ttsRequestController = null;
    }
    if (ttsAudio) {
        ttsAudio.pause();
        if (ttsAudio.dataset.objectUrl) {
            URL.revokeObjectURL(ttsAudio.dataset.objectUrl);
        }
        ttsAudio = null;
    }
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}
window.stopTTSPlayback = stopTTSPlayback;

async function playAssistantSpeech(text, language) {
    const lang = language || getCurrentLanguage();
    const cleanText = (text || '')
        .replace(/<[^>]+>/g, ' ')
        .replace(/\*/g, '')
        .replace(/\s+/g, ' ')
        .trim()
        .slice(0, 1000);

    if (!cleanText) return;

    stopTTSPlayback();
    ttsRequestController = new AbortController();

    try {
        const res = await fetch(API + '/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: cleanText,
                language: lang,
                voice: getPreferredTtsVoice(lang)
            }),
            signal: ttsRequestController.signal
        });
        if (!res.ok) throw new Error('TTS request failed');

        const blob = await res.blob();
        if (ttsRequestController.signal.aborted) return;

        const objectUrl = URL.createObjectURL(blob);
        const audio = new Audio(objectUrl);
        audio.dataset.objectUrl = objectUrl;
        audio.onended = () => {
            URL.revokeObjectURL(objectUrl);
            if (ttsAudio === audio) ttsAudio = null;
        };
        audio.onerror = () => {
            URL.revokeObjectURL(objectUrl);
            if (ttsAudio === audio) ttsAudio = null;
        };

        ttsAudio = audio;
        await audio.play();
    } catch (err) {
        if (err.name !== 'AbortError') {
            console.error('Microsoft TTS playback failed', err);
        }
    } finally {
        ttsRequestController = null;
    }
}
window.playAssistantSpeech = playAssistantSpeech;

async function previewTtsVoice(language) {
    const isEnglish = language === 'en';
    const text = isEnglish
        ? 'This is how the selected Microsoft voice sounds.'
        : 'Так звучит выбранный голос Microsoft.';
    const select = document.getElementById(isEnglish ? 'ttsVoiceEn' : 'ttsVoiceRu');
    const voice = select ? select.value : getPreferredTtsVoice(language);
    stopTTSPlayback();
    ttsRequestController = new AbortController();

    try {
        const res = await fetch(API + '/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language, voice }),
            signal: ttsRequestController.signal
        });
        if (!res.ok) throw new Error('TTS preview request failed');
        const blob = await res.blob();
        if (ttsRequestController.signal.aborted) return;

        const objectUrl = URL.createObjectURL(blob);
        const audio = new Audio(objectUrl);
        audio.dataset.objectUrl = objectUrl;
        audio.onended = () => {
            URL.revokeObjectURL(objectUrl);
            if (ttsAudio === audio) ttsAudio = null;
        };
        audio.onerror = () => {
            URL.revokeObjectURL(objectUrl);
            if (ttsAudio === audio) ttsAudio = null;
        };
        ttsAudio = audio;
        await audio.play();
    } catch (err) {
        if (err.name !== 'AbortError') console.error('Microsoft TTS preview failed', err);
    } finally {
        ttsRequestController = null;
    }
}
window.previewTtsVoice = previewTtsVoice;

function toggleTTS() {
    ttsEnabled = !ttsEnabled;
    let btn = document.getElementById('ttsBtn');
    if (ttsEnabled) {
        btn.style.color = 'var(--accent)';
        btn.innerHTML = '<i data-lucide="volume-2" style="width:18px;"></i>';
        playAssistantSpeech(getCurrentLanguage() === 'en' ? 'Voice on' : 'Голос включен', getCurrentLanguage());
    } else {
        btn.style.color = '';
        btn.innerHTML = '<i data-lucide="volume-x" style="width:18px;"></i>';
        stopTTSPlayback();
    }
    lucide.createIcons();
}

function getLocalizedUiContent() {
    const lang = getCurrentLanguage();
    return {
        ru: {
            sosHints: [
                'Паника, учащённое сердцебиение — быстро снижает пульс',
                '',
                '',
                ''
            ],
            breathingPane: {
                title: 'Дыхательные практики',
                desc: 'Выберите ритм дыхания, который лучше всего подходит вашему состоянию прямо сейчас.'
            },
            breatheTypes: [
                {
                    desc: 'Снижает пульс и останавливает панику.',
                    bgImage: 'img/bg/forest.png',
                    cardTitle: 'Квадрат 4-4-4-4',
                    cardDesc: 'Снижает пульс, останавливает панику',
                    steps: [
                        { text: 'Вдох...', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Задержка', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Выдох...', dur: 4000, scale: '1', bg: 'var(--border)', color: 'var(--text)' },
                        { text: 'Задержка', dur: 4000, scale: '1', bg: 'var(--border)', color: 'var(--text)' }
                    ]
                },
                {
                    desc: 'Техника для снижения тревоги и быстрого засыпания.',
                    bgImage: 'img/bg/stars.png',
                    cardTitle: '4-7-8',
                    cardDesc: 'Снижает тревогу, помогает заснуть',
                    steps: [
                        { text: 'Вдох...', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Задержка...', dur: 7000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Выдох...', dur: 8000, scale: '1', bg: 'var(--border)', color: 'var(--text)' }
                    ]
                },
                {
                    desc: 'Выдох длиннее вдоха — включает парасимпатическую нервную систему.',
                    bgImage: 'img/bg/ocean.png',
                    cardTitle: 'Успокаивающее 4-6',
                    cardDesc: 'Включает парасимпатическую систему',
                    steps: [
                        { text: 'Вдох...', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Выдох...', dur: 6000, scale: '1', bg: 'var(--border)', color: 'var(--text)' }
                    ]
                }
            ],
            breatheTips: [
                'Дышите через нос для максимального эффекта',
                'Сфокусируйтесь на ощущениях в теле',
                'Представьте, как напряжение покидает вас с выдохом',
                'Закройте глаза для более глубокого расслабления',
                'Каждый цикл снижает уровень кортизола',
                'Не торопитесь — ваш ритм идеален',
                'Медленное дыхание активирует блуждающий нерв',
                'Вы делаете важное для своего здоровья'
            ],
            groundingPane: {
                title: 'Заземление 5-4-3-2-1',
                desc: 'Пошаговая техника — помогает вернуться в «здесь и сейчас» при тревоге или панике.',
                items: ['Вещей, которые вы видите', 'Предмета, которых касаетесь', 'Звука, которые слышите', 'Запаха, которые чувствуете', 'Хорошая вещь о себе']
            },
            pmrPane: {
                title: 'Мышечная релаксация',
                desc: 'Напрягайте и расслабляйте группы мышц — снижает физическое напряжение и тревогу.',
                items: ['Лицо — сожмите и расслабьте', 'Плечи и шея', 'Руки и кисти', 'Живот и грудь', 'Ноги и стопы']
            },
            stopPane: {
                title: 'Техника СТОП',
                desc: 'Быстрый 4-шаговый алгоритм — останавливает спираль тревожных мыслей.',
                items: ['Стоп — остановитесь', 'Тело — сделайте глубокий вдох', 'Осмотрись — наблюдайте без оценки', 'Продолжай — действуйте осознанно']
            },
            groundSteps: [
                { num: '5', sense: 'Зрение', text: 'Назовите 5 вещей, которые вы видите вокруг' },
                { num: '4', sense: 'Осязание', text: 'Дотроньтесь до 4 предметов рядом с вами' },
                { num: '3', sense: 'Слух', text: 'Услышьте 3 звука прямо сейчас' },
                { num: '2', sense: 'Обоняние', text: 'Почувствуйте 2 запаха или вспомните их' },
                { num: '1', sense: 'Вы сами', text: 'Назовите 1 хорошую вещь о себе' }
            ],
            groundDone: { sense: 'Готово', text: 'Вы вернулись в «здесь и сейчас». Молодец!', button: 'Закрыть' },
            pmrSteps: [
                { num: '1', muscle: 'Лицо', tenseText: 'Сожмите лицо: зажмурьтесь, нахмурьтесь, сожмите челюсть', relaxText: 'Медленно расслабьте все мышцы лица… почувствуйте тепло' },
                { num: '2', muscle: 'Плечи и шея', tenseText: 'Поднимите плечи к ушам, напрягите шею', relaxText: 'Опустите плечи… почувствуйте как уходит напряжение' },
                { num: '3', muscle: 'Руки и кисти', tenseText: 'Сожмите кулаки и напрягите предплечья', relaxText: 'Разожмите кулаки… расправьте пальцы' },
                { num: '4', muscle: 'Живот и грудь', tenseText: 'Напрягите пресс и грудь, как будто ждёте удар', relaxText: 'Расслабьте живот… дышите свободно' },
                { num: '5', muscle: 'Ноги и стопы', tenseText: 'Вытяните ноги, напрягите бёдра и икры', relaxText: 'Расслабьте ноги… почувствуйте тяжесть и тепло' }
            ],
            pmrPhaseTense: 'Напрягите',
            pmrPhaseRelax: 'Расслабьте',
            pmrDone: 'Готово',
            pmrDoneText: 'Всё тело расслаблено. Молодец!',
            pmrClose: 'Закрыть',
            stopSteps: [
                { letter: 'С', word: 'Стоп', text: 'Скажите себе «Стоп». Мысленно или вслух. Остановите поток мыслей.' },
                { letter: 'Т', word: 'Тело', text: 'Сделайте глубокий вдох через нос на 4 счёта. Медленный выдох через рот на 6.' },
                { letter: 'О', word: 'Осмотрись', text: 'Наблюдайте свои мысли и ощущения со стороны — без оценки и критики.' },
                { letter: 'П', word: 'Продолжай', text: 'Теперь действуйте осознанно. Что важно прямо сейчас?' }
            ],
            stopDone: { word: 'Готово', text: 'Вы вернули контроль. Действуйте осознанно!', button: 'Закрыть' },
            notifications: {
                title: 'КПТ Ассистент',
                morning: '🌅 Доброе утро! Как вы себя чувствуете? Запишите настроение.',
                evening: '🌙 Добрый вечер! Время записать благодарность или мысли дня.'
            },
            aiBreathingStarted: '🌬️ Я запустил(а) для вас Дыхательную практику. Следуйте инструкциям на экране.'
        },
        en: {
            sosHints: [
                '',
                '',
                '',
                ''
            ],
            breathingPane: {
                title: 'Breathing practices',
                desc: 'Choose the breathing rhythm that best matches you.'
            },
            breatheTypes: [
                {
                    desc: 'Helps slow your pulse and interrupt panic.',
                    bgImage: 'img/bg/forest.png',
                    cardTitle: 'Box 4-4-4-4',
                    cardDesc: 'Slows the pulse and interrupts panic',
                    steps: [
                        { text: 'Inhale...', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Hold', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Exhale...', dur: 4000, scale: '1', bg: 'var(--border)', color: 'var(--text)' },
                        { text: 'Hold', dur: 4000, scale: '1', bg: 'var(--border)', color: 'var(--text)' }
                    ]
                },
                {
                    desc: 'A technique for lowering anxiety and falling asleep faster.',
                    bgImage: 'img/bg/stars.png',
                    cardTitle: '4-7-8',
                    cardDesc: 'Reduces anxiety and helps you fall asleep',
                    steps: [
                        { text: 'Inhale...', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Hold...', dur: 7000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Exhale...', dur: 8000, scale: '1', bg: 'var(--border)', color: 'var(--text)' }
                    ]
                },
                {
                    desc: 'A longer exhale activates the parasympathetic nervous system.',
                    bgImage: 'img/bg/ocean.png',
                    cardTitle: 'Soothing 4-6',
                    cardDesc: 'Activates the parasympathetic system',
                    steps: [
                        { text: 'Inhale...', dur: 4000, scale: '1.5', bg: 'var(--accent-light)', color: 'var(--accent)' },
                        { text: 'Exhale...', dur: 6000, scale: '1', bg: 'var(--border)', color: 'var(--text)' }
                    ]
                }
            ],
            breatheTips: [
                'Breathe through your nose for the strongest effect',
                'Focus on what you feel in your body',
                'Imagine tension leaving with every exhale',
                'Close your eyes if that helps you relax',
                'Each cycle helps lower stress hormones',
                'No need to rush, this pace is enough',
                'Slow breathing activates the vagus nerve',
                'You are doing something important for your health'
            ],
            groundingPane: {
                title: 'Grounding 5-4-3-2-1',
                desc: 'A technique to ground you in the present during anxiety or panic.',
                items: ['Things you can see', 'Objects you can touch', 'Sounds you can hear', 'Scents you can notice', 'One good thing about yourself']
            },
            pmrPane: {
                title: 'Progressive Muscle Relaxation',
                desc: 'Tense and release muscles to ease tension and anxiety.',
                items: ['Face - tense and release', 'Shoulders and neck', 'Arms and hands', 'Stomach and chest', 'Legs and feet']
            },
            stopPane: {
                title: 'STOP Technique',
                desc: 'A fast 4-step method that interrupts the spiral of anxious thoughts.',
                items: ['Stop - pause', 'Take a breath - breathe deeply', 'Observe - notice without judging', 'Proceed - act with intention']
            },
            groundSteps: [
                { num: '5', sense: 'Sight', text: 'Name 5 things you can see around you' },
                { num: '4', sense: 'Touch', text: 'Touch 4 objects near you' },
                { num: '3', sense: 'Hearing', text: 'Notice 3 sounds right now' },
                { num: '2', sense: 'Smell', text: 'Notice 2 smells or remember them' },
                { num: '1', sense: 'You', text: 'Name 1 good thing about yourself' }
            ],
            groundDone: { sense: 'Done', text: 'You are back in the here and now. Well done.', button: 'Close' },
            pmrSteps: [
                { num: '1', muscle: 'Face', tenseText: 'Tense your face: squeeze your eyes shut, frown, clench your jaw', relaxText: 'Slowly relax all the muscles in your face and notice the warmth' },
                { num: '2', muscle: 'Shoulders and neck', tenseText: 'Lift your shoulders to your ears and tense your neck', relaxText: 'Drop your shoulders and feel the tension leave' },
                { num: '3', muscle: 'Arms and hands', tenseText: 'Clench your fists and tense your forearms', relaxText: 'Unclench your fists and open your fingers' },
                { num: '4', muscle: 'Stomach and chest', tenseText: 'Tense your abdomen and chest as if bracing for impact', relaxText: 'Relax your stomach and breathe freely' },
                { num: '5', muscle: 'Legs and feet', tenseText: 'Stretch your legs and tense your thighs and calves', relaxText: 'Relax your legs and notice heaviness and warmth' }
            ],
            pmrPhaseTense: 'Tense',
            pmrPhaseRelax: 'Release',
            pmrDone: 'Done',
            pmrDoneText: 'Your whole body is more relaxed now. Well done.',
            pmrClose: 'Close',
            stopSteps: [
                { letter: 'S', word: 'Stop', text: 'Tell yourself “Stop,” silently or out loud. Interrupt the stream of thoughts.' },
                { letter: 'T', word: 'Take a breath', text: 'Take a deep breath in through the nose for 4 counts, then exhale through the mouth for 6.' },
                { letter: 'O', word: 'Observe', text: 'Notice your thoughts and sensations from a small distance, without judging them.' },
                { letter: 'P', word: 'Proceed', text: 'Now act intentionally. What matters most right now?' }
            ],
            stopDone: { word: 'Done', text: 'You have regained control. Move forward with intention.', button: 'Close' },
            notifications: {
                title: 'CBT Assistant',
                morning: '🌅 Good morning. How are you feeling? Log your mood.',
                evening: '🌙 Good evening. It may be a good time to record gratitude or thoughts from the day.'
            },
            aiBreathingStarted: '🌬️ I started a breathing practice for you. Follow the instructions on the screen.'
        }
    }[lang] || null;
}

sosHints = window.sosHints || [];
let BREATHE_TYPES = [];
let BREATHE_TIPS = [];
let GROUND_STEPS = [];
let PMR_STEPS = [];
let STOP_STEPS = [];

function refreshLocalizedExercises() {
    const content = getLocalizedUiContent();
    if (!content) return;
    sosHints = content.sosHints.slice();
    BREATHE_TYPES = content.breatheTypes.map((item) => ({ ...item, steps: item.steps.map((step) => ({ ...step })) }));
    BREATHE_TIPS = content.breatheTips.slice();
    GROUND_STEPS = content.groundSteps.map((step) => ({ ...step }));
    PMR_STEPS = content.pmrSteps.map((step) => ({ ...step }));
    STOP_STEPS = content.stopSteps.map((step) => ({ ...step }));

    const sosHint = document.getElementById('sosHint');
    if (sosHint && document.getElementById('sosPane0')?.style.display !== 'none') {
        sosHint.textContent = sosHints[0] || '';
    }

    const breatheButtons = document.querySelectorAll('#breatheTypes .breathe-option');
    BREATHE_TYPES.forEach((type, idx) => {
        const btn = breatheButtons[idx];
        if (!btn) return;
        const icon = btn.querySelector('span');
        const contentWrap = btn.querySelectorAll('span')[1];
        if (contentWrap) {
            contentWrap.innerHTML = `${type.cardTitle}<br><span style="font-weight:400; font-size:11px;">${type.cardDesc}</span>`;
        }
    });

    const ids = [
        ['breathePaneTitle', content.breathingPane.title],
        ['breathePaneDesc', content.breathingPane.desc],
        ['groundPaneTitle', content.groundingPane.title],
        ['groundPaneDesc', content.groundingPane.desc],
        ['pmrPaneTitle', content.pmrPane.title],
        ['pmrPaneDesc', content.pmrPane.desc],
        ['stopPaneTitle', content.stopPane.title],
        ['stopPaneDesc', content.stopPane.desc],
        ['groundSense', GROUND_STEPS[groundStepIdx]?.sense || GROUND_STEPS[0]?.sense || ''],
        ['groundInstruction', GROUND_STEPS[groundStepIdx]?.text || GROUND_STEPS[0]?.text || ''],
        ['pmrMuscle', PMR_STEPS[pmrStepIdx]?.muscle || PMR_STEPS[0]?.muscle || ''],
        ['stopWord', STOP_STEPS[stopStepIdx]?.word || STOP_STEPS[0]?.word || ''],
        ['stopInstruction', STOP_STEPS[stopStepIdx]?.text || STOP_STEPS[0]?.text || '']
    ];
    ids.forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el && value) el.textContent = value;
    });

    content.groundingPane.items.forEach((text, idx) => {
        const el = document.getElementById(`groundPaneItem${idx}`);
        if (el) el.textContent = text;
    });
    content.pmrPane.items.forEach((text, idx) => {
        const el = document.getElementById(`pmrPaneItem${idx}`);
        if (el) el.textContent = text;
    });
    content.stopPane.items.forEach((text, idx) => {
        const el = document.getElementById(`stopPaneItem${idx}`);
        if (el) el.textContent = text;
    });
    STOP_STEPS.forEach((step, idx) => {
        const el = document.getElementById(`stopPaneLetter${idx}`);
        if (el) el.textContent = step.letter;
    });
}

/* === SOS Tabs === */
function switchSosTab(n) {
    const tb = document.getElementById('sosTabBody');
    if (tb) tb.setAttribute('data-tab', String(n));
    if (n !== 0) stopBreathing();
}
window.switchSosTab = switchSosTab;
let breatheTimer = null;
let breatheStepIdx = 0;
let breatheTypeIdx = 0;

function setBreatheType(idx) {
    stopBreathing();
    breatheTypeIdx = idx;
}
window.setBreatheType = setBreatheType;

function openBreatheScreen() {
    console.log('openBreatheScreen called');
    var overlay = document.getElementById('breatheOverlay');
    if (!overlay) { console.error('breatheOverlay not found!'); return; }

    // Set background image based on selected type
    const type = BREATHE_TYPES[breatheTypeIdx];
    overlay.style.backgroundImage = 'linear-gradient(to bottom, rgba(5,5,16,0.6) 0%, rgba(5,5,16,0.85) 100%), url(' + type.bgImage + ')';

    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    // Reset visuals
    var phase = document.getElementById('breathePhase');
    var timer = document.getElementById('breatheTimer');
    var flower = document.getElementById('breatheFlower');
    var glow = document.querySelector('.breathe-bg-glow');
    var cycleEl = document.getElementById('breatheCycleCount');
    var tipEl = document.getElementById('breatheTip');
    if (phase) phase.innerText = t('breathe_phase');
    if (timer) timer.innerText = '';
    if (flower) {
        flower.className = 'breathe-portal';
        flower.style.transitionDuration = '0.5s'; // reset quickly
    }
    if (glow) {
        glow.className = 'breathe-bg-glow';
        glow.style.transitionDuration = '0.5s'; // reset quickly
    }
    if (cycleEl) cycleEl.innerText = t('cycle_one');
    if (tipEl) tipEl.innerText = '';
    _breatheCycleNum = 1;
    // Spawn particles
    spawnBreatheParticles();
    // Auto-start after 0.8s
    setTimeout(function () { toggleBreathing(); }, 800);
}
window.openBreatheScreen = openBreatheScreen;

function closeBreatheScreen() {
    stopBreathing();
    destroyBreatheParticles();
    var overlay = document.getElementById('breatheOverlay');
    if (overlay) overlay.style.display = 'none';
    document.body.style.overflow = '';
}
window.closeBreatheScreen = closeBreatheScreen;

/* === Particle system === */
let _particleInterval = null;

function spawnBreatheParticles() {
    destroyBreatheParticles();
    var container = document.getElementById('breatheParticles');
    if (!container) return;
    function createParticle() {
        var p = document.createElement('div');
        p.className = 'breathe-particle';
        var size = 2 + Math.random() * 3;
        var left = Math.random() * 100;
        var dur = 10 + Math.random() * 15;
        var delay = Math.random() * 8;
        var hue = 240 + Math.random() * 40;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = left + '%';
        p.style.bottom = '-10px';
        p.style.background = 'hsla(' + hue + ', 75%, 70%, ' + (0.3 + Math.random() * 0.4) + ')';
        p.style.animationDuration = dur + 's';
        p.style.animationDelay = delay + 's';
        p.style.boxShadow = '0 0 ' + (size * 3) + 'px hsla(' + hue + ', 75%, 70%, 0.4)';
        container.appendChild(p);
    }
    for (var i = 0; i < 30; i++) createParticle();
    _particleInterval = setInterval(function () {
        if (container.children.length < 40) createParticle();
        if (container.children.length > 50) container.removeChild(container.children[0]);
    }, 2500);
}

function destroyBreatheParticles() {
    if (_particleInterval) { clearInterval(_particleInterval); _particleInterval = null; }
    var container = document.getElementById('breatheParticles');
    if (container) container.innerHTML = '';
}

let _tipIdx = 0;

function showBreatheTip() {
    var tipEl = document.getElementById('breatheTip');
    if (!tipEl) return;
    tipEl.style.opacity = '0';
    setTimeout(function () {
        tipEl.innerText = BREATHE_TIPS[_tipIdx % BREATHE_TIPS.length];
        tipEl.style.transition = 'opacity 1.2s ease';
        tipEl.style.opacity = '1';
        _tipIdx++;
    }, 400);
}

let _breatheCountdown = null;
let _breatheCycleNum = 1;

function toggleBreathing() {
    if (breatheTimer) { stopBreathing(); return; }
    breatheStepIdx = 0;
    _breatheCycleNum = 1;
    showBreatheTip();
    runBreatheStep();
}

function runBreatheStep() {
    const type = BREATHE_TYPES[breatheTypeIdx];
    const step = type.steps[breatheStepIdx % type.steps.length];
    const stepInCycle = breatheStepIdx % type.steps.length;
    const flower = document.getElementById('breatheFlower');
    const glow = document.querySelector('.breathe-bg-glow');
    const phase = document.getElementById('breathePhase');
    const timer = document.getElementById('breatheTimer');
    const cycleEl = document.getElementById('breatheCycleCount');

    if (phase) phase.innerText = step.text;

    // Determine phase type (expanded or collapsed) based directly on the scale property
    let phaseClass = step.scale === '1.5' ? 'expanded' : 'collapsed';

    // Set transition duration to match the step dur precisely
    const durSeconds = (step.dur / 1000) + 's';

    // Animate portal ring (formerly flower)
    if (flower) {
        flower.className = 'breathe-portal ' + phaseClass;
        flower.style.transitionDuration = durSeconds;
    }

    // Animate background glow
    if (glow) {
        glow.className = 'breathe-bg-glow ' + phaseClass;
        glow.style.transitionDuration = durSeconds;
    }

    // Cycle counter update
    if (stepInCycle === 0 && breatheStepIdx > 0) {
        _breatheCycleNum++;
        if (cycleEl) cycleEl.innerText = (getCurrentLanguage() === 'en' ? 'Cycle ' : 'Цикл ') + _breatheCycleNum;
        showBreatheTip();
    }

    // Countdown timer
    var secs = Math.round(step.dur / 1000);
    if (timer) timer.innerText = secs;
    if (_breatheCountdown) clearInterval(_breatheCountdown);
    var remaining = secs - 1;
    _breatheCountdown = setInterval(function () {
        if (remaining > 0 && timer) { timer.innerText = remaining; remaining--; }
        else { clearInterval(_breatheCountdown); _breatheCountdown = null; }
    }, 1000);

    breatheTimer = setTimeout(function () {
        breatheStepIdx++;
        if (breatheTimer) runBreatheStep();
    }, step.dur);
}

function stopBreathing() {
    if (breatheTimer) { clearTimeout(breatheTimer); breatheTimer = null; }
    if (_breatheCountdown) { clearInterval(_breatheCountdown); _breatheCountdown = null; }
    const flower = document.getElementById('breatheFlower');
    const glow = document.querySelector('.breathe-bg-glow');
    const phase = document.getElementById('breathePhase');
    const timer = document.getElementById('breatheTimer');
    if (flower) {
        flower.className = 'breathe-portal';
        flower.style.transitionDuration = '0.5s';
    }
    if (glow) {
        glow.className = 'breathe-bg-glow';
        glow.style.transitionDuration = '0.5s';
    }
    if (phase) phase.innerText = t('breathe_phase');
    if (timer) timer.innerText = '';
}

var groundStepIdx = 0;

function openGroundScreen() {
    groundStepIdx = 0;
    var overlay = document.getElementById('groundOverlay');
    if (!overlay) return;
    overlay.style.backgroundImage = 'linear-gradient(to bottom, rgba(9,16,12,0.52) 0%, rgba(9,16,12,0.82) 100%), url(img/bg/forest.png)';
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    renderGroundStep();
}
window.openGroundScreen = openGroundScreen;

function closeGroundScreen() {
    var overlay = document.getElementById('groundOverlay');
    if (overlay) overlay.style.display = 'none';
    document.body.style.overflow = '';
}
window.closeGroundScreen = closeGroundScreen;

function renderGroundStep() {
    var step = GROUND_STEPS[groundStepIdx];
    var numEl = document.getElementById('groundNumber');
    var senseEl = document.getElementById('groundSense');
    var instrEl = document.getElementById('groundInstruction');
    var btn = document.getElementById('groundNextBtn');
    var dots = document.querySelectorAll('.ground-dot');
    var scene = document.querySelector('.ground-scene');

    if (numEl) { numEl.innerText = step.num; numEl.style.animation = 'none'; numEl.offsetHeight; numEl.style.animation = ''; }
    if (senseEl) { senseEl.innerText = step.sense; senseEl.style.animation = 'none'; senseEl.offsetHeight; senseEl.style.animation = ''; }
    if (instrEl) { instrEl.innerText = step.text; instrEl.style.animation = 'none'; instrEl.offsetHeight; instrEl.style.animation = ''; }
    if (btn) btn.innerText = (groundStepIdx < 4) ? t('done_arrow') : (getCurrentLanguage() === 'en' ? 'Finish' : 'Завершить');
    if (scene) scene.classList.remove('ground-complete');

    dots.forEach(function (d, i) {
        d.className = 'ground-dot' + (i < groundStepIdx ? ' done' : '') + (i === groundStepIdx ? ' active' : '');
    });
}

function groundNext() {
    groundStepIdx++;
    if (groundStepIdx >= GROUND_STEPS.length) {
        showGroundComplete();
        return;
    }
    renderGroundStep();
}
window.groundNext = groundNext;

function showGroundComplete() {
    var numEl = document.getElementById('groundNumber');
    var senseEl = document.getElementById('groundSense');
    var instrEl = document.getElementById('groundInstruction');
    var btn = document.getElementById('groundNextBtn');
    var dots = document.querySelectorAll('.ground-dot');
    var scene = document.querySelector('.ground-scene');

    if (scene) scene.classList.add('ground-complete');
    if (numEl) { numEl.innerText = '\u2713'; numEl.style.animation = 'none'; }
    const content = getLocalizedUiContent();
    if (senseEl) senseEl.innerText = content.groundDone.sense;
    if (instrEl) instrEl.innerText = content.groundDone.text;
    if (btn) { btn.innerText = content.groundDone.button; btn.onclick = closeGroundScreen; }
    dots.forEach(function (d) { d.className = 'ground-dot done'; });
}

var pmrStepIdx = 0;
var pmrPhaseIsTense = true;
var pmrTimerId = null;

function openPmrScreen() {
    pmrStepIdx = 0;
    pmrPhaseIsTense = true;
    var overlay = document.getElementById('pmrOverlay');
    if (!overlay) return;
    overlay.style.backgroundImage = 'linear-gradient(to bottom, rgba(7,10,22,0.58) 0%, rgba(7,10,22,0.84) 100%), url(img/bg/ocean.png)';
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    renderPmrStep();
    startPmrTimer(5);
}
window.openPmrScreen = openPmrScreen;

function closePmrScreen() {
    clearInterval(pmrTimerId);
    pmrTimerId = null;
    var overlay = document.getElementById('pmrOverlay');
    if (overlay) overlay.style.display = 'none';
    document.body.style.overflow = '';
}
window.closePmrScreen = closePmrScreen;

function renderPmrStep() {
    var step = PMR_STEPS[pmrStepIdx];
    var numEl = document.getElementById('pmrStepNum');
    var muscleEl = document.getElementById('pmrMuscle');
    var phaseEl = document.getElementById('pmrPhase');
    var instrEl = document.getElementById('pmrInstruction');
    var scene = document.querySelector('.pmr-scene');
    var dots = document.querySelectorAll('.pmr-dot');

    if (numEl) {
        numEl.innerText = step.num;
        numEl.className = 'pmr-step-num' + (pmrPhaseIsTense ? ' tense' : ' relax');
    }
    if (muscleEl) { muscleEl.innerText = step.muscle; }
    if (phaseEl) {
        const content = getLocalizedUiContent();
        phaseEl.innerText = pmrPhaseIsTense ? content.pmrPhaseTense : content.pmrPhaseRelax;
        phaseEl.className = 'pmr-phase' + (pmrPhaseIsTense ? ' tense' : ' relax');
    }
    if (instrEl) instrEl.innerText = pmrPhaseIsTense ? step.tenseText : step.relaxText;
    if (scene) scene.classList.remove('pmr-complete');

    dots.forEach(function (d, i) {
        d.className = 'pmr-dot' + (i < pmrStepIdx ? ' done' : '') + (i === pmrStepIdx ? ' active' : '');
    });
}

function startPmrTimer(seconds) {
    clearInterval(pmrTimerId);
    var remaining = seconds;
    var timerEl = document.getElementById('pmrTimer');
    if (timerEl) timerEl.innerText = remaining;
    pmrTimerId = setInterval(function () {
        remaining--;
        if (timerEl) timerEl.innerText = remaining > 0 ? remaining : '';
        if (remaining <= 0) {
            clearInterval(pmrTimerId);
            if (pmrPhaseIsTense) {
                pmrPhaseIsTense = false;
                renderPmrStep();
                startPmrTimer(7);
            } else {
                pmrStepIdx++;
                if (pmrStepIdx >= PMR_STEPS.length) {
                    showPmrComplete();
                } else {
                    pmrPhaseIsTense = true;
                    renderPmrStep();
                    startPmrTimer(5);
                }
            }
        }
    }, 1000);
}

function pmrNext() {
    clearInterval(pmrTimerId);
    if (pmrPhaseIsTense) {
        pmrPhaseIsTense = false;
        renderPmrStep();
        startPmrTimer(7);
    } else {
        pmrStepIdx++;
        if (pmrStepIdx >= PMR_STEPS.length) {
            showPmrComplete();
        } else {
            pmrPhaseIsTense = true;
            renderPmrStep();
            startPmrTimer(5);
        }
    }
}
window.pmrNext = pmrNext;

function showPmrComplete() {
    clearInterval(pmrTimerId);
    var numEl = document.getElementById('pmrStepNum');
    var muscleEl = document.getElementById('pmrMuscle');
    var phaseEl = document.getElementById('pmrPhase');
    var instrEl = document.getElementById('pmrInstruction');
    var timerEl = document.getElementById('pmrTimer');
    var btn = document.getElementById('pmrNextBtn');
    var dots = document.querySelectorAll('.pmr-dot');
    var scene = document.querySelector('.pmr-scene');

    if (scene) scene.classList.add('pmr-complete');
    if (numEl) { numEl.innerText = '\u2713'; numEl.className = 'pmr-step-num relax'; }
    if (muscleEl) muscleEl.innerText = '';
    const content = getLocalizedUiContent();
    if (phaseEl) { phaseEl.innerText = content.pmrDone; phaseEl.className = 'pmr-phase relax'; }
    if (instrEl) instrEl.innerText = content.pmrDoneText;
    if (timerEl) timerEl.innerText = '';
    if (btn) { btn.innerText = content.pmrClose; btn.onclick = closePmrScreen; }
    dots.forEach(function (d) { d.className = 'pmr-dot done'; });
}

var stopStepIdx = 0;

function openStopScreen() {
    stopStepIdx = 0;
    var overlay = document.getElementById('stopOverlay');
    if (!overlay) return;
    overlay.style.backgroundImage = 'linear-gradient(to bottom, rgba(6,8,18,0.54) 0%, rgba(6,8,18,0.82) 100%), url(img/bg/stars.png)';
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    renderStopStep();
}
window.openStopScreen = openStopScreen;

function closeStopScreen() {
    var overlay = document.getElementById('stopOverlay');
    if (overlay) overlay.style.display = 'none';
    document.body.style.overflow = '';
}
window.closeStopScreen = closeStopScreen;

function renderStopStep() {
    var step = STOP_STEPS[stopStepIdx];
    var letterEl = document.getElementById('stopLetter');
    var wordEl = document.getElementById('stopWord');
    var instrEl = document.getElementById('stopInstruction');
    var btn = document.getElementById('stopNextBtn');
    var dots = document.querySelectorAll('.stop-dot');
    var scene = document.querySelector('.stop-scene');

    if (letterEl) { letterEl.innerText = step.letter; letterEl.style.animation = 'none'; letterEl.offsetHeight; letterEl.style.animation = ''; }
    if (wordEl) { wordEl.innerText = step.word; wordEl.style.animation = 'none'; wordEl.offsetHeight; wordEl.style.animation = ''; }
    if (instrEl) { instrEl.innerText = step.text; instrEl.style.animation = 'none'; instrEl.offsetHeight; instrEl.style.animation = ''; }
    if (btn) { btn.innerText = (stopStepIdx < 3) ? t('done_arrow') : (getCurrentLanguage() === 'en' ? 'Finish' : 'Завершить'); btn.onclick = stopNext; }
    if (scene) scene.classList.remove('stop-complete');

    dots.forEach(function (d, i) {
        d.className = 'stop-dot' + (i < stopStepIdx ? ' done' : '') + (i === stopStepIdx ? ' active' : '');
    });
}

function stopNext() {
    stopStepIdx++;
    if (stopStepIdx >= STOP_STEPS.length) {
        showStopComplete();
        return;
    }
    renderStopStep();
}
window.stopNext = stopNext;

function showStopComplete() {
    var letterEl = document.getElementById('stopLetter');
    var wordEl = document.getElementById('stopWord');
    var instrEl = document.getElementById('stopInstruction');
    var btn = document.getElementById('stopNextBtn');
    var dots = document.querySelectorAll('.stop-dot');
    var scene = document.querySelector('.stop-scene');

    if (scene) scene.classList.add('stop-complete');
    if (letterEl) { letterEl.innerText = '\u2713'; letterEl.style.animation = 'none'; }
    const content = getLocalizedUiContent();
    if (wordEl) wordEl.innerText = content.stopDone.word;
    if (instrEl) instrEl.innerText = content.stopDone.text;
    if (btn) { btn.innerText = content.stopDone.button; btn.onclick = closeStopScreen; }
    dots.forEach(function (d) { d.className = 'stop-dot done'; });
}

/* === Crisis Plan === */
function saveSosPlan() {
    const text = document.getElementById('sosPlanText')?.value || '';
    localStorage.setItem('sosCrisisPlan', text);
}
function loadSosPlan() {
    const el = document.getElementById('sosPlanText');
    if (el) el.value = localStorage.getItem('sosCrisisPlan') || '';
}
window.saveSosPlan = saveSosPlan;

/* === Notifications === */
let _notifTimers = [];

function openNotifModal() {
    const s = JSON.parse(localStorage.getItem('notifSettings') || '{}');
    document.getElementById('notifMorning').checked = s.morning || false;
    document.getElementById('notifMorningTime').value = s.morningTime || '09:00';
    document.getElementById('notifEvening').checked = s.evening || false;
    document.getElementById('notifEveningTime').value = s.eveningTime || '21:00';
    populateTtsVoiceControls();
    openModal('notifModal');
}
window.openNotifModal = openNotifModal;

function saveNotifSettings() {
    const s = {
        morning: document.getElementById('notifMorning').checked,
        morningTime: document.getElementById('notifMorningTime').value,
        evening: document.getElementById('notifEvening').checked,
        eveningTime: document.getElementById('notifEveningTime').value,
    };
    const ttsSettings = {
        ruVoice: document.getElementById('ttsVoiceRu')?.value || 'ru-RU-SvetlanaNeural',
        enVoice: document.getElementById('ttsVoiceEn')?.value || 'en-US-JennyNeural'
    };
    localStorage.setItem('notifSettings', JSON.stringify(s));
    localStorage.setItem('ttsSettings', JSON.stringify(ttsSettings));
    scheduleNotifications(s);
    closeModal('notifModal');
    // Update bell icon to show active state
    const bell = document.getElementById('notifSidebarBtn');
    if (bell) bell.style.color = (s.morning || s.evening) ? 'var(--accent)' : '';
}
window.saveNotifSettings = saveNotifSettings;

function scheduleNotifications(s) {
    _notifTimers.forEach(t => clearTimeout(t));
    _notifTimers = [];
    if (!('Notification' in window)) return;
    const proceed = () => {
        if (Notification.permission !== 'granted') return;
        function scheduleAt(timeStr, message) {
            const [h, m] = timeStr.split(':').map(Number);
            const now = new Date();
            const target = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m, 0);
            if (target <= now) target.setDate(target.getDate() + 1);
            const delay = target - now;
            _notifTimers.push(setTimeout(() => {
                const notif = getLocalizedUiContent().notifications;
                new Notification(notif.title, { body: message });
                scheduleAt(timeStr, message);
            }, delay));
        }
        const notif = getLocalizedUiContent().notifications;
        if (s.morning) scheduleAt(s.morningTime, notif.morning);
        if (s.evening) scheduleAt(s.eveningTime, notif.evening);
    };
    if (Notification.permission === 'default') {
        Notification.requestPermission().then(proceed);
    } else {
        proceed();
    }
}

function startBreathingFromAI() {
    openModal('sosModal');
    switchSosTab(0);
    if (!breatheTimer) toggleBreathing();
    const practiceLabel = getCurrentLanguage() === 'en' ? 'breathing practice' : 'Дыхательную практику';
    const sentence = getCurrentLanguage() === 'en'
        ? '🌬️ I started a {link} for you. Follow the on-screen instructions.'
        : '🌬️ Я запустил(а) для вас {link}. Следуйте инструкциям на экране.';
    let btnMessage = document.getElementById('messages');
    let div = document.createElement('div');
    div.className = 'msg assistant';
    div.innerHTML = `
                <div class="msg-avatar"><i data-lucide="sparkles" style="width:18px;"></i></div>
                <div class="msg-content"><p>${sentence.replace('{link}', `<a href="#" onclick="openModal('sosModal'); return false;" style="color:var(--accent);text-decoration:underline;">${practiceLabel}</a>`)}</p></div>
            `;
    if (btnMessage) {
        btnMessage.appendChild(div);
        if (window.lucide) window.lucide.createIcons();
        btnMessage.scrollTop = btnMessage.scrollHeight;
    }
}
window.startBreathingFromAI = startBreathingFromAI;

refreshLocalizedExercises();

// --- Article Library ---
const ARTICLE_CATALOG = [
    {
        kicker: 'Статья 1',
        title: 'Что такое депрессия — данные ВОЗ и NIMH',
        excerpt: 'Базовый обзор депрессии: распространённость, факторы риска, подходы к лечению и практические шаги поддержки.',
        sources: ['WHO', 'NIMH'],
        body: [
            'По данным ВОЗ, депрессия остаётся одним из самых распространённых психических расстройств в мире и затрагивает около 5,7% взрослого населения планеты. Женщины сталкиваются с ней чаще мужчин.',
            'ВОЗ подчёркивает, что депрессия возникает не по одной причине, а на фоне сложного взаимодействия социальных, психологических и биологических факторов. Риск повышается после тяжёлых жизненных событий: потери работы, утраты близких, травматического опыта.',
            'National Institute of Mental Health указывает, что при более лёгких формах депрессии первым шагом обычно становится психотерапия. Если только терапия не даёт достаточного эффекта, к ней позже могут добавляться медикаменты. При умеренной и тяжёлой депрессии лекарства, как правило, подключают сразу.',
            'ВОЗ отдельно отмечает, что существуют эффективные методы помощи при лёгкой, умеренной и тяжёлой депрессии, а часть кратких психологических интервенций может применяться даже специалистами без глубокой психотерапевтической подготовки.',
            'Ключевые публикации: WHO Comprehensive Mental Health Action Plan 2013–2030; NIMH Depression Publication (NIH); Global Burden of Disease Study 2021.'
        ],
        bullets: [
            'Выделяйте хотя бы 30 минут в день на физическую активность, даже если это просто ходьба.',
            'Старайтесь держать регулярный режим сна и питания.',
            'Не изолируйтесь: поддерживайте контакт с близкими и говорите о своём состоянии.',
            'Избегайте алкоголя, никотина и запрещённых веществ.',
            'По возможности отложите крупные жизненные решения до стабилизации состояния.'
        ]
    },
    {
        kicker: 'Статья 2',
        title: 'Когнитивная терапия депрессии — наследие Аарона Бека',
        excerpt: 'Как Аарон Бек заложил основу КПТ и почему работа с автоматическими мыслями меняет течение депрессии.',
        sources: ['Beck Institute', 'PMC', 'StatPearls'],
        body: [
            'Аарон Темкин Бек, американский психиатр и профессор Университета Пенсильвании, считается «отцом когнитивной терапии». В 1960-х годах он разработал подход, который позже стал когнитивно-поведенческой терапией.',
            'Работая с депрессивными пациентами, Бек заметил, что в основе их эмоционального состояния часто лежат устойчивые негативные убеждения о потере, неудаче и собственной несостоятельности. Эти убеждения проявляются через автоматические мысли, возникающие быстро и воспринимаемые как факты.',
            'Одно из ключевых понятий Бека — когнитивная триада депрессии: негативный взгляд на себя, на мир и на будущее. Когда человек смотрит на всё через эту схему, его настроение и поведение начинают поддерживать депрессивный цикл.',
            'В 1977 году было опубликовано одно из первых крупных клинических исследований, где когнитивная терапия сравнивалась с антидепрессантами. Это стало важной точкой для признания разговорной терапии как доказательного метода лечения депрессии.',
            'Ключевые публикации: Beck, A.T. et al. (1979). Cognitive Therapy of Depression; Rush, A.J., Beck, A.T. et al. (1977). Cognitive Therapy and Research, 1, 17–37.'
        ],
        bullets: [
            'Замечайте автоматические негативные мысли, а не принимайте их сразу за истину.',
            'Проверяйте мысль вопросами: какие есть факты за и против?',
            'Ищите когнитивные искажения: катастрофизацию, сверхобобщение, чтение мыслей.',
            'Формулируйте более сбалансированную альтернативу вместо жёсткого самокритичного вывода.'
        ]
    },
    {
        kicker: 'Статья 3',
        title: 'Выученная беспомощность и «выученный оптимизм» — Мартин Селигман',
        excerpt: 'Почему чувство «от меня ничего не зависит» связано с депрессией и как работает более реалистичный атрибутивный стиль.',
        sources: ['PMC', 'Positive Psychology Center'],
        body: [
            'Мартин Селигман вместе со Стивеном Майером в 1967 году описал феномен выученной беспомощности. Они показали, что при повторяющихся неконтролируемых негативных событиях человек или животное могут «обучиться» убеждению, что их действия ничего не меняют.',
            'Селигман рассматривал выученную беспомощность как лабораторную модель клинической депрессии. Особенно важным оказалось то, как человек объясняет себе плохие события.',
            'Пессимистический атрибутивный стиль трактует неудачи как постоянные, личные и всеобъемлющие. Оптимистический стиль видит их как временные, ограниченные и не определяющие всю личность. Именно этот сдвиг объяснения помогает снижать уязвимость к депрессии.',
            'Идея выученного оптимизма позже оформилась в практику оспаривания пессимистических убеждений. В книге Learned Optimism Селигман предложил технику ABC: Adversity, Belief, Consequence — событие, убеждение, последствие.',
            'Ключевые публикации: Seligman, M.E.P. & Maier, S.F. (1967). Journal of Experimental Psychology, 74, 1–9; Seligman, M.E.P. (1990). Learned Optimism; Abramson, L.Y., Seligman, M.E.P. & Teasdale, J.D. (1978). Reformulated Learned Helplessness.'
        ],
        bullets: [
            'Замечайте, как вы объясняете себе неудачу.',
            'Спросите себя: это точно навсегда, везде и только из-за меня?',
            'Ищите более ограниченное и реалистичное объяснение события.',
            'Отделяйте факт неприятности от глобального вывода о собственной ценности.'
        ]
    },
    {
        kicker: 'Статья 4',
        title: 'Физическая активность как лечение депрессии — мета-анализы',
        excerpt: 'Что показывают крупные мета-анализы: ходьба, бег, йога и силовые тренировки реально уменьшают симптомы депрессии.',
        sources: ['JAMA Psychiatry', 'BMJ', 'American Journal of Psychiatry'],
        body: [
            'Мета-анализ Pearce et al. в JAMA Psychiatry включил 15 проспективных исследований и более 2 миллионов человеко-лет наблюдений. Люди, выполнявшие рекомендованный объём физической активности, имели на 25% ниже риск развития депрессии по сравнению с малоактивными.',
            'Даже половина от рекомендованного объёма активности была связана с заметной пользой: риск снижался примерно на 18%. Это важно, потому что вход в движение может начинаться не с «идеального режима», а с очень малого шага.',
            'Сетевой мета-анализ Noetel et al. в BMJ в 2024 году показал, что ходьба, бег трусцой, йога и силовые тренировки дают умеренное снижение симптомов депрессии по сравнению с обычным лечением. Авторы рассматривают эти формы нагрузки как полноценный элемент помощи наряду с психотерапией и медикаментами.',
            'Предполагаемые механизмы включают усиление нейрогенеза, влияние на гиппокамп, снижение воспалительных маркеров и активацию систем, связанных с естественной регуляцией стресса и удовольствия.',
            'Ключевые публикации: Pearce, M. et al. (2022). JAMA Psychiatry, 79(6), 550–559; Noetel, M. et al. (2024). BMJ, 384, e075847; Schuch, F.B. et al. (2018). American Journal of Psychiatry, 175(7), 631–648.'
        ],
        bullets: [
            'Начинайте с малого: даже 15 минут ходьбы в день уже полезны.',
            'Постепенно наращивайте активность до 150 минут умеренной нагрузки в неделю.',
            'Выбирайте формат, который реально переносим и приятен: ходьба, йога, плавание, силовые тренировки.',
            'Смотрите на движение как на лечение, а не как на экзамен на силу воли.'
        ]
    },
    {
        kicker: 'Статья 5',
        title: 'Майндфулнесс-когнитивная терапия (MBCT) — профилактика рецидивов депрессии',
        excerpt: 'Почему MBCT снижает риск новых эпизодов депрессии и как идея «мысли — это не факты» помогает выходить из руминации.',
        sources: ['Segal, Williams & Teasdale', 'PMC', 'NICE'],
        body: [
            'MBCT была разработана Зинделем Сигалом, Марком Уильямсом и Джоном Тисдейлом при поддержке Джона Кабат-Зинна. Подход сочетает практики осознанности и когнитивную терапию для профилактики рецидивов депрессии.',
            'Ключевая идея MBCT — помочь человеку замечать ухудшение настроения раньше и не сливаться автоматически с привычными депрессивными паттернами мышления. Осознанность даёт позицию наблюдателя, а когнитивная часть помогает по-новому относиться к мыслям.',
            'Мета-анализы показывают, что у людей с тремя и более депрессивными эпизодами в прошлом MBCT может заметно снижать риск рецидива по сравнению с обычным лечением. NICE в Великобритании включал MBCT в рекомендации как метод профилактики повторных эпизодов.',
            'Классическая программа длится 8 недель и включает групповые встречи, домашнюю практику, сканирование тела, сидячую медитацию, мягкую йогу и обучение распознаванию ранних сигналов ухудшения настроения.',
            'Ключевой принцип MBCT звучит просто: мысли — это не факты. Когда человек учится видеть мысль как ментальное событие, а не как приказ или доказательство, круг руминации ослабевает.',
            'Ключевые публикации: Segal, Z.V., Williams, J.M.G., & Teasdale, J.D. (2002). Mindfulness-Based Cognitive Therapy for Depression; Teasdale, J.D. et al. (2000). Journal of Consulting and Clinical Psychology, 68, 615–623; Kabat-Zinn, J. (1990). Full Catastrophe Living.'
        ],
        bullets: [
            'Отслеживайте ранние сигналы ухудшения настроения до сильного провала.',
            'Практикуйте короткие моменты осознанности, а не только длинные медитации.',
            'Тренируйте позицию наблюдения: мысль пришла, но это ещё не факт.',
            'Возвращайте внимание в тело, дыхание и текущий момент, когда начинается руминация.'
        ]
    },
    {
        kicker: 'Статья 6',
        title: 'Сон и депрессия — двусторонняя связь',
        excerpt: 'Почему бессонница может быть не только симптомом депрессии, но и фактором, который повышает риск нового эпизода.',
        sources: ['Neuroscience Research', 'Journal of Clinical Sleep Medicine', 'PMC'],
        body: [
            'Нарушения сна считаются одним из самых частых симптомов депрессии, но современные данные показывают, что связь идёт в обе стороны. У людей с депрессией часто наблюдаются изменения архитектуры сна, включая сокращение латентности REM-фазы и снижение дельта-мощности в фазе медленного сна.',
            'Недостаток сна сам по себе создаёт физиологический и психологический стресс, который ухудшает эмоциональную регуляцию и повышает риск психических расстройств. Поэтому бессонницу всё чаще рассматривают не только как следствие депрессии, но и как её предиктор.',
            'Лонгитюдные исследования показывают, что бессонница является независимым фактором риска для развития новых и повторных эпизодов депрессии у людей разного возраста. Это важно для профилактики: сон может быть ранним сигналом ухудшения состояния.',
            'Систематические обзоры подтверждают двустороннюю связь между бессонницей, тревогой и депрессией. Один из обсуждаемых механизмов связан с воспалительным путём: нарушения сна активируют симпатическую нервную систему и усиливают провоспалительные процессы.',
            'Ключевые публикации: Yasugaki, S. et al. (2023). Neuroscience Research, 211, 57–64; Fang, H. et al. (2019). J Clin Sleep Med, 15(3), 405–411; Baglioni, C. et al. (2011). J Affect Disord, 135(1-3), 10–19.'
        ],
        bullets: [
            'Поддерживайте стабильное время отхода ко сну и пробуждения.',
            'Уберите экраны хотя бы за час до сна.',
            'Следите за бессонницей как за важным маркером состояния, а не как за мелочью.',
            'При сочетании депрессии и инсомнии учитывайте CBT-I как терапию первой линии.'
        ]
    },
    {
        kicker: 'Статья 7',
        title: 'Социальные связи и одиночество — Джулианна Холт-Ланстад',
        excerpt: 'Почему одиночество связано не только с настроением, но и с долгосрочным риском депрессии и ухудшением здоровья.',
        sources: ['World Psychiatry', 'Perspectives on Psychological Science', 'Harvard T.H. Chan School'],
        body: [
            'Джулианна Холт-Ланстад, профессор психологии и нейронауки Университета Бригама Янга, посвятила значительную часть исследований влиянию социальной изоляции и одиночества на психическое и физическое здоровье.',
            'Современные данные показывают устойчивую связь между социальной изоляцией, чувством одиночества и депрессией на разных этапах жизни. Чем выше уровень качественной социальной связанности, тем ниже риск выраженных депрессивных симптомов.',
            'В обзоре 2024 года в World Psychiatry был показан важный результат: у людей, которые часто испытывают одиночество, вероятность развития новой депрессии более чем вдвое выше по сравнению с теми, кто редко или никогда не чувствует себя одиноким.',
            'Мета-аналитические работы Холт-Ланстад и коллег также показали, что социальная изоляция, одиночество и проживание в одиночку связаны с повышением риска преждевременной смерти. При этом прочные социальные связи, наоборот, заметно повышают шансы на выживание.',
            'Ключевые публикации: Holt-Lunstad, J. (2024). World Psychiatry, 23(3), 312–332; Holt-Lunstad, J. et al. (2015). Perspectives on Psychological Science, 10(2), 227–237; US Surgeon General\'s Advisory (2023).'
        ],
        bullets: [
            'Поддерживайте регулярный контакт хотя бы с одним близким человеком.',
            'Ищите групповые активности: волонтёрство, хобби, спорт, клубы по интересам.',
            'Ставьте акцент на качество связи, а не на количество контактов.',
            'Относитесь к социальной изоляции как к фактору риска, а не просто к особенности характера.'
        ]
    },
    {
        kicker: 'Статья 8',
        title: 'Питание и депрессия — исследование SMILES',
        excerpt: 'Как первое крупное РКИ показало, что улучшение рациона может заметно ослаблять симптомы клинической депрессии.',
        sources: ['BMC Medicine', 'Food & Mood Centre'],
        body: [
            'Феличе Джака, профессор Университета Дикина и основательница Food & Mood Centre, стала одним из ключевых исследователей в области нутрициональной психиатрии. Исследование SMILES было первым рандомизированным контролируемым испытанием, специально созданным для проверки того, может ли улучшение питания помогать в лечении клинической депрессии.',
            'В течение 12 недель участники с умеренной и тяжёлой депрессией получали либо поддержку по модифицированной средиземноморской диете, либо социальную поддержку. Группа с диетической поддержкой показала более выраженное улучшение симптомов, а часть участников достигла полной ремиссии.',
            'Подход SMILES делал акцент на овощах, фруктах, цельнозерновых продуктах, бобовых, орехах, оливковом масле extra virgin, рыбе и умеренном количестве нежирного мяса. Одновременно ограничивались ультраобработанные продукты, сладости и рафинированные углеводы.',
            'Особенно важно, что участники, которые сильнее всего улучшили рацион, получили и наибольшее снижение депрессивных симптомов. Позже результаты получили поддержку в последующих исследованиях, включая HELFIMED и AMMEND.',
            'Ключевые публикации: Jacka, F.N. et al. (2017). BMC Medicine, 15, 23; Parletta, N. et al. (2019). Nutritional Neuroscience; Bayes, J. et al. (2022). American Journal of Clinical Nutrition.'
        ],
        bullets: [
            'Смещайте рацион в сторону овощей, фруктов, бобовых и цельнозерновых.',
            'Добавляйте рыбу, орехи и оливковое масло как более устойчивую основу питания.',
            'Сокращайте долю ультраобработанной пищи и избытка сахара.',
            'Смотрите на питание как на поддерживающий элемент лечения, а не как на магическое решение.'
        ]
    },
    {
        kicker: 'Статья 9',
        title: 'Ось «кишечник — мозг» и депрессия — новый рубеж науки',
        excerpt: 'Что известно о связи микробиоты, воспаления, нейромедиаторов и депрессивных симптомов.',
        sources: ['Nature Communications', 'University College Cork', 'Frontiers in Microbiology'],
        body: [
            'Ось «микробиота — кишечник — мозг» стала одним из самых быстрорастущих направлений в исследовании депрессии. Крупные когортные исследования показали связь между составом кишечной микробиоты и выраженностью депрессивных симптомов.',
            'В одном из заметных исследований, основанном на выборках из Роттердама и Амстердама, была обнаружена связь ряда микробных таксонов с депрессивными симптомами. Эти микроорганизмы вовлечены в метаболические пути, связанные с глутаматом, бутиратом, серотонином и ГАМК.',
            'Джон Крайан и его коллеги показали, что микробные сообщества у людей с депрессией отличаются от таковых у здоровых людей. В экспериментальных моделях перенос такой микробиоты влиял на поведение животных и на метаболизм триптофана, предшественника серотонина.',
            'Хотя это направление ещё развивается, уже ясно, что кишечная микробиота влияет на мозг через иммунные, метаболические и нейромедиаторные механизмы. При этом питание снова оказывается важным звеном, потому что влияет и на воспаление, и на состав микробиоты.',
            'Ключевые публикации: Radjabzadeh, D. et al. (2022). Nature Communications, 13, 7128; Cryan, J. & Dinan, T. (2012). Nature Reviews Neuroscience, 13, 701–712; Bizzozero-Peroni, B. et al. (2025).'
        ],
        bullets: [
            'Увеличивайте долю клетчатки: овощи, бобовые, цельнозерновые.',
            'Добавляйте ферментированные продукты, если они вам подходят.',
            'Ограничивайте ультраобработанную пищу и избыток сахара.',
            'Рассматривайте пробиотики как возможное дополнение, а не замену основному лечению.'
        ]
    },
    {
        kicker: 'Статья 10',
        title: 'Новейшие методы лечения — кетамин, ТМС и цифровые интервенции',
        excerpt: 'Краткий обзор современных подходов для случаев, когда стандартное лечение помогает недостаточно быстро или недостаточно сильно.',
        sources: ['NIMH', 'Clinical Pharmacology & Therapeutics', 'APA'],
        body: [
            'Для людей с резистентной депрессией, когда стандартные антидепрессанты помогают недостаточно, используются новые подходы. Один из самых заметных — кетамин и его форма эскетамин, который может давать быстрый эффект в течение часов, а не недель.',
            'Эскетамин одобрен FDA для резистентной депрессии в форме назального спрея и применяется под наблюдением медицинского персонала. Это не домашняя стратегия самопомощи, а специализированное медицинское лечение.',
            'Другой важный вектор — методы нейростимуляции, включая транскраниальную магнитную стимуляцию. Исследования показывают, что методы этого класса могут быть полезны при тяжёлой депрессии и в ряде случаев дают меньше побочных эффектов, чем более старые подходы.',
            'Отдельно развиваются цифровые интервенции: онлайн-программы когнитивной терапии, телездоровье и цифровые дополнения к психотерапии. Они не заменяют всю помощь, но могут расширять доступ к лечению и поддерживать человека между сессиями.',
            'Рекомендации APA подчёркивают, что лечение депрессии должно подбираться индивидуально. Если в течение 6–8 недель ответ на фармакотерапию остаётся недостаточным, план лечения нужно пересматривать вместе со специалистом.',
            'Ключевые публикации: Raja, S.M. et al. (2024). Clinical Pharmacology & Therapeutics, 116(5), 1314–1324; APA Clinical Practice Guideline (2019); NIMH Brain Stimulation Therapies overview.'
        ],
        bullets: [
            'При тяжёлой или резистентной депрессии обсуждайте варианты лечения только со специалистом.',
            'Не ждите месяцами без пересмотра схемы, если ответа на лечение нет.',
            'Рассматривайте цифровые интервенции как дополнение к терапии, а не как полную замену.',
            'Сохраняйте индивидуальный подход: один и тот же метод подходит не всем.'
        ]
    }
];

const ARTICLE_CATALOG_EN = [
    {
        kicker: 'Article 1',
        title: 'What Depression Is: WHO and NIMH Data',
        excerpt: 'A grounded overview of depression, including prevalence, risk factors, treatment paths, and practical support steps.',
        sources: ['WHO', 'NIMH'],
        body: [
            'According to the World Health Organization, depression remains one of the most common mental disorders worldwide and affects about 5.7% of the adult population. Women experience it more often than men.',
            'WHO emphasizes that depression does not arise from one single cause. It usually develops through a complex interaction of social, psychological, and biological factors, and the risk rises after difficult life events such as loss, trauma, or serious stress.',
            'The National Institute of Mental Health notes that for milder forms of depression, psychotherapy is often the first step. If therapy alone is not enough, medication may be added later. In moderate and severe depression, medication is often introduced earlier.',
            'WHO also stresses that effective treatments exist for mild, moderate, and severe depression, and that some brief psychological interventions can be delivered even outside highly specialized psychotherapy settings.',
            'Key publications: WHO Comprehensive Mental Health Action Plan 2013–2030; NIMH Depression Publication (NIH); Global Burden of Disease Study 2021.'
        ],
        bullets: [
            'Try to include at least 30 minutes of physical activity a day, even if it is only walking.',
            'Keep sleep and meals as regular as you reasonably can.',
            'Stay connected with close people instead of isolating yourself.',
            'Avoid alcohol, nicotine, and illicit substances when possible.',
            'If you can, delay major life decisions until your state is more stable.'
        ]
    },
    {
        kicker: 'Article 2',
        title: 'Cognitive Therapy for Depression: Aaron Beck’s Legacy',
        excerpt: 'How Aaron Beck laid the foundation for CBT and why working with automatic thoughts changes the course of depression.',
        sources: ['Beck Institute', 'PMC', 'StatPearls'],
        body: [
            'Aaron T. Beck, an American psychiatrist and professor at the University of Pennsylvania, is widely seen as the father of cognitive therapy. In the 1960s he developed the approach that later became cognitive behavioral therapy.',
            'Working with depressed patients, Beck noticed that persistent negative beliefs about loss, failure, and personal inadequacy often sat underneath their emotional suffering. These beliefs show up through automatic thoughts that feel immediate and true.',
            'One of Beck’s key ideas is the cognitive triad of depression: a negative view of the self, the world, and the future. When experience is filtered through that triad, mood and behavior begin to maintain the depressive cycle.',
            'A major clinical trial published in 1977 helped establish cognitive therapy as an evidence-based talking treatment by comparing it with antidepressant medication.',
            'Key publications: Beck, A.T. et al. (1979). Cognitive Therapy of Depression; Rush, A.J., Beck, A.T. et al. (1977). Cognitive Therapy and Research, 1, 17–37.'
        ],
        bullets: [
            'Notice automatic negative thoughts instead of accepting them as facts.',
            'Test a thought with evidence for and against it.',
            'Look for distortions such as catastrophizing, overgeneralization, and mind reading.',
            'Replace harsh conclusions with a more balanced alternative.'
        ]
    },
    {
        kicker: 'Article 3',
        title: 'Learned Helplessness and Learned Optimism: Martin Seligman',
        excerpt: 'Why the feeling that “nothing I do matters” is tied to depression and how a more realistic explanatory style helps.',
        sources: ['PMC', 'Positive Psychology Center'],
        body: [
            'Martin Seligman and Steven Maier described learned helplessness in 1967. They showed that repeated uncontrollable negative events can teach a person or animal that their actions make no difference.',
            'Seligman treated learned helplessness as a laboratory model of clinical depression. A crucial factor turned out to be how a person explains bad events to themselves.',
            'A pessimistic explanatory style treats setbacks as permanent, personal, and global. A more optimistic style sees them as temporary, limited, and not equal to the whole self. That shift can reduce vulnerability to depression.',
            'In Learned Optimism, Seligman translated this into practice through the ABC model: adversity, belief, consequence.',
            'Key publications: Seligman, M.E.P. & Maier, S.F. (1967). Journal of Experimental Psychology, 74, 1–9; Seligman, M.E.P. (1990). Learned Optimism; Abramson, L.Y., Seligman, M.E.P. & Teasdale, J.D. (1978). Reformulated Learned Helplessness.'
        ],
        bullets: [
            'Watch how you explain setbacks to yourself.',
            'Ask whether this really means always, everywhere, and all because of me.',
            'Look for a more limited and realistic explanation.',
            'Separate an unpleasant event from a global judgment about your worth.'
        ]
    },
    {
        kicker: 'Article 4',
        title: 'Physical Activity as a Depression Treatment: Meta-Analyses',
        excerpt: 'What large meta-analyses show: walking, jogging, yoga, and strength training can meaningfully reduce depressive symptoms.',
        sources: ['JAMA Psychiatry', 'BMJ', 'American Journal of Psychiatry'],
        body: [
            'The Pearce et al. meta-analysis in JAMA Psychiatry included 15 prospective studies and more than 2 million person-years of follow-up. People who reached the recommended amount of activity had about a 25% lower risk of developing depression than inactive people.',
            'Even half of the recommended level of activity was linked to meaningful benefit. This matters because starting to move does not require an ideal routine from day one.',
            'The 2024 network meta-analysis by Noetel et al. in BMJ found that walking, jogging, yoga, and strength training all produced moderate reductions in depression symptoms compared with usual care.',
            'Possible mechanisms include changes in neurogenesis, the hippocampus, inflammation, and natural stress-regulation systems.',
            'Key publications: Pearce, M. et al. (2022). JAMA Psychiatry, 79(6), 550–559; Noetel, M. et al. (2024). BMJ, 384, e075847; Schuch, F.B. et al. (2018). American Journal of Psychiatry, 175(7), 631–648.'
        ],
        bullets: [
            'Start small: even 15 minutes of walking a day matters.',
            'Build gradually toward about 150 minutes of moderate activity per week.',
            'Choose a form you can realistically tolerate or enjoy.',
            'Treat movement as part of care, not as a test of discipline.'
        ]
    },
    {
        kicker: 'Article 5',
        title: 'Mindfulness-Based Cognitive Therapy (MBCT) and Relapse Prevention',
        excerpt: 'Why MBCT lowers relapse risk and how the idea that “thoughts are not facts” weakens rumination.',
        sources: ['Segal, Williams & Teasdale', 'PMC', 'NICE'],
        body: [
            'MBCT was developed by Zindel Segal, Mark Williams, and John Teasdale with support from Jon Kabat-Zinn. It combines mindfulness practice with cognitive therapy for relapse prevention.',
            'The core aim is to help a person notice mood deterioration earlier and stop fusing automatically with familiar depressive thought patterns. Mindfulness provides an observing position, while the cognitive component helps reshape the relationship to thoughts.',
            'Meta-analyses suggest that for people with three or more prior depressive episodes, MBCT can lower relapse risk meaningfully compared with usual care.',
            'The classic program lasts 8 weeks and includes group sessions, home practice, body scans, seated meditation, gentle yoga, and recognition of early warning signs.',
            'Key publications: Segal, Z.V., Williams, J.M.G., & Teasdale, J.D. (2002). Mindfulness-Based Cognitive Therapy for Depression; Teasdale, J.D. et al. (2000). Journal of Consulting and Clinical Psychology, 68, 615–623; Kabat-Zinn, J. (1990). Full Catastrophe Living.'
        ],
        bullets: [
            'Notice early mood shifts before a larger downturn.',
            'Practice short moments of mindfulness, not only long meditations.',
            'Train the stance that a thought is a mental event, not a fact.',
            'Bring attention back to the body and present moment when rumination starts.'
        ]
    },
    {
        kicker: 'Article 6',
        title: 'Sleep and Depression: A Two-Way Relationship',
        excerpt: 'Why insomnia may be both a symptom of depression and a factor that raises the risk of a new episode.',
        sources: ['Neuroscience Research', 'Journal of Clinical Sleep Medicine', 'PMC'],
        body: [
            'Sleep disturbances are among the most frequent symptoms of depression, but current evidence suggests the relationship works both ways. Depression often changes sleep architecture, while poor sleep itself worsens emotional regulation and stress load.',
            'Longitudinal research shows that insomnia is an independent risk factor for first and recurrent depressive episodes across age groups.',
            'This means sleep problems are not just background noise. They may be an early warning sign of worsening mental health.',
            'Systematic reviews also support a bidirectional link between insomnia, anxiety, and depression, with inflammation being one possible pathway.',
            'Key publications: Yasugaki, S. et al. (2023). Neuroscience Research, 211, 57–64; Fang, H. et al. (2019). J Clin Sleep Med, 15(3), 405–411; Baglioni, C. et al. (2011). J Affect Disord, 135(1-3), 10–19.'
        ],
        bullets: [
            'Keep bedtime and wake time as stable as possible.',
            'Remove screens for at least one hour before sleep.',
            'Treat insomnia as an important marker, not a trivial side issue.',
            'When insomnia and depression overlap, CBT-I is worth considering as a first-line treatment.'
        ]
    },
    {
        kicker: 'Article 7',
        title: 'Social Connection and Loneliness: Julianne Holt-Lunstad',
        excerpt: 'Why loneliness is linked not only to mood, but also to long-term depression risk and poorer health outcomes.',
        sources: ['World Psychiatry', 'Perspectives on Psychological Science', 'Harvard T.H. Chan School'],
        body: [
            'Julianne Holt-Lunstad, a professor of psychology and neuroscience at Brigham Young University, has done major work on how social isolation and loneliness affect mental and physical health.',
            'Current evidence shows a stable link between isolation, loneliness, and depression across the lifespan. Stronger and more meaningful social connection is associated with lower depressive risk.',
            'A 2024 review in World Psychiatry showed that people who often feel lonely have more than twice the risk of developing a new depression compared with those who rarely or never feel lonely.',
            'Her meta-analytic work also suggests that social isolation and loneliness are linked to higher mortality risk, while strong social ties improve survival odds.',
            'Key publications: Holt-Lunstad, J. (2024). World Psychiatry, 23(3), 312–332; Holt-Lunstad, J. et al. (2015). Perspectives on Psychological Science, 10(2), 227–237; US Surgeon General\'s Advisory (2023).'
        ],
        bullets: [
            'Keep regular contact with at least one close person.',
            'Look for group-based activities such as volunteering, hobbies, or sport.',
            'Focus on the quality of connection, not only the number of contacts.',
            'Treat isolation as a real risk factor rather than just a personality trait.'
        ]
    },
    {
        kicker: 'Article 8',
        title: 'Nutrition and Depression: The SMILES Trial',
        excerpt: 'How the first major randomized trial showed that improving diet can meaningfully reduce clinical depression symptoms.',
        sources: ['BMC Medicine', 'Food & Mood Centre'],
        body: [
            'Felice Jacka, a professor at Deakin University and founder of the Food & Mood Centre, became one of the leading researchers in nutritional psychiatry. The SMILES trial was the first randomized controlled study designed specifically to test whether improving diet could help treat clinical depression.',
            'Over 12 weeks, participants with moderate to severe depression received either support for a modified Mediterranean-style diet or social support. The diet-support group showed stronger symptom improvement, and some participants reached remission.',
            'The SMILES pattern emphasized vegetables, fruit, whole grains, legumes, nuts, olive oil, fish, and moderate lean meat, while reducing ultra-processed foods, sweets, and refined carbohydrates.',
            'An important result was that the people who improved their diet the most also showed the greatest drop in depressive symptoms.',
            'Key publications: Jacka, F.N. et al. (2017). BMC Medicine, 15, 23; Parletta, N. et al. (2019). Nutritional Neuroscience; Bayes, J. et al. (2022). American Journal of Clinical Nutrition.'
        ],
        bullets: [
            'Shift your diet toward vegetables, fruit, legumes, and whole grains.',
            'Use fish, nuts, and olive oil as a steadier base for meals.',
            'Reduce ultra-processed foods and excess sugar.',
            'See nutrition as one supportive part of treatment, not as magic.'
        ]
    },
    {
        kicker: 'Article 9',
        title: 'The Gut-Brain Axis and Depression: A New Scientific Frontier',
        excerpt: 'What current research suggests about microbiota, inflammation, neurotransmitters, and depressive symptoms.',
        sources: ['Nature Communications', 'University College Cork', 'Frontiers in Microbiology'],
        body: [
            'The microbiota-gut-brain axis has become one of the fastest-growing areas in depression research. Large cohort studies suggest links between gut microbial composition and the severity of depressive symptoms.',
            'Studies in major Dutch cohorts found associations between several microbial taxa and depressive symptoms. These organisms are involved in pathways related to glutamate, butyrate, serotonin, and GABA.',
            'John Cryan and colleagues showed that the microbiota of people with depression differs from that of healthy individuals. Experimental transfer studies also suggest downstream effects on behavior and tryptophan metabolism.',
            'This field is still developing, but it is already clear that the gut can influence the brain through immune, metabolic, and neurotransmitter pathways. Nutrition matters here as well because it affects both inflammation and microbial composition.',
            'Key publications: Radjabzadeh, D. et al. (2022). Nature Communications, 13, 7128; Cryan, J. & Dinan, T. (2012). Nature Reviews Neuroscience, 13, 701–712; Bizzozero-Peroni, B. et al. (2025).'
        ],
        bullets: [
            'Increase fiber intake through vegetables, legumes, and whole grains.',
            'Add fermented foods if they suit you.',
            'Limit ultra-processed foods and excess sugar.',
            'Think of probiotics as a possible add-on, not a replacement for treatment.'
        ]
    },
    {
        kicker: 'Article 10',
        title: 'Newer Treatments: Ketamine, TMS, and Digital Interventions',
        excerpt: 'A brief look at modern options for cases where standard treatment is not fast enough or not effective enough.',
        sources: ['NIMH', 'Clinical Pharmacology & Therapeutics', 'APA'],
        body: [
            'For treatment-resistant depression, when standard antidepressants do not help enough, newer options are available. One of the most visible examples is ketamine and its form esketamine, which can act within hours rather than weeks.',
            'Esketamine is FDA-approved for treatment-resistant depression as a nasal spray administered under medical supervision. It is not a home self-help strategy but a specialized intervention.',
            'Another important direction is neurostimulation, including transcranial magnetic stimulation. Research suggests these methods can be useful in severe depression and may produce fewer side effects than some older approaches.',
            'Digital interventions are also developing quickly, including online cognitive therapy programs, telehealth, and app-based support between sessions. They do not replace all care, but they can expand access and continuity.',
            'APA guidance emphasizes that depression treatment should be individualized. If medication response remains insufficient after about 6 to 8 weeks, the treatment plan should be reviewed with a clinician.',
            'Key publications: Raja, S.M. et al. (2024). Clinical Pharmacology & Therapeutics, 116(5), 1314–1324; APA Clinical Practice Guideline (2019); NIMH Brain Stimulation Therapies overview.'
        ],
        bullets: [
            'Discuss severe or treatment-resistant depression options only with a clinician.',
            'Do not wait for months without reassessing a treatment plan that is not helping.',
            'Use digital interventions as support, not as a complete replacement.',
            'Keep an individualized view: the same method will not fit everyone.'
        ]
    }
];

function getArticleCatalog() {
    return getCurrentLanguage() === 'en' ? ARTICLE_CATALOG_EN : ARTICLE_CATALOG;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function openArticleLibrary() {
    renderArticleList();
    document.getElementById('articleListContainer').style.display = 'block';
    document.getElementById('articleReaderContainer').style.display = 'none';
    openModal('articleModal');
}
window.openArticleLibrary = openArticleLibrary;

function closeArticleLibraryModal() {
    closeArticleReader();
    closeModal('articleModal');
}
window.closeArticleLibraryModal = closeArticleLibraryModal;

function renderArticleList() {
    const grid = document.getElementById('articleListGrid');
    if (!grid) return;
    const catalog = getArticleCatalog();

    let html = '';
    catalog.forEach((article, index) => {
        html += `
            <div class="article-card" onclick="openArticleReader(${index})">
                <div class="article-card-kicker">${escapeHtml(article.kicker)}</div>
                <div class="article-card-title">${escapeHtml(article.title)}</div>
                <div class="article-card-excerpt">${escapeHtml(article.excerpt)}</div>
                <div class="article-card-sources">
                    ${article.sources.map(source => `<span class="article-source-chip">${escapeHtml(source)}</span>`).join('')}
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
}

function openArticleReader(index) {
    const article = getArticleCatalog()[index];
    if (!article) return;
    window._articleReaderIndex = index;

    document.getElementById('articleListContainer').style.display = 'none';
    document.getElementById('articleReaderContainer').style.display = 'block';
    document.getElementById('articleReaderKicker').innerText = article.kicker;
    document.getElementById('articleReaderTitle').innerText = article.title;
    document.getElementById('articleReaderSources').innerHTML = article.sources
        .map(source => `<span class="article-source-chip">${escapeHtml(source)}</span>`)
        .join('');

    let bodyHtml = article.body.map(paragraph => `<p>${escapeHtml(paragraph)}</p>`).join('');
    if (article.bullets && article.bullets.length) {
        bodyHtml += `<ul>${article.bullets.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
    }
    document.getElementById('articleReaderBody').innerHTML = bodyHtml;

    if (window.lucide) window.lucide.createIcons();
}
window.openArticleReader = openArticleReader;

function closeArticleReader() {
    const list = document.getElementById('articleListContainer');
    const reader = document.getElementById('articleReaderContainer');
    if (list) list.style.display = 'block';
    if (reader) reader.style.display = 'none';
    window._articleReaderIndex = null;
}
window.closeArticleReader = closeArticleReader;

// --- Video Library ---
const VIDEO_CATALOG = [
    { title: 'Почему вас мучает тревога?', title_en: 'Why Anxiety Feels So Overwhelming', author: 'Правое полушарие Интроверта', id: 'WB662esfVpk', duration: '12:18' },
    { title: 'КПТ самостоятельно! | Как работает терапия', title_en: 'CBT on Your Own: How Therapy Works', author: 'Психолог Шастин Егор', id: 'sfRyNk0oouE', duration: '20:53' },
    { title: 'Что такое КПТ? (ABC модель)', title_en: 'What CBT Is (ABC Model)', author: 'ПостПсихология', id: 'rm0tH1oVIXg', duration: '46:23' },
    { title: 'Релаксация по Джекобсону (Практика)', title_en: 'Jacobson Relaxation (Practice)', author: 'Александр Усольцев', id: '_4XzfyFxDTg', duration: '6:00' },
    { title: 'Тревога vs Тревожность (Научпок)', title_en: 'Anxiety vs Anxiousness', author: 'Научпок', id: 'TTCVrYONffw', duration: '6:00' },
    { title: 'Психотерапия при панических атаках', title_en: 'Psychotherapy for Panic Attacks', author: 'Клиника Доктор САН', id: 'Hh-pud7_Uug', duration: '16:12' },
    { title: 'Медитация осознанности Mindfulness', title_en: 'Mindfulness Meditation', author: 'toki well-being', id: 'Juo-8PtSaLI', duration: '12:36' },
    { title: 'Техники против катастрофизации', title_en: 'Techniques Against Catastrophizing', author: 'initium - психологи', id: 'WDTl4qtw94Q', duration: '16:41' }
];

const VIDEO_CATALOG_EN = [
    { title: 'What Is Depression?', author: 'TED-Ed', id: 'z-IR48Mb3W0', duration: '4:29' },
    { title: 'How Does Cognitive Behavioral Therapy Work?', author: 'Psych Hub', id: 'ZdyOwZ4_RnI', duration: '4:55' },
    { title: 'ABC Model of Cognitive Behavioral Therapy', author: 'Therapist Aid', id: 'WRRdSm4ZjX4', duration: '3:52' },
    { title: 'What Is Anxiety Really?', author: 'Therapy in a Nutshell', id: 'db3K8b3ftaY', duration: '12:00' },
    { title: 'How to Stop a Panic Attack: The Anti-Struggle Technique', author: 'Therapy in a Nutshell', id: '2CQpyA485wc', duration: '8:15' },
    { title: 'Progressive Muscle Relaxation: An Essential Anxiety Skill', author: 'Therapy in a Nutshell', id: 'SNqYG95j_UQ', duration: '9:05' },
    { title: '20 Minute Guided Meditation for Reducing Anxiety and Stress', author: 'The Mindful Movement', id: 'MIr3RsUWrdo', duration: '20:16' },
    { title: 'Catastrophizing: How to Stop Making Yourself More Anxious', author: 'Therapy in a Nutshell', id: 'bS2LPNlO07s', duration: '17:22' }
];

function getVideoCatalog() {
    if (getCurrentLanguage() === 'en') return VIDEO_CATALOG_EN;
    return VIDEO_CATALOG.map((video) => ({
        ...video,
        title: video.title
    }));
}

function openVideoLibrary() {
    renderVideoList();
    document.getElementById('videoListContainer').style.display = 'block';
    document.getElementById('videoPlayerContainer').style.display = 'none';
    document.getElementById('videoIframe').src = '';

    // Open the modal explicitly
    const modal = document.getElementById('videoModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}
window.openVideoLibrary = openVideoLibrary;

function closeVideoLibraryModal() {
    closeModal('videoModal');
    document.getElementById('videoIframe').src = '';
}
window.closeVideoLibraryModal = closeVideoLibraryModal;

function renderVideoList() {
    const grid = document.getElementById('videoListGrid');
    if (!grid) return;

    let html = '';
    getVideoCatalog().forEach(vid => {
        // Use i.ytimg.com as it often bypasses local file restrictions better than img.youtube.com
        let thumbUrl = `https://i.ytimg.com/vi/${vid.id}/mqdefault.jpg`;
        html += `
            <div onclick="playVideo('${vid.id}')" style="display:flex; gap:16px; background:var(--bg); border:1px solid var(--border); border-radius:12px; padding:12px; cursor:pointer; transition:all 0.2s; align-items:center;" onmouseover="this.style.borderColor='var(--gray)'" onmouseout="this.style.borderColor='var(--border)'">
                <div style="position:relative; width:120px; height:70px; border-radius:8px; overflow:hidden; flex-shrink:0; background:var(--panel); display:flex; align-items:center; justify-content:center;">
                    <img src="${thumbUrl}" style="width:100%; height:100%; object-fit:cover; opacity:0.8; transition: opacity 0.3s;" onerror="this.style.opacity='0';">
                    <div style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.2);">
                        <i data-lucide="play" style="width:24px; color:rgba(255,255,255,0.8); fill:rgba(255,255,255,0.2);"></i>
                    </div>
                </div>
                <div style="flex:1; min-width:0;">
                    <div style="font-size:14px; font-weight:600; color:var(--text); margin-bottom:6px; line-height:1.4; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${vid.title}</div>
                    <div style="display:flex; align-items:center; gap:12px; font-size:12px; color:var(--gray);">
                        <span style="display:flex; align-items:center; gap:4px;"><i data-lucide="user" style="width:12px; opacity:0.6;"></i> ${vid.author}</span>
                        <span style="display:flex; align-items:center; gap:4px;"><i data-lucide="clock" style="width:12px; opacity:0.6;"></i> ${vid.duration}</span>
                    </div>
                </div>
            </div>
        `;
    });
    grid.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
}

function playVideo(youtubeId) {
    document.getElementById('videoListContainer').style.display = 'none';
    const playerContainer = document.getElementById('videoPlayerContainer');
    playerContainer.style.display = 'block';
    const iframe = document.getElementById('videoIframe');
    iframe.src = `https://www.youtube-nocookie.com/embed/${youtubeId}?autoplay=1&rel=0&origin=${window.location.origin}`;
}
window.playVideo = playVideo;

function closeVideoPlayer() {
    document.getElementById('videoListContainer').style.display = 'block';
    document.getElementById('videoPlayerContainer').style.display = 'none';
    document.getElementById('videoIframe').src = '';
}
window.closeVideoPlayer = closeVideoPlayer;
