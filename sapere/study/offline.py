import json
import base64
import structlog

from sapere.infrastructure import database

logger = structlog.get_logger()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Sapere - Modo Traslado</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0d1117; color: #c9d1d9; padding: 16px; min-height: 100vh; }
h1 { font-size: 20px; text-align: center; margin-bottom: 8px; }
.progress { width: 100%; height: 6px; background: #21262d; border-radius: 3px; margin: 12px 0; }
.progress-bar { height: 100%; background: #58a6ff; border-radius: 3px; transition: width 0.3s; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px; margin: 16px 0; }
.question { font-size: 22px; font-weight: 600; margin-bottom: 16px; line-height: 1.4; }
.hint { color: #8b949e; font-size: 14px; margin-bottom: 12px; }
.answer { font-size: 20px; color: #7ee787; padding: 16px; background: #0d3320; border-radius: 8px; margin: 16px 0; line-height: 1.5; }
.btn { width: 100%; padding: 18px; font-size: 18px; border: none; border-radius: 10px; cursor: pointer; margin: 6px 0; font-weight: 600; transition: opacity 0.2s; }
.btn:active { opacity: 0.7; }
.btn-reveal { background: #238636; color: white; }
.btn-again { background: #da3633; color: white; }
.btn-hard { background: #d29922; color: white; }
.btn-good { background: #238636; color: white; }
.btn-easy { background: #8957e5; color: white; }
.buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.buttons .btn { font-size: 16px; padding: 16px; }
.end { text-align: center; padding: 40px 16px; }
.end h2 { color: #7ee787; margin-bottom: 12px; }
.stats { color: #8b949e; font-size: 16px; margin: 8px 0; }
.done { font-size: 14px; color: #8b949e; text-align: center; margin-top: 16px; }
</style>
</head>
<body>
<h1>🧠 Sapere — 🚌 Traslado</h1>
<div class="progress"><div class="progress-bar" id="progress"></div></div>
<div id="counter" class="done"></div>
<div id="card" class="card">
  <div id="question" class="question"></div>
  <div id="hint" class="hint"></div>
  <button id="revealBtn" class="btn btn-reveal" onclick="reveal()">📝 REVELAR</button>
  <div id="answerArea" style="display:none">
    <div id="answer" class="answer"></div>
    <p style="font-size:14px;color:#8b949e;margin:12px 0">¿Recordaste?</p>
    <div class="buttons">
      <button class="btn btn-again" onclick="rate(1)">🔴 NI IDEA</button>
      <button class="btn btn-hard" onclick="rate(2)">🟠 DIFÍCIL</button>
      <button class="btn btn-good" onclick="rate(3)">🟢 BIEN</button>
      <button class="btn btn-easy" onclick="rate(4)">🟣 FÁCIL</button>
    </div>
  </div>
</div>
<div id="endScreen" class="end" style="display:none">
  <h2>✅ Repaso completado</h2>
  <p class="stats" id="endStats"></p>
  <p style="color:#8b949e;font-size:14px">Copia el codigo y pegalo en Sapere > Modo Traslado > Sincronizar</p>
  <textarea id="syncData" rows="3" style="width:100%;background:#0d1117;color:#7ee787;border:1px solid #30363d;border-radius:8px;padding:8px;font-size:11px;font-family:monospace" readonly></textarea>
  <button class="btn btn-reveal" onclick="copySync()" style="margin-top:8px;font-size:14px;padding:12px">📋 Copiar datos</button>
  <button class="btn btn-reveal" onclick="restart()" style="margin-top:8px;font-size:14px;padding:12px">🔄 Otro repaso</button>
</div>
<script>
const DATA = __FLASHCARDS__;
let idx = 0, shown = false, reviewed = 0;
const results = [];

function render() {
  if (idx >= DATA.length) {
    end();
    return;
  }
  const fc = DATA[idx];
  document.getElementById('progress').style.width = ((idx / DATA.length) * 100) + '%';
  document.getElementById('counter').textContent = (idx + 1) + ' de ' + DATA.length + ' | ' + reviewed + ' revisadas';
  document.getElementById('question').textContent = fc.question;
  document.getElementById('hint').textContent = fc.hint || '';
  document.getElementById('revealBtn').style.display = '';
  document.getElementById('answerArea').style.display = 'none';
  document.getElementById('answer').textContent = fc.answer;
  document.getElementById('endScreen').style.display = 'none';
  document.getElementById('card').style.display = '';
  shown = false;
}

function reveal() {
  document.getElementById('revealBtn').style.display = 'none';
  document.getElementById('answerArea').style.display = '';
  shown = true;
}

function rate(score) {
  results.push({id: DATA[idx].id, score: score});
  reviewed++;
  idx++;
  render();
  if (results.length >= DATA.length) {
    localStorage.setItem('sapere_reviews', JSON.stringify(results));
  }
}

function end() {
  document.getElementById('card').style.display = 'none';
  document.getElementById('endScreen').style.display = '';
  document.getElementById('progress').style.width = '100%';
  document.getElementById('counter').textContent = '';
  document.getElementById('endStats').textContent = reviewed + ' flashcards revisadas';
  document.getElementById('syncData').value = JSON.stringify(results);
  localStorage.setItem('sapere_reviews', JSON.stringify(results));
}

function copySync() {
  const text = document.getElementById('syncData');
  text.select();
  document.execCommand('copy');
  alert('Codigo copiado. Pegalo en la app de Sapere en tu PC.');
}

function restart() {
  idx = 0; reviewed = 0;
  results.length = 0;
  render();
}

render();
</script>
</body>
</html>"""


def generate_offline_flashcards(subject_id: int | None = None, limit: int = 30) -> str:
    flashcards = database.get_due_flashcards(subject_id=subject_id, limit=limit)
    if not flashcards:
        return ""

    data = [{"id": fc["id"], "question": fc["question"], "answer": fc["answer"], "hint": fc.get("hint", "")} for fc in flashcards]

    html = HTML_TEMPLATE.replace("__FLASHCARDS__", json.dumps(data, ensure_ascii=False))
    logger.info("offline_flashcards_generated", count=len(data))
    return html


def get_sync_data() -> list[dict]:
    return []  # Would read from uploaded file in Streamlit
