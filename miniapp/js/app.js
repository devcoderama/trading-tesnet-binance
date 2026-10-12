async function api(path, method="GET", body=null){
  const token=new URLSearchParams(location.search).get('t') || localStorage.getItem('miniapp_token') || '';
  const sep=path.includes('?')?'&':'?';
  const url=token ? path+sep+'t='+encodeURIComponent(token) : path;
  const opts={method, headers:{"Content-Type":"application/json"}, credentials:'include'};
  if(token) opts.headers.Authorization='Bearer '+token;
  if(body) opts.body=JSON.stringify(body);
  let r=await fetch(url,opts);
  if(r.status===401){
    const username=prompt('Username miniapp:');
    const pwd=prompt('Password miniapp:');
    if(username && pwd){ await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:username,password:pwd})}); r=await fetch(url,opts); }
  }
  return r.json();
}
async function loadProviders(){ const r=await api('/api/ai/providers'); document.getElementById('providers').innerText=(r.providers||[]).join(',')||'-'; }
async function addProvider(){ const name=document.getElementById('newProvider').value.trim(); if(!name){msg('nama provider wajib');return;} const r=await api('/api/ai/providers/add','POST',{name}); if(r.ok){ msg('Provider added.'); await loadProviders(); } else msg(r.error||'gagal'); }
async function removeProvider(){ const name=document.getElementById('newProvider').value.trim(); if(!name){msg('nama provider wajib');return;} const r=await api('/api/ai/providers/remove','POST',{name}); if(r.ok){ msg('Provider removed.'); await loadProviders(); } else msg(r.error||'gagal'); }
async function loadStatus(){ const s=await api('/api/status'); document.getElementById('appRoot').classList.remove('hidden'); document.getElementById('loginBox').classList.add('hidden');
  document.getElementById('risk').innerText=s.risk||'-';
  document.getElementById('interval').innerText=s.interval||'-';
  document.getElementById('symbols').innerText=s.symbols||'-';
  document.getElementById('symbolMode').innerText=s.symbol_mode||'-';
  document.getElementById('aiMode').innerText=s.ai_mode||'-';
  document.getElementById('statusMsg').innerText=s.paused==='true'?'Bot paused':'Bot running';
}
function toggleTheme(){ const d=document.documentElement; const next=d.classList.contains('dark')?'light':'dark'; d.classList.remove('dark','light'); d.classList.add(next); localStorage.setItem('theme',next); if(next==='light'){ document.body.classList.remove('bg-slate-950','text-slate-100'); document.body.classList.add('bg-slate-50','text-slate-900'); } else { document.body.classList.remove('bg-slate-50','text-slate-900'); document.body.classList.add('bg-slate-950','text-slate-100'); } }
async function doLogin(){ const u=document.getElementById('loginUser').value.trim(); const p=document.getElementById('loginPass').value; const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({username:u,password:p})}); const j=await r.json(); if(j.ok){ document.getElementById('loginBox').classList.add('hidden'); document.getElementById('loginMsg').innerText='Login success.'; loadStatus(); } else { document.getElementById('loginMsg').innerText=j.error||'login failed'; } }
function msg(t){ const el=document.getElementById('statusMsg'); if(el) el.innerText=t; const toast=document.getElementById('toast'); if(toast){ toast.innerText=t; toast.classList.remove('hidden'); setTimeout(()=>toast.classList.add('hidden'),2500);} }
async function setTf(){ const v=document.getElementById('tf').value.trim(); if(!v) return; await api('/api/config','POST',{key:'INTERVAL',value:v}); document.getElementById('interval').innerText=v; msg('Timeframe set: '+v); }
async function setSyms(){ const v=document.getElementById('syms').value.trim(); if(!v) return; await api('/api/config','POST',{key:'SYMBOLS',value:v}); document.getElementById('symbols').innerText=v; msg('Symbols set.'); }
async function setMode(){ const v=document.getElementById('mode').value; await api('/api/config','POST',{key:'SYMBOL_MODE',value:v}); document.getElementById('symbolMode').innerText=v; msg('Symbol mode: '+v); }
async function setRisk(){ const v=document.getElementById('riskSel').value; await api('/api/config','POST',{key:'RISK_LEVEL',value:v}); document.getElementById('risk').innerText=v; msg('Risk: '+v); }
async function aiSave(){ const p=document.getElementById('provider').value.trim(); const t=document.getElementById('token').value.trim(); if(!p||!t){msg('Provider & token wajib.');return;} const r=await api('/api/ai/validate','POST',{provider:p,token:t}); if(!r.ok){msg('Validasi gagal: '+(r.error||''));return;} msg('AI token '+p+' divalidasi & tersimpan.'); }
async function aiDelete(){ const p=document.getElementById('provider').value.trim(); if(!p){msg('Isi provider.');return;} await api('/api/config','POST',{key:'AI_TOKEN_'+p.toUpperCase(),value:''}); msg('Delete '+p+'.'); }
async function setAiMode(){ const v=document.getElementById('aiModeSel').value; await api('/api/config','POST',{key:'AI_MODE',value:v}); document.getElementById('aiMode').innerText=v; msg('AI mode: '+v); }
async function botStart(){ await api('/api/config','POST',{key:'BOT_PAUSED',value:'false'}); msg('Bot resumed.'); }
async function botStop(){ await api('/api/config','POST',{key:'BOT_PAUSED',value:'true'}); msg('Bot paused.'); }
async function loadHistory(){ try { const r=await api('/api/history'); if(!r){ msg('history: no response'); return; } const rows=r.history||[]; const tb=document.getElementById('historyBody'); if(tb) tb.innerHTML=rows.map(x=>`<tr><td>${x[0]}</td><td>${x[1]}</td><td>${x[2]}</td><td>${x[3]}</td><td>${x[4]}</td></tr>`).join(''); if(!rows.length) msg('No trade history yet.'); } catch(e){ msg('history error: '+e); } }
async function loadAudit(){ const r=await api('/api/audit'); const rows=r.audit||[]; const tb=document.getElementById('auditBody'); if(tb) tb.innerHTML=rows.map(x=>`<tr><td class="text-[10px]">${x[0]}</td><td class="text-[10px]">${x[1]}</td><td class="text-[10px]">${x[2]}</td></tr>`).join(''); }
loadStatus();
loadProviders();
loadHistory();
loadAudit();
const es=new EventSource('/api/events'+(new URLSearchParams(location.search).get('t')?('?t='+new URLSearchParams(location.search).get('t')):''));
es.onmessage=(e)=>{try{const s=JSON.parse(e.data); document.getElementById('risk').innerText=s.risk||'-'; document.getElementById('interval').innerText=s.interval||'-'; document.getElementById('symbols').innerText=s.symbols||'-'; document.getElementById('symbolMode').innerText=s.symbol_mode||'-'; document.getElementById('aiMode').innerText=s.ai_mode||'-'; document.getElementById('statusMsg').innerText=s.paused==='true'?'Bot paused':'Bot running';}catch(_){}};
setInterval(loadHistory,10000);
setInterval(loadAudit,15000);