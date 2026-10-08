# Backend

FastAPI service. See the root README for the full guide.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload          # API docs: http://localhost:8000/docs
python -m app.ml.train --country RW    # rebuild dataset, retrain, rewrite outputs
```

Layout: `app/pipeline` (data), `app/ml` (training, validation, prediction), `app/services` (logic),
`app/api` (routers), `app/schemas` (Pydantic). Artefacts: `data/processed`, `models`, `outputs` (per country code).
