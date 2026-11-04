# Tasks API (proyecto para aprender CI/CD)

API REST pequeña con FastAPI, usada para aprender GitHub Actions, Docker y despliegue continuo.

## Ejecutar en local
```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload
```
Documentación interactiva en http://127.0.0.1:8000/docs.

## Tests y linter
```
python -m pytest
python -m ruff check .
```

## Con Docker
```
docker build -t tasks-api .
docker run -p 8000:8000 tasks-api
```

## Con Docker Compose (API + PostgreSQL)
```
copy .env.example .env     # y cambia la contraseña
docker compose up -d --build
docker compose down        # para (los datos se conservan en el volumen)
docker compose down -v     # para y BORRA también los datos
```
Sin la variable `DATABASE_URL` la app usa SQLite, así que `uvicorn` en local sigue funcionando sin base de datos externa.

## Pipeline (GitHub Actions)
- **test:** ruff + pytest, en cada push y pull request.
- **docker:** construye y publica la imagen en GHCR (solo en `main`).
- **deploy:** avisa a Render para desplegar (solo en `main`).

`main` está protegida: los cambios entran mediante pull request con el check `test` en verde.
