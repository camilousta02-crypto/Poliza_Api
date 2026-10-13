# polizas-api

Servicio de gestión de pólizas de la Aseguradora Santo Tomás. Registra pólizas
y los siniestros que se les declaran, resume la cartera y puntúa el riesgo de
cada póliza con un modelo, guardando cada predicción.

## Configuración

La configuración se lee de variables de entorno (o de un archivo `.env`).
Las claves no están en el repositorio.

```bash
cp .env.example .env      # y cambie los valores de ejemplo
```

## Arranque local

```bash
python -m pip install -r requirements.txt
python -m alembic upgrade head        # crea el esquema en la base de DATABASE_URL
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

La base de datos no viene en el repositorio: la crea Alembic al aplicar las migraciones.

## En contenedor

```bash
docker build -t polizas-api .
docker run -p 8000:8000 polizas-api
curl localhost:8000/health
```

La imagen aplica las migraciones al arrancar y corre sin privilegios de root.
Sin volumen, los datos viven dentro del contenedor: se conservan con
`docker restart` pero se pierden al borrarlo. Para que persistan:

```bash
docker run -p 8000:8000 -v datos:/app/data polizas-api
```

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado del servicio y de la base de datos |
| POST | `/polizas` | Crea una póliza (201; 409 si el número existe; 422 si es inválida) |
| GET | `/polizas` | Lista las pólizas con sus siniestros |
| GET | `/polizas/{id}` | Consulta una póliza (404 si no existe) |
| PUT | `/polizas/{id}` | Actualiza una póliza, de forma parcial |
| POST | `/polizas/{id}/siniestros` | Declara un siniestro |
| GET | `/siniestros` | Lista los siniestros con su póliza |
| GET | `/resumen` | Siniestros y monto total por póliza |
| POST | `/score` | Puntúa el riesgo de una póliza y guarda la predicción |
| GET | `/predicciones` | Histórico de predicciones |

### Ejemplo

```bash
curl -X POST localhost:8000/polizas \
  -H "Content-Type: application/json" \
  -d '{"numero": "POL-2026-09001", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000,
       "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'

curl -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"numero": "POL-2026-09001"}'
```

## Pruebas

```bash
python -m pytest tests/test_contrato.py
```

## Utilidades

- `sembrar_datos.py` crea pólizas de ejemplo a través de la API.
- `contar_consultas.py` cuenta las sentencias SQL que emite cada endpoint y escribe `CONSULTAS.csv`.