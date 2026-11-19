from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone

from app.core.auth import require_api_key
from app.core.db import get_db
from app.models.observation import Observation
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

router = APIRouter()

MOOD_FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mood check-in</title>
<style>
  :root { color-scheme: light dark; }
  body {
    font-family: system-ui, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    margin: 0;
    gap: 1.5rem;
    padding: 1rem;
    box-sizing: border-box;
  }
  h1 { font-size: 1.25rem; margin: 0; }
  .scores { display: flex; gap: 0.75rem; }
  button.score {
    width: 3.5rem;
    height: 3.5rem;
    border-radius: 50%;
    border: 2px solid currentColor;
    background: transparent;
    font-size: 1.25rem;
    font-weight: 600;
    cursor: pointer;
  }
  button.score:active { transform: scale(0.95); }
  #status { font-size: 0.95rem; min-height: 1.2em; }
</style>
</head>
<body>
  <h1>How's today, on a scale of 1-5?</h1>
  <div class="scores">
    <button class="score" data-score="1">1</button>
    <button class="score" data-score="2">2</button>
    <button class="score" data-score="3">3</button>
    <button class="score" data-score="4">4</button>
    <button class="score" data-score="5">5</button>
  </div>
  <div id="status"></div>

<script>
  const statusEl = document.getElementById('status');

  function getApiKey() {
    let key = localStorage.getItem('moodApiKey');
    if (!key) {
      key = prompt('Enter API key (saved on this device only):');
      if (key) localStorage.setItem('moodApiKey', key);
    }
    return key;
  }

  document.querySelectorAll('button.score').forEach(btn => {
    btn.addEventListener('click', async () => {
      const key = getApiKey();
      if (!key) return;
      statusEl.textContent = 'Saving...';
      try {
        const res = await fetch('/mood', {
          method: 'PUT',
          headers: {
            'Authorization': 'Bearer ' + key,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ score: Number(btn.dataset.score) })
        });
        if (res.ok) {
          statusEl.textContent = 'Saved mood: ' + btn.dataset.score;
        } else if (res.status === 401 || res.status === 403) {
          localStorage.removeItem('moodApiKey');
          statusEl.textContent = 'Invalid API key, try again.';
        } else {
          statusEl.textContent = 'Error: ' + res.status;
        }
      } catch (e) {
        statusEl.textContent = 'Network error.';
      }
    });
  });
</script>
</body>
</html>
"""

@router.get("/mood-form", response_class=HTMLResponse)
def mood_form():
    return MOOD_FORM_HTML

class Mood(BaseModel):
    score: int = Field(ge=1, le=5)
@router.put("/mood", dependencies=[Depends(require_api_key)])
def update_mood(mood: Mood, db: Session = Depends(get_db)):
    today = date.today()
    external_id = today.isoformat()
    existing = db.query(Observation).filter_by(source='mood', metric='score', external_id=external_id).one_or_none()
    if existing:
        existing.value_num = mood.score
    else:
        db.add(Observation(
            source='mood',
            metric='score',
            timestamp=datetime.now(timezone.utc),
            local_date=today,
            value_num=mood.score,
            unit='score',
            external_id=external_id
        ))
    db.commit() 

    