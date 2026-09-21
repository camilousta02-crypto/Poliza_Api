# polizas-api-v0

Servicio de gestión de pólizas de la Aseguradora Santo Tomás. Registra pólizas
y los siniestros que se les declaran, resume la cartera y puntúa el riesgo de
cada póliza con un modelo, guardando cada predicción.

## Instalación

```bash
pip install -r requirements.txt
```

El modelo entrenado (`modelo.pkl`) y la base de datos con datos de ejemplo
(`app.db`) vienen en el repositorio: no hay que configurar nada.

## Puesta en marcha

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

El mismo comando sirve en el servidor de producción. `--reload` es cómodo
porque recoge los cambios sin reiniciar a mano.

### En contenedor

```bash
docker build -t polizas-api .
docker run -p 8000:8000 polizas-api
```

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/polizas` | Crea una póliza, con sus siniestros si ya tiene |
| GET | `/polizas` | Lista las pólizas con sus siniestros |
| GET | `/polizas/{id}` | Consulta una póliza |
| PUT | `/polizas/{id}` | Actualiza una póliza |
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
```

```bash
curl -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"numero": "POL-2026-09001"}'
```

## Pruebas

```bash
pytest tests/test_api.py
```

## Utilidades

- `sembrar_datos.py` crea pólizas de ejemplo a través de la API.
- `contar_consultas.py` cuenta las sentencias SQL que emite cada endpoint.

## Notas

- Las claves están en `config.py` para que el equipo pueda probar sin configurar nada.
- La base de datos se crea sola al arrancar si no existe.
