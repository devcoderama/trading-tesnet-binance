import json, urllib.request, urllib.error, time
from config.settings import settings

PROVIDERS = [p.strip() for p in (settings.AI_PROVIDERS or "gemini").split(",") if p.strip()]

def _key(provider):
    env = (provider + "_API_KEY").upper()
    import os
    return os.getenv(env, settings.AI_API_KEY)

def _openai_compat(provider, base, model, prompt, key):
    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 10,
    }).encode()
    req = urllib.request.Request(base + "/v1/chat/completions", data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.loads(r.read().decode())
    return j["choices"][0]["message"]["content"].strip().upper()

def _anthropic(prompt, key):
    data = json.dumps({
        "model": "claude-3-haiku-20240307",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=data, headers={
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.loads(r.read().decode())
    return j["content"][0]["text"].strip().upper()

def _gemini(prompt, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.loads(r.read().decode())
    return j["candidates"][0]["content"]["parts"][0]["text"].strip().upper()

def _call(provider, prompt):
    key = _key(provider)
    if not key:
        raise RuntimeError(f"no key for {provider}")
    if provider in ("openai", "chatgpt", "gpt"):
        return _openai_compat(provider, "https://api.openai.com", "gpt-4o-mini", prompt, key)
    if provider in ("grok", "xai"):
        return _openai_compat(provider, "https://api.x.ai", "grok-2-latest", prompt, key)
    if provider in ("claude", "anthropic"):
        return _anthropic(prompt, key)
    if provider in ("gemini", "google"):
        return _gemini(prompt, key)
    raise RuntimeError(f"unknown provider {provider}")

def _normalize(text):
    for t in ("BUY", "SELL", "HOLD"):
        if t in text:
            return t
    return "HOLD"

def get_ai_signal(closes, symbol):
    if not closes:
        return "HOLD", None
    prompt = (
        "You are a trading assistant. Given recent closing prices (oldest to newest) for "
        f"{symbol}: {closes[-20:]}. Reply with exactly one word: BUY, SELL, or HOLD. "
        "No explanation."
    )
    last_err = None
    for provider in PROVIDERS:
        try:
            out = _call(provider, prompt)
            sig = _normalize(out)
            return sig, provider
        except Exception as e:
            last_err = e
            time.sleep(1)
            continue
    return "HOLD", f"none({last_err})"