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

## Con Kubernetes (Docker Desktop)
Activa Kubernetes en Docker Desktop (Settings > Kubernetes). Los manifiestos están en `k8s/`.
```
docker build -t tasks-api:local .
kubectl apply -f k8s/00-namespace.yaml
kubectl create secret generic postgres-credentials -n tasks --from-literal=POSTGRES_USER=tasks --from-literal=POSTGRES_PASSWORD=<contraseña> --from-literal=POSTGRES_DB=tasks
kubectl apply -f k8s/10-postgres.yaml -f k8s/20-api.yaml
kubectl port-forward svc/api 8080:80 -n tasks     # API en http://localhost:8080/docs
kubectl delete namespace tasks                    # limpiar todo
```
El Secret no está en el repo (es público): se crea con el comando de arriba.

## Pipeline (GitHub Actions)
- **test:** ruff + pytest, en cada push y pull request.
- **docker:** construye y publica la imagen en GHCR (solo en `main`).
- **deploy:** avisa a Render para desplegar (solo en `main`).

`main` está protegida: los cambios entran mediante pull request con el check `test` en verde.
