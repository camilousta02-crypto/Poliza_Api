# Taller del Corte II — «Pólizas API v0»

**Python para Desarrollo de APIs e IA** · USTA · Estadística · 2026-II · Código 28549
**Cubre:** módulos 6 a 11 · **Peso:** 60 % del Corte II (18 % de la nota definitiva)
**Grupos:** de 1 a 3 personas · **Publicado:** lun 21 sep 2026
**Congelado del repositorio:** vie 16 oct 2026, 23:59 · **Sustentación:** sesiones de la tercera y cuarta semana de octubre

---

## 1. De qué se trata

Reciben un servicio web que **funciona pero está mal hecho**: `polizas-api-v0`, el servicio con el
que la Aseguradora Santo Tomás gestiona su cartera de pólizas y los siniestros que se le declaran,
y que además puntúa el riesgo de cada póliza con un modelo y **guarda cada predicción**. Arranca,
responde, persiste en SQLite, trae tests y hasta un `Dockerfile`. También arrastra una colección de
decisiones equivocadas, todas del tipo que los módulos 6 a 11 enseñan a no tomar.

El trabajo tiene cinco partes: **diagnosticar** lo que está mal, **arreglarlo** bajo restricciones,
**decidir y medir** un punto donde la intuición falla, **auditar unos tests escritos por IA**, y
**defender** lo que hicieron.

### Lo que se evalúa, y lo que no

| Sí se evalúa | No se evalúa |
|---|---|
| Que sepan nombrar lo que ven y por qué está mal | Que el código sea largo |
| Que la decisión técnica esté justificada y medida | Que hayan añadido funcionalidades extra |
| Que sepan demostrar que algo funciona, y que un test lo demuestre | Que el servicio tenga interfaz gráfica |
| Que cada integrante responda por el repositorio | La elegancia del formateo |

Cualquier cosa que añadan más allá de lo pedido no suma puntos y sí ocupa el tiempo de la defensa.
La consigna es **hacer lo pedido y saber por qué**.

---

## 2. Reglas del juego

### 2.1 La IA está permitida — y es parte de lo evaluado

Pueden usar cualquier asistente de IA, sin restricción y para cualquier parte. A cambio, dos
obligaciones:

1. **Bitácora obligatoria** (`BITACORA_IA.md`). Registran los prompts relevantes, qué aceptaron y
   —esto es lo que se califica— **qué rechazaron y con qué argumento**. Una bitácora que solo
   lista prompts aceptados vale la mitad.
2. **La Parte D audita a la IA.** Se les entrega un archivo de tests generado por IA que está en
   verde y no demuestra nada. Encontrar por qué es el ejercicio.

Bitácora ausente o falsificada: **−15 puntos**.

El taller está diseñado sabiendo que van a usar IA. Las partes A y B las van a resolver más rápido
con ayuda, y está bien: ese tiempo es para las partes C, D y E, donde la IA no puede contar
consultas en su máquina, no audita bien sus propios tests, y no se sienta en la sustentación.

### 2.2 Entrega

- **Un repositorio en GitHub por grupo**, clonado del semilla, con historia real de commits. No se
  reciben `.zip`: el criterio C2 califica `git log` por persona.
- **Clonen el repositorio semilla; no descarguen carpetas del sitio del curso.** El calificador
  comprueba que el commit del semilla está en la historia de su repositorio. Si no está, C2 y la
  reproducción de la evidencia de la Parte A no se pueden medir.
- El enlace se entrega por Moodle antes del **vie 16 oct, 23:59**. A esa hora se lee el remoto de
  cada grupo y se registra el SHA del último commit; **lo que se califica es ese commit**, no lo que
  haya después.
- Entrega fuera de plazo: no se recibe.
- El repositorio debe arrancar siguiendo **su propio README**, en una máquina limpia, con
  `uvicorn` y con `docker run`. Si no arranca de ninguna de las dos maneras, la nota tiene tope de 60.
- **Antes de congelar, corran `python verificar_entrega.py`** en la raíz de su repositorio. Hace
  las mismas comprobaciones de entrada que el calificador —servicio en la raíz, entregables en la
  raíz, plantillas parseables, historia que desciende del semilla, identidades declaradas— y les
  dice qué falta. Lo que ese guion reporta, el calificador lo va a reportar igual.

### 2.3 Grupos y responsabilidad individual

De 1 a 3 personas. Esta agrupación **es independiente de los equipos del proyecto integrador** y
no crea equipo de proyecto. Un grupo de una persona hace el mismo taller; no hay versión reducida.

Declaren el equipo en **`EQUIPO.md`** (plantilla en el repositorio): nombre, correo y **todas** las
identidades con las que hacen commits (nombre y correo tal como salen en `git log`). El calificador
agrupa los commits por persona con esa tabla; una identidad no declarada cuenta como una persona
extra que no está en el grupo.

Repartan el trabajo como quieran, pero **cualquier integrante puede ser preguntado por cualquier
línea del repositorio**. El 30 % de la nota es individual, y se mide dos veces:

**Control presencial — sesión de la segunda semana de octubre, 10 minutos, individual, sin IA y
sin consultar a los compañeros.** Papel y lápiz; no hace falta computador.

A cada estudiante se le entrega **un endpoint con relaciones que no ha visto**, de cinco a diez
líneas, y escribe:

1. **Estrategia de carga:** `lazy`, `selectinload`, `joinedload` o `agregada`.
2. **Predicción:** cuántas consultas SQL esperaría con 10 registros y con 10 000, y por qué.
3. **Justificación**, dos o tres frases: *por qué* esa estrategia y no otra.

No se pide reproducir nada de lo que entregaron: se pide **llevar el criterio de la Parte C a un
caso nuevo**. Los integrantes de un grupo reciben endpoints distintos.

Lo que se califica es la justificación y la predicción. Acertar la etiqueta sin saber justificarla
vale poco; equivocarse de etiqueta con un razonamiento que revela comprensión vale bastante. Si
hicieron la Parte C ustedes, esto les sale en cinco minutos.

**La nota individual acota la grupal.** La nota final de cada estudiante es:

> `nota = min( 0,70 × grupal + 0,30 × individual ,  individual + 15 )`

Es decir: un buen repositorio no compensa no entender lo que hay dentro. Si su nota individual es
40, la final no pasa de 55 por bueno que sea el trabajo del grupo. Si ambas van parejas, la cota no
se activa y no cambia nada.

---

## 3. El artefacto

```bash
git clone https://github.com/JotaMao1985/polizas-api-v0 polizas-api
cd polizas-api
cat README.md          # léanlo: forma parte del problema
```

Contiene un servicio de gestión de pólizas con **nueve endpoints** —pólizas, siniestros, resumen,
puntuación e histórico de predicciones—, un modelo serializado de juguete (`modelo.pkl`), una base
de datos SQLite, tests, un `Dockerfile` y un README. **Arranca.** Ninguno de los defectos impide que
corra: por eso hay que buscarlos.

No se dice cuántos defectos hay.

---

## 4. Las cinco partes

### Parte A — Diagnóstico

Encuentren los defectos y documéntenlos en **`HALLAZGOS.md`**, una fila por defecto, con este
formato exacto:

```markdown
| ID | Síntoma observable | Causa | Módulo · Sección | SHA donde se observa | Comando de evidencia | Salida obtenida | Corrección aplicada |
|----|--------------------|-------|------------------|----------------------|----------------------|-----------------|---------------------|
| H1 | *(ejemplo de FORMATO, no un defecto de este repositorio)* `GET /health` responde sin cabecera `Cache-Control` | El handler no declara política de caché | M6 · 5. Routing y CRUD | `v0-semilla` | `curl -sI localhost:8000/health \| grep -ci cache-control` | `0` | Se añade la cabecera en la respuesta |
```

Reglas:

- **`Módulo · Sección` debe citar una sección que exista** en el material de los módulos 6 a 11,
  con su título tal como aparece en el menú lateral. El calificador lo verifica contra los archivos
  del curso; una cita inventada anula la fila.
- **`SHA donde se observa`.** El síntoma se observa en el repositorio **roto**, y la Parte B lo
  repara. Si el calificador ejecutara su comando sobre el commit final no vería nada. Declaren el
  commit donde el defecto todavía vive —normalmente `v0-semilla`, la etiqueta del repositorio tal
  como se lo entregamos— y el calificador hace *checkout* ahí para reproducirlo.
- **`Comando de evidencia` debe ser ejecutable y reproducible.** El calificador lo corre sobre ese
  commit con el servicio levantado. Escríbanlo contra `localhost:8000`: el puerto lo sustituye el
  calificador. Si la evidencia es un comando `docker`, también vale: se reproduce cuando hay Docker
  en la máquina que califica, y si no lo hay pasa a revisión manual sin restar.
- **`Salida obtenida` es literal**, copiada de su terminal. No parafraseada. **Se compara con la
  salida real**, normalizando solo puertos, fechas y rutas absolutas. Una salida inventada se
  detecta.
- **Entre 8 y 14 hallazgos.** Una fila que no corresponda a un defecto real **resta la mitad** de
  lo que suma una correcta. El máximo se alcanza con precisión, no con volumen.
- **Si el comando lleva `|`, escríbanlo `\|`.** Sin escapar, Markdown lo lee como separador de
  columna y la fila queda con nueve campos: el parser la rechaza.
- Un hallazgo sin evidencia ejecutable no cuenta.

### Parte B — Refactor con restricciones

Arreglen el servicio. Las restricciones no son sugerencias; el calificador las comprueba:

| # | Restricción | Módulo |
|---|---|---|
| B1 | El entorno es reproducible: `requirements.txt` con versiones fijadas; `.env.example` con valores de ejemplo **con los que el servicio arranca** (el calificador lo copia a `.env` si no hay `.env`); sin secretos versionados; `.gitignore` que cubre `.env`, `*.db` y el entorno virtual, y nada de eso sigue en el índice | M1 · M8 |
| B2 | La configuración se lee con `BaseSettings` desde `.env`; la función que la entrega lleva `lru_cache` y se inyecta con `Depends`; **la app honra la variable `DATABASE_URL`** | M8 |
| B3 | La sesión es **por petición**: `database.get_db` es un generador con `yield` que cierra la sesión; no existe ninguna sesión a nivel de módulo; toda ruta que toca la base recibe la sesión con `Depends(get_db)` | M8 · M9 |
| B4 | Modelos con SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped`, `mapped_column`, `relationship`); `PRAGMA foreign_keys` activo en SQLite; esquemas de salida con `from_attributes=True` | M9 |
| B5 | Existe `alembic/` con al menos una revisión; `alembic/env.py` toma la URL de `DATABASE_URL`; `alembic upgrade head` sobre una base vacía crea el esquema; `create_all` desaparece del arranque | M9 |
| B6 | `response_model` en **todas** las rutas; 201 al crear, 404 si no existe, 409 si el número de póliza está repetido, 422 si la entrada es inválida; el `PUT` es parcial y no destruye lo que no se envió | M6 |
| B7 | Los validadores de campo **devuelven** el valor; el campo anidado de siniestros se tipa con un `BaseModel`; hay un `model_validator` que exige `fecha_fin` posterior a `fecha_inicio`; las restricciones van en `Field` | M7 |
| B8 | `tests/test_contrato.py` llega intacto y pasa; los tests propios sustituyen la sesión con `app.dependency_overrides` sobre una base temporal; `pytest` pasa dos veces seguidas; la base de la aplicación no cambia al correrlos | M10 |
| B9 | `Dockerfile` multietapa sobre `python:3.11.9-slim-bookworm`, `.dockerignore`, usuario no root, `HEALTHCHECK`, `CMD` sin `--reload` y con `--host 0.0.0.0`; `docker run -p 8000:8000` responde en `/health` **desde el host** | M11 |
| B10 | Existe `GET /health` que responde 200 e indica si la base de datos responde | M6 · M9 |

**El contrato de rutas no se cambia.** Estas son las rutas y los verbos que el calificador va a
golpear; renombrarlas o cambiarles el verbo hace fallar los checks:

| Verbo | Ruta | Devuelve |
|---|---|---|
| POST | `/polizas` | **201** con la póliza creada · 422 si la entrada es inválida · **409** si el número ya existe |
| GET | `/polizas` | 200, cada póliza con sus siniestros |
| GET | `/polizas/{id}` | 200 · **404** si no existe |
| PUT | `/polizas/{id}` | 200 con la póliza actualizada · 404 · 422; **parcial** |
| POST | `/polizas/{id}/siniestros` | **201** · **404** si la póliza no existe · 422 |
| GET | `/siniestros` | 200, cada siniestro con su póliza |
| GET | `/resumen` | 200, número de siniestros y monto total **por póliza** |
| POST | `/score` | 200 con la puntuación · 404 si la póliza no existe · 422; **registra** la predicción |
| GET | `/predicciones` | 200, cada predicción con el `numero` de su póliza y su `puntaje` |
| GET | `/health` | 200 · **hay que crearlo** |

Pueden añadir rutas si lo justifican; no pueden quitar ni renombrar estas.

**El contrato de datos tampoco.** La batería oculta arranca su servicio con una base de datos
vacía y espera dos cosas de su repositorio:

- La aplicación lee la ruta de la base de `DATABASE_URL` (restricción B2): con esa variable
  puesta, `uvicorn main:app` arranca contra esa base y no contra `app.db`.
- `alembic upgrade head` crea el esquema en esa base: `alembic/env.py` toma la URL de `DATABASE_URL`, igual que la aplicación (restricción B5).
- Los modelos se siguen llamando `modelos.Poliza`, `modelos.Siniestro` y `modelos.Prediccion`, la
  aplicación sigue siendo `main:app`, y la dependencia que entrega la sesión se llama
  `database.get_db`: la batería visible la sustituye para aislarse, igual que harán sus tests.
- Las respuestas conservan los nombres de campo de la entrada (`numero`, `asegurado`, `tipo`,
  `prima`, `fecha_inicio`, `fecha_fin`, `siniestros`) más el `id`; `/score` devuelve `numero`,
  `puntaje` en [0, 1] y `alto_riesgo`.

Dentro de esos límites el modelado es suyo: qué columnas, qué cascadas, dónde vive la lógica del
puntaje y del resumen es justo lo que califica C5.

En `tests/test_contrato.py` hay una batería de doce tests. La mayoría están **en rojo** sobre el
repositorio tal como se entrega y **todos deben pasar al terminar**. Que pasen es el mínimo, no
la meta: hay criterios de rúbrica que los tests no ven. **No modifiquen ni borren esos tests**: se
comprueba que el archivo llega intacto.

### Parte C — Decisión medida: cómo se cargan las relaciones

Cuatro endpoints del servicio devuelven datos que viven en más de una tabla:

| Endpoint | Qué devuelve |
|---|---|
| `/polizas` | Todas las pólizas, cada una con la lista de sus siniestros |
| `/polizas/{id}` | Una póliza con sus siniestros |
| `/siniestros` | Todos los siniestros, cada uno con el número de su póliza |
| `/resumen` | Por póliza: cuántos siniestros tiene y cuánto suman |

Para cada uno: decidan **cómo debe cargarse la relación**, déjenlo en el código, y
**demuéstrenlo contando las consultas SQL** que el servicio emite. El vocabulario es cerrado —se
parsea, escríbanlo exactamente así:

| Columna | Valores admitidos |
|---|---|
| `estrategia` | `lazy` · `selectinload` · `joinedload` · `agregada` |

Entregan **`CONSULTAS.csv`** con estas columnas exactas:

```csv
endpoint,estrategia,n_polizas,consultas_sql,tiempo_ms
/ejemplo,selectinload,10,2,3.1
/ejemplo,selectinload,2000,2,148.7
```

`/ejemplo` no existe: la fila muestra el **formato**, no una respuesta.

Cada endpoint con **dos tamaños**: 10 pólizas y 2000 pólizas, cada una con tres siniestros.

**El semilla trae `contar_consultas.py` funcionando**: siembra la base con el tamaño pedido a
través de la propia API, levanta la aplicación en proceso, cuenta cada sentencia SQL que ejecuta
el motor y escribe el CSV con las cinco columnas. Lo que no hace —y es lo que se califica— es
rellenar `estrategia`, ni explicar los números. Pueden modificarlo; si lo hacen, díganlo en
`HALLAZGOS.md`.

**Se califica el número de consultas, no el tiempo.** El conteo es determinista y el calificador lo
reproduce sobre su commit; el tiempo cambia de máquina en máquina y solo sirve para su
interpretación.

Y un párrafo por endpoint en **`HALLAZGOS.md`** (sección «Parte C») que explique **las consultas
que obtuvieron ustedes**: por qué ese número, por qué cambia o no cambia entre 10 y 2000. Se
califica la coherencia entre la estrategia, la que quedó en el código y la explicación de los
números.

> Aviso: la regla «cargar todo de una vez es más eficiente» falla en más de un caso, y de dos
> maneras distintas. En uno, seguirla da peor rendimiento. En otro, el código la incumple y **la
> medición dice que da exactamente igual**. Los dos cuentan, y el segundo solo se responde bien
> midiendo primero y decidiendo después. Cuenten antes de decidir.

### Parte D — Auditoría de los tests propuestos por la IA

En el repositorio hay un archivo **`ia_tests_propuesta.py`**: una batería de tests generada por un
asistente de IA para este mismo servicio. Se ejecuta con `pytest ia_tests_propuesta.py` y **está en
verde**. Está comentada, es legible y **tiene tres defectos**: hay tests que no pueden fallar, tests
que no prueban lo que dicen probar y tests que unas veces pasan y otras no.

Entregan **`DICTAMEN_IA.md`**:

```markdown
## Defecto 1
- **Qué está mal:**
- **Por qué es un defecto** (citando módulo · sección):
- **Cómo lo comprobamos:** (la mutación que introdujeron, el test original en verde y el corregido en rojo, con su salida)
- **Corrección:**
```

Más **`tests/test_ia_corregido.py`** con la batería corregida, que debe pasar sobre su servicio.

El peso está en **«cómo lo comprobamos»**, y aquí la comprobación tiene una forma concreta: **una
mutación**. Introduzcan a propósito un defecto en el servicio —un 404 que deja de devolverse, un
`commit` que se quita, un validador que acepta lo que no debe—, muestren que el test original
sigue en verde y que el corregido se pone en rojo, y vuelvan a dejar el servicio como estaba.
Afirmar que un test es malo no vale; demostrar que no detecta nada, sí.

El calificador hace lo mismo con tres mutaciones que ustedes no ven: sus tests corregidos deben
pasar sobre el código sano y fallar con cada mutación.

### Parte E — Bitácora y sustentación

**`BITACORA_IA.md`**, con estas secciones obligatorias: `## Prompts`, `## Aceptado`,
`## Rechazado`. En `## Rechazado` va lo que se califica: qué les propuso la IA que no aceptaron, y
por qué. Es el único apartado de la bitácora con peso propio.

**Sustentación: 12 minutos** (grupos de una persona: 9). Los grupos se reparten por sorteo entre
las dos sesiones; el repositorio se congela para todos el mismo día.

- **4 min — demo en vivo, en Docker.** `docker build`, `docker run -p`, `curl /health`, un
  `POST /polizas` que devuelve 201, y después **`GET /polizas` dos veces: tras `docker restart` y
  tras borrar el contenedor y levantar otro desde la misma imagen**. Lo que pase con los datos en
  cada caso, tienen que poder explicarlo. Sin diapositivas.
- **8 min — preguntas dirigidas.** Se pregunta a **un integrante concreto** por **una línea
  concreta** de su repositorio, al menos una pregunta por integrante. Todos deben poder responder
  por todo.

---

## 5. Qué se entrega — lista de verificación

En la raíz del repositorio:

- [ ] El servicio corregido, que arranca siguiendo su propio README, con `uvicorn` y con `docker run`
- [ ] `EQUIPO.md` — integrantes e identidades git
- [ ] `HALLAZGOS.md` — tabla de la Parte A + sección «Parte C»
- [ ] `CONSULTAS.csv` — Parte C, 4 endpoints × 2 tamaños = 8 filas
- [ ] `contar_consultas.py` — con las modificaciones que hayan necesitado
- [ ] `DICTAMEN_IA.md` — Parte D
- [ ] `tests/test_ia_corregido.py` — Parte D
- [ ] `BITACORA_IA.md` — Parte E
- [ ] `alembic/` con su revisión, `Dockerfile`, `.dockerignore`, `.env.example`
- [ ] `requirements.txt` con versiones fijadas
- [ ] `README.md` actualizado con el arranque real, local y en contenedor

Las cinco plantillas vienen en `plantillas/` **dentro del repositorio semilla**. Cópienlas a la
raíz y rellénenlas; no las reescriban desde cero: traen resueltos detalles de formato que el parser
exige. **`python verificar_entrega.py` les dice si algo quedó en el sitio equivocado.**

---

## 6. Rúbrica — 100 puntos

**Nota del taller = min( 0,70 × grupal + 0,30 × individual , individual + 15 )**, con la nota
individual repartida así:

| # | Componente individual | Pts |
|---|---|---:|
| I1 | Sustentación dirigida, sesiones de la tercera y cuarta semana de octubre | 50 |
| I2 | Control presencial, sesión de la segunda semana de octubre: un endpoint nuevo, sin IA | 30 |
| I3 | Contribución trazable al repositorio (`git log` propio, con las identidades de `EQUIPO.md`) | 20 |

Escala por criterio: **4 Excelente (100 %) · 3 Competente (75 %) · 2 En desarrollo (50 %) ·
1 Insuficiente (25 %) · 0 Ausente o no verificable.**

| # | Criterio | Pts | Nivel 4 se ve así |
|---|---|---:|---|
| C1 | Entorno y configuración (M1 · M8) | 8 | Versiones fijadas; instalación limpia; sin secretos; `.gitignore` correcto; `Settings` con caché y `.env.example` |
| C2 | Higiene de Git y trazabilidad | 7 | Una persona por integrante con ≥ 2 commits sustantivos cada una; mensajes que describen el cambio |
| C3 | Diagnóstico (Parte A) | 15 | Todos los defectos hallados, cada uno con síntoma, causa, cita real al material y evidencia reproducible |
| C4 | Contratos HTTP y validación (M6 · M7) | 12 | `response_model` en todo; 201/404/409/422; `PUT` parcial; validadores que devuelven; submodelos tipados; coherencia de fechas |
| C5 | Persistencia e inyección (M8 · M9) | 15 | Sesión por petición; claves foráneas activas; Alembic aplica en limpio; `from_attributes`; modelado con responsabilidades claras |
| C6 | Tests (M10) | 10 | Batería visible verde e intacta; tests propios aislados con `dependency_overrides`; dos corridas iguales; la base de la app no cambia |
| C7 | Decisión medida sobre la carga de relaciones (Parte C) | 10 | Las 4 estrategias defendibles; conteos reproducibles; la interpretación explica **sus** números |
| C8 | Auditoría de los tests de la IA (Parte D) | 10 | Los 3 defectos, cada uno con una mutación demostrada; tests corregidos que detectan las mutaciones del calificador |
| C9 | Contenedor (M11) | 9 | Construye; responde desde el host; imagen sin `.env` ni base de datos; no root; `HEALTHCHECK`; multietapa con base fijada |
| C10 | Bitácora de IA (Parte E) | 4 | Rechazos argumentados y localizables, no solo prompts aceptados |
| | **Total** | **100** | |

**Penalizaciones:** bitácora ausente o falsificada −15 · repositorio que no arranca siguiendo su
propio README ni con `uvicorn` ni con `docker run`, tope de 60 · entrega fuera del congelado, no
se recibe.

---

## 7. Cómo se califica

72 de los 100 puntos los resuelve un **calificador automático** que se corre sobre su repositorio:
lo clona en el SHA congelado, crea un entorno limpio, instala sus dependencias, aplica sus
migraciones sobre una base vacía, corre una batería de tests que ustedes no ven, levanta su
servicio y le pega, construye y arranca su imagen de Docker, cuenta las consultas de la Parte C,
muta su servicio para ver si sus tests lo notan, analiza la estructura de su código y ejecuta los
comandos de evidencia que declararon. Los 28 restantes —la calidad del diagnóstico, del modelado,
de la interpretación y del dictamen— los lee el docente.

Reciben `reporte_<grupo>.md` con **la nota de cada criterio y la evidencia que la sustenta**: el
comando ejecutado y su salida literal. Es auditable: si creen que un check está mal, se revisa
contra esa evidencia.

Tres consecuencias prácticas:

- **Los formatos son rígidos porque se parsean.** Una tabla torcida en `HALLAZGOS.md` no se
  «entiende igual»: se rechaza indicando la línea. Usen las plantillas.
- **La estructura también se comprueba.** El servicio y los entregables van en la raíz, y la
  historia desciende del semilla. `verificar_entrega.py` se lo dice antes que el calificador.
- **Que el calificador no pueda medir algo no es un aprobado.** Sale marcado como no verificable y
  pasa a revisión del docente; si tampoco así puede sustentarse, cuenta 0.
