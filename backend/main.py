from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
import json
import os
from datetime import datetime
from . import db, monitor
from .constants import APP_NAME, CONFIG_FILE, DEFAULT_CONFIG

import httpx
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
current_app = None
monitoring = True
whitelist = []
app_limits = {} # { "app_name": seconds_limit }
ai_config = {
    "api_key": "",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo"
}

# Load config
def load_config():
    global whitelist, app_limits, ai_config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                whitelist = config.get("Process Whitelist", [])
                app_limits = config.get("App Limits", {})
                ai_config = config.get("AI Config", ai_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            whitelist = []
            app_limits = {}
    else:
        whitelist = []
        app_limits = {}

def save_config():
    global whitelist, app_limits, ai_config
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()
    
    config["Process Whitelist"] = whitelist
    config["App Limits"] = app_limits
    config["AI Config"] = ai_config
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

def monitor_loop():
    global current_app
    # Keep track of notifications sent today to avoid spamming
    notified_apps = set()
    last_day = datetime.now().day
    
    while monitoring:
        try:
            now_day = datetime.now().day
            if now_day != last_day:
                notified_apps.clear()
                last_day = now_day

            # monitor.get_active_window now returns friendly_name
            friendly_name = monitor.get_active_window()
            if friendly_name:
                current_app = friendly_name
                
                # Check whitelist
                if friendly_name not in whitelist:
                    db.log_usage(friendly_name, 1) # Log 1 second
                    
                    # Check limits
                    if friendly_name in app_limits:
                        limit = app_limits[friendly_name]
                        # Get today's usage for this app
                        # Optimization: In a real app, we might cache this or increment a counter in memory
                        # For now, querying DB every second is too heavy. 
                        # Let's just check every minute or so? Or keep a simple in-memory counter for the current session?
                        # Better: Query DB only if we are close to limit?
                        # Simplest robust way: Query DB but maybe not every single second if performance is an issue.
                        # Given SQLite speed and single user, it might be fine.
                        # Let's optimize: get usage only if it's in limits list
                        
                        # To avoid DB spam, we can rely on the fact that we just logged 1 second.
                        # But we need the TOTAL for today.
                        # Let's do a quick query.
                        today_data = db.get_daily_usage_data()
                        # Find usage for current app
                        usage = next((item[1] for item in today_data if item[0] == friendly_name), 0)
                        
                        if usage >= limit and friendly_name not in notified_apps:
                            monitor.send_notification(
                                "Time Limit Reached",
                                f"You have used {friendly_name} for {usage//60} minutes today. Limit is {limit//60} minutes."
                            )
                            notified_apps.add(friendly_name)
                            
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(1)

@app.on_event("startup")
def startup_event():
    load_config()
    db.init_db()
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()

@app.get("/api/status")
def get_status():
    return {"current_app": current_app}

@app.get("/api/today")
def get_today_usage():
    data = db.get_daily_usage_data()
    # data is list of (app, duration)
    result = []
    for app_name, duration in data:
        if app_name in whitelist:
            continue
        result.append({
            "name": app_name,
            "duration": duration,
        })
    return result

@app.get("/api/icon/{app_name}")
def get_icon(app_name: str):
    b64 = monitor.get_process_icon(app_name)
    if b64:
        return {"image": f"data:image/png;base64,{b64}"}
    return {"image": None}

@app.get("/api/whitelist")
def get_whitelist():
    return whitelist

@app.post("/api/whitelist")
def add_whitelist(item: str = Body(..., embed=True)):
    if item not in whitelist:
        whitelist.append(item)
        save_config()
    return whitelist

@app.delete("/api/whitelist")
def remove_whitelist(item: str = Body(..., embed=True)):
    if item in whitelist:
        whitelist.remove(item)
        save_config()
    return whitelist

@app.get("/api/week")
def get_week_usage():
    data = db.get_weekly_usage_data()
    result = []
    for app_name, duration in data:
        if app_name in whitelist:
            continue
        result.append({
            "name": app_name,
            "duration": duration,
        })
    return result

@app.get("/api/limits")
def get_limits():
    return app_limits

@app.post("/api/limits")
def update_limits(limits: dict = Body(...)):
    global app_limits
    app_limits = limits
    save_config()
    return app_limits

@app.get("/api/ai-config")
def get_ai_config():
    return ai_config

@app.post("/api/ai-config")
def update_ai_config(config: dict = Body(...)):
    global ai_config
    ai_config.update(config)
    save_config()
    return ai_config

class AIReportRequest(BaseModel):
    period: str = "today" # today or week

@app.post("/api/report/ai")
async def generate_ai_report(request: AIReportRequest):
    if not ai_config.get("api_key"):
        return {"error": "API Key not configured"}
    
    # Get data
    if request.period == "week":
        data = db.get_weekly_usage_data()
        period_str = "past 7 days"
    else:
        data = db.get_daily_usage_data()
        period_str = "today"
        
    # Filter whitelist
    filtered_data = []
    total_duration = 0
    for app_name, duration in data:
        if app_name in whitelist:
            continue
        filtered_data.append(f"{app_name}: {duration//60} mins")
        total_duration += duration
        
    usage_summary = "\n".join(filtered_data[:10]) # Top 10
    total_hours = total_duration / 3600
    
    prompt = f"""
    You are a strict, sharp-tongued, but constructive productivity coach.
    The user has spent {total_hours:.1f} hours on the computer {period_str}.
    Here are their top apps:
    {usage_summary}
    
    Please provide a "Sharp Critique" (锐评) of their time management. 
    Be slightly sarcastic if they spent too much time on entertainment, but encouraging if they worked hard.
    Keep it under 150 words. Language: Chinese.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ai_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {ai_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": ai_config['model'],
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30.0
            )
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {"content": content}
            else:
                return {"error": f"AI API Error: {response.status_code} {response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

@app.get("/api/processes")
def get_processes():
    # Get historical processes from DB
    usage_data = db.get_all_usage_data()
    raw_processes = set(item[0] for item in usage_data)
    
    # Add current process if active
    current = monitor.get_active_window()
    if current:
        raw_processes.add(current)
    
    # Intelligent filtering and deduplication
    # Map normalized name (lowercase, no .exe) to best display name
    process_map = {}
    
    for name in raw_processes:
        if not name: continue
        
        # Normalize
        norm = name.lower()
        if norm.endswith('.exe'):
            norm = norm[:-4]
            
        # Determine score for "quality" of name
        # 1. Prefer names without .exe
        # 2. Prefer names with mixed case or spaces (likely Friendly Names)
        # 3. Prefer longer names (usually "Google Chrome" > "chrome")
        
        score = 0
        if not name.lower().endswith('.exe'):
            score += 10
        if name != name.lower() and name != name.upper(): # Mixed case
            score += 5
        if ' ' in name:
            score += 5
            
        current_best = process_map.get(norm)
        if not current_best or score > current_best['score']:
            process_map[norm] = {'name': name, 'score': score}
            
    # Return only the best names
    final_list = sorted([v['name'] for v in process_map.values()])
    return final_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
