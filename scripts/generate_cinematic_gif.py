import os
import math
import subprocess
import concurrent.futures
from PIL import Image, ImageChops

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SCRATCH_DIR = os.path.join(PROJECT_ROOT, 'scratch', 'cinematic_demo')
FRAMES_DIR = os.path.join(SCRATCH_DIR, 'frames')
PNGS_DIR = os.path.join(SCRATCH_DIR, 'pngs')
FINAL_FRAMES_DIR = os.path.join(SCRATCH_DIR, 'final_frames')

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(PNGS_DIR, exist_ok=True)
os.makedirs(FINAL_FRAMES_DIR, exist_ok=True)

CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# SVG Icons
ICON_NOTEBOOK = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13.4 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7.4"/><path d="M2 6h4"/><path d="M2 10h4"/><path d="M2 14h4"/><path d="M2 18h4"/><path d="M18.4 2.6a2.12 2.12 0 0 1 3 3L11 16l-4 1 1-4Z"/></svg>'''
ICON_MOON = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'''
ICON_CLIPBOARD = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/></svg>'''
ICON_CALENDAR = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg>'''
ICON_BARCHART = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>'''
ICON_SETTINGS = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>'''
ICON_BRAIN = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M12 18v4"/></svg>'''
ICON_USER = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'''
ICON_LIFEBUOY = '''<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/><circle cx="12" cy="12" r="4"/></svg>'''
ICON_SEND = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>'''
ICON_WIND = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.7 7.7A2.5 2.5 0 1 1 19 12H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/></svg>'''

def get_chat_html(typed_text="", show_user_msg=False, show_assistant_msg=False, assistant_text="", show_cursor_click=False):
    css_path = os.path.abspath(os.path.join(PROJECT_ROOT, 'frontend', 'css', 'style.css'))
    
    user_msg_html = ""
    if show_user_msg:
        user_msg_html = f'''
        <div class="msg user" style="animation: fadeIn 0.3s ease;">
            <div class="msg-avatar">{ICON_USER}</div>
            <div class="msg-content">
                <p>I'm feeling really anxious and overwhelmed right now...</p>
            </div>
        </div>
        '''
        
    assistant_msg_html = ""
    if show_assistant_msg:
        assistant_msg_html = f'''
        <div class="msg" style="animation: fadeIn 0.3s ease;">
            <div class="msg-avatar" style="background:var(--accent-light); color:var(--accent);">{ICON_BRAIN}</div>
            <div class="msg-content">
                <p>{assistant_text}</p>
                <div style="margin-top:14px;">
                    <div class="sos-action-card" style="display:inline-flex; align-items:center; gap:10px; padding:10px 16px; background:var(--accent-light); color:var(--accent); border-radius:12px; font-weight:600; font-size:14px; border:1px solid rgba(121, 114, 152, 0.2); box-shadow:0 2px 8px rgba(121, 114, 152, 0.15);">
                        {ICON_WIND}
                        <span>🌬️ Calming Breathing Practice (5s Inhale)</span>
                    </div>
                </div>
            </div>
        </div>
        '''
        
    click_indicator = ""
    if show_cursor_click:
        click_indicator = '''
        <div style="position:absolute; bottom:180px; left:460px; pointer-events:none; z-index:100; display:flex; align-items:center; gap:8px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="#2f2f2b" stroke="#ffffff" stroke-width="1.5">
                <path d="m3 3 7 18 3-7 7-3L3 3z"/>
            </svg>
            <div style="width:28px; height:28px; border-radius:50%; background:rgba(121,114,152,0.4); border:2px solid #797298; position:absolute; top:-6px; left:-6px; animation: pulse 0.5s infinite;"></div>
        </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="file://{css_path}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            display: flex;
            height: 920px;
            width: 1280px;
            overflow: hidden;
            padding-left: 54px;
        }}
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 54px;
            background: var(--panel);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16px 0;
            gap: 12px;
            z-index: 10;
        }}
        .sidebar-btn {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--gray);
            background: transparent;
            border: none;
            cursor: pointer;
        }}
        .sidebar-btn.active, .sidebar-btn:hover {{
            background: var(--accent-light);
            color: var(--accent);
        }}
        .container {{
            max-width: 820px;
            margin: 0 auto;
            width: 100%;
            display: flex;
            flex-direction: column;
            height: 920px;
            position: relative;
        }}
        .header {{
            padding: 18px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            background: var(--bg);
        }}
        .chat-box {{
            flex: 1;
            overflow-y: auto;
            padding: 24px 24px 10px 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .input-dock {{
            padding: 14px 24px 24px 24px;
            background: var(--bg);
        }}
        .cursor {{
            display: inline-block;
            width: 2px;
            height: 18px;
            background: var(--accent);
            vertical-align: middle;
            margin-left: 2px;
            animation: blink 0.8s infinite;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0; }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <aside class="sidebar">
        <button class="sidebar-btn active" title="Thought Diary">{ICON_NOTEBOOK}</button>
        <button class="sidebar-btn" title="Sleep Tracker">{ICON_MOON}</button>
        <button class="sidebar-btn" title="Assessments">{ICON_CLIPBOARD}</button>
        <button class="sidebar-btn" title="Calendar">{ICON_CALENDAR}</button>
        <button class="sidebar-btn" title="Dashboard">{ICON_BARCHART}</button>
        <div style="margin-top:auto; display:flex; flex-direction:column; gap:8px;">
            <button class="sidebar-btn" title="Settings">{ICON_SETTINGS}</button>
        </div>
    </aside>

    <div class="container">
        <div class="header">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="color:var(--accent); display:flex;">{ICON_BRAIN}</div>
                <span style="font-weight:600; font-size:16px; color:var(--text);">CBT Assistant</span>
            </div>
            <div style="display:flex; align-items:center; gap:14px;">
                <button style="background:#797298; color:#ffffff; border:none; border-radius:10px; padding:7px 14px; font-size:13px; font-weight:600; display:flex; align-items:center; gap:6px; cursor:pointer;">
                    {ICON_LIFEBUOY} <span>SOS</span>
                </button>
                <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:var(--gray);">
                    <span style="width:8px; height:8px; border-radius:50%; background:#6aa882; display:inline-block;"></span>
                    <span>Online • ornith-1.5:9b</span>
                </div>
            </div>
        </div>

        <div class="chat-box">
            {user_msg_html}
            {assistant_msg_html}
        </div>

        <div class="input-dock">
            <div class="input-wrap" style="flex-direction:column; align-items:stretch; padding:14px 18px; border-radius:18px; background:var(--panel); border:1px solid var(--border); box-shadow:0 4px 16px rgba(0,0,0,0.04);">
                <div style="min-height:36px; font-size:15px; color:var(--text); line-height:1.5; font-family:inherit;">
                    {typed_text}{'<span class="cursor"></span>' if not show_user_msg else ''}
                </div>
                <div style="display:flex; justify-content:flex-end; align-items:center; margin-top:6px;">
                    <button class="btn-send" style="background:var(--accent); color:#fff; width:34px; height:34px; border-radius:50%; border:none; display:flex; align-items:center; justify-content:center; cursor:pointer;">
                        {ICON_SEND}
                    </button>
                </div>
            </div>
            <p style="text-align:center; font-size:11.5px; color:var(--gray); opacity:0.7; margin-top:8px;">
                Local CBT Assistant grounded via knowledge base RAG and session memory.
            </p>
        </div>
    </div>
    {click_indicator}
</body>
</html>'''
    return html

def get_breathe_html(scale, count_num, t_sec, particles):
    css_path = os.path.abspath(os.path.join(PROJECT_ROOT, 'frontend', 'css', 'style.css'))
    bg_img_path = os.path.abspath(os.path.join(PROJECT_ROOT, 'frontend', 'img', 'bg', 'forest.png'))
    
    p_html = ''
    for p in particles:
        cur_y = (p['start_y'] + p['speed'] * t_sec) % 900
        p_html += f'''<div class="breathe-particle" style="width:{p['size']}px;height:{p['size']}px;left:{p['left']}%;bottom:{cur_y}px;background:hsla({p['hue']},75%,70%,0.45);box-shadow:0 0 {p['size']*3}px hsla({p['hue']},75%,70%,0.4);"></div>'''
        
    ease_progress = (scale - 1.0) / 0.6
    glow_scale = 1.0 + 0.5 * ease_progress
    glow_opacity = 0.35 + 0.45 * ease_progress

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="file://{css_path}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{
            width: 1280px;
            height: 920px;
            overflow: hidden;
            background: #050510;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        #breatheOverlay {{
            display: flex !important;
            width: 1280px;
            height: 920px;
            position: absolute;
            top: 0;
            left: 0;
            background-image: linear-gradient(to bottom, rgba(5,5,16,0.6) 0%, rgba(5,5,16,0.85) 100%), url('file://{bg_img_path}');
            background-size: cover;
            background-position: center;
        }}
        #breatheFlower {{
            transform: scale({scale:.4f}) !important;
            opacity: {0.65 + 0.35 * ease_progress:.3f} !important;
            transition: none !important;
        }}
        .breathe-bg-glow {{
            transform: scale({glow_scale:.4f}) !important;
            opacity: {glow_opacity:.3f} !important;
            transition: none !important;
        }}
    </style>
</head>
<body>
    <div id="breatheOverlay" class="breathe-overlay">
        <div class="breathe-bg-glow"></div>
        <div class="breathe-particles">{p_html}</div>
        <button type="button" class="sos-audio-toggle" data-sos-audio-toggle data-enabled="true" aria-pressed="true">
            <span class="sos-audio-on">♪</span>
        </button>
        <button class="breathe-close-btn" aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
        <div class="breathe-scene">
            <div class="breathe-portal" id="breatheFlower">
                <div class="breathe-portal-ring"></div>
            </div>
            <div class="breathe-text-overlay" id="breatheTextOverlay">
                <span id="breathePhase" class="breathe-phase-text">Inhale...</span>
                <span id="breatheTimer" class="breathe-timer-text">{count_num}</span>
            </div>
            <div class="breathe-info">
                <span id="breatheCycleCount" class="breathe-cycle">CYCLE 1</span>
                <p id="breatheHint" class="breathe-hint">Follow the circle</p>
                <p id="breatheTip" class="breathe-tip">Breathe through your nose for the strongest effect</p>
            </div>
        </div>
    </div>
</body>
</html>'''
    return html

def render_one(name, html_content):
    html_file = os.path.join(FRAMES_DIR, f'{name}.html')
    png_file = os.path.join(PNGS_DIR, f'{name}.png')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    cmd = [
        CHROME_PATH,
        '--headless=new',
        '--disable-gpu',
        '--window-size=1280,920',
        f'--screenshot={png_file}',
        f'file://{html_file}'
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return name

def main():
    print("Generating cinematic frames specification...")
    
    # 1. Typing prompts
    prompt = "I'm feeling really anxious and overwhelmed right now..."
    typing_frames = []
    # 14 frames for typing
    for i in range(14):
        chars = int((i + 1) / 14 * len(prompt))
        text = prompt[:chars]
        typing_frames.append(('chat_type_' + f'{i:02d}', get_chat_html(typed_text=text)))
        
    # 2. User message posted (4 frames)
    user_posted_frames = []
    for i in range(4):
        user_posted_frames.append(('chat_user_' + f'{i:02d}', get_chat_html(show_user_msg=True)))
        
    # 3. Assistant responds with supportive text & breathing action (16 frames)
    ast_text = "I hear you. Let's take a pause together and ground yourself with a calming breathing practice."
    ast_frames = []
    for i in range(16):
        show_click = (i >= 12)
        ast_frames.append(('chat_ast_' + f'{i:02d}', get_chat_html(
            show_user_msg=True,
            show_assistant_msg=True,
            assistant_text=ast_text,
            show_cursor_click=show_click
        )))
        
    # 4. Breathing Inhale Sequence (50 frames, 5 seconds at unaccelerated 1s/count)
    particles = []
    for i in range(35):
        particles.append({
            'size': 2 + (i % 4),
            'left': (i * 2.85 + 3) % 96,
            'hue': 240 + (i % 40),
            'start_y': (i * 27 + 50) % 850,
            'speed': 30 + (i % 5) * 10
        })
        
    breathe_frames = []
    total_b_frames = 50
    for i in range(total_b_frames):
        t_sec = i / 10.0
        count_num = min(5, int(t_sec) + 1)
        progress = i / (total_b_frames - 1)
        ease_progress = 0.5 - 0.5 * math.cos(math.pi * progress)
        scale = 1.0 + 0.6 * ease_progress
        breathe_frames.append(('breathe_' + f'{i:02d}', get_breathe_html(scale, count_num, t_sec, particles)))

    all_specs = typing_frames + user_posted_frames + ast_frames + breathe_frames
    print(f"Total base frames to render: {len(all_specs)}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(render_one, name, html) for name, html in all_specs]
        for f in concurrent.futures.as_completed(futures):
            f.result()
            
    print("All base frames rendered to PNG.")
    
    # 5. Composite timeline with smooth cross-dissolve transitions
    # - Chat typing: 14 frames
    # - Chat user: 4 frames
    # - Chat assistant: 16 frames
    # - Transition Chat -> Breathing (8 cross-fade frames)
    # - Breathing Inhale: 50 frames
    # - Transition Breathing -> Chat Loop (8 cross-fade frames)
    
    timeline = []
    
    # Chat section
    for name, _ in typing_frames:
        timeline.append(os.path.join(PNGS_DIR, f'{name}.png'))
    for name, _ in user_posted_frames:
        timeline.append(os.path.join(PNGS_DIR, f'{name}.png'))
    for name, _ in ast_frames:
        timeline.append(os.path.join(PNGS_DIR, f'{name}.png'))
        
    # Crossfade 1: Last chat frame -> First breathe frame (8 frames)
    last_chat_img = Image.open(timeline[-1]).convert('RGB')
    first_breathe_img = Image.open(os.path.join(PNGS_DIR, f'{breathe_frames[0][0]}.png')).convert('RGB')
    
    dissolve1_frames = []
    for step in range(1, 9):
        alpha = step / 9.0
        blended = Image.blend(last_chat_img, first_breathe_img, alpha)
        diss_path = os.path.join(FINAL_FRAMES_DIR, f'dissolve1_{step:02d}.png')
        blended.save(diss_path)
        dissolve1_frames.append(diss_path)
        
    timeline.extend(dissolve1_frames)
    
    # Breathing section
    for name, _ in breathe_frames:
        timeline.append(os.path.join(PNGS_DIR, f'{name}.png'))
        
    # Crossfade 2: Last breathe frame -> First chat frame (8 frames) for seamless loop
    last_breathe_img = Image.open(timeline[-1]).convert('RGB')
    first_chat_img = Image.open(os.path.join(PNGS_DIR, f'{typing_frames[0][0]}.png')).convert('RGB')
    
    dissolve2_frames = []
    for step in range(1, 9):
        alpha = step / 9.0
        blended = Image.blend(last_breathe_img, first_chat_img, alpha)
        diss_path = os.path.join(FINAL_FRAMES_DIR, f'dissolve2_{step:02d}.png')
        blended.save(diss_path)
        dissolve2_frames.append(diss_path)
        
    timeline.extend(dissolve2_frames)
    
    print(f"Total timeline frames: {len(timeline)}")
    
    # Save ordered sequence for ffmpeg
    for idx, src_path in enumerate(timeline):
        dst_path = os.path.join(FINAL_FRAMES_DIR, f'seq_{idx:04d}.png')
        img = Image.open(src_path)
        img.save(dst_path)
        
    print("Compiling final optimized GIF with ffmpeg...")
    output_gif = os.path.join(PROJECT_ROOT, 'assets', 'cbt-assistant-demo.gif')
    
    cmd = [
        'ffmpeg', '-y',
        '-framerate', '10',
        '-i', os.path.join(FINAL_FRAMES_DIR, 'seq_%04d.png'),
        '-filter_complex', '[0:v] split [a][b];[a] palettegen=max_colors=192:stats_mode=single [p];[b][p] paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle',
        output_gif
    ]
    subprocess.run(cmd, check=True)
    
    size_mb = os.path.getsize(output_gif) / (1024 * 1024)
    print(f"Cinematic Demo GIF generated successfully: {output_gif} ({size_mb:.2f} MB)")

if __name__ == '__main__':
    main()
