"""
Comprueba que su repositorio tiene la forma que el calificador espera.
Córranlo en la raíz de su repositorio antes de congelar:

    python verificar_entrega.py

No califica nada. Dice qué falta, qué está en el sitio equivocado y qué no se
parsea, con las mismas comprobaciones de entrada que hace el calificador. Lo
que aquí sale como FALTA, allá sale igual.
"""
import csv
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path.cwd()
DOCENTE = "javiersierra@usta.edu.co"
ASUNTO_SEMILLA = "polizas-api-v0"
ENTREGABLES = ["EQUIPO.md", "HALLAZGOS.md", "CONSULTAS.csv", "DICTAMEN_IA.md", "BITACORA_IA.md",
               "tests/test_ia_corregido.py", "tests/test_contrato.py", "requirements.txt",
               "README.md", "Dockerfile", ".dockerignore", ".env.example", "contar_consultas.py"]
COLUMNAS_CSV = ["endpoint", "estrategia", "n_polizas", "consultas_sql", "tiempo_ms"]
ESTRATEGIAS = {"lazy", "selectinload", "joinedload", "agregada"}
ENDPOINTS = {"/polizas", "/polizas/{id}", "/siniestros", "/resumen"}
BASURA = re.compile(r"(^|/)(venv|\.venv|env|source|__pycache__|\.pytest_cache|node_modules)(/|$)|\.db$|(^|/)\.env$")
FUERA = {"venv", ".venv", "env", "source", "__pycache__", ".git", ".pytest_cache", "node_modules", "build"}

informe = []


def ok(msg):
    informe.append(("OK", msg))


def falta(msg):
    informe.append(("FALTA", msg))


def aviso(msg):
    informe.append(("AVISO", msg))


def git(*args):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_bytes(*args):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def celdas(linea):
    return [c.strip() for c in re.split(r"(?<!\\)\|", linea.strip())[1:-1]]


def buscar(nombre):
    """Dónde está un archivo, a cualquier profundidad, fuera de venvs y .git."""
    hallados = []
    for p in RAIZ.rglob(Path(nombre).name):
        if any(parte in FUERA for parte in p.relative_to(RAIZ).parts):
            continue
        hallados.append(p.relative_to(RAIZ))
    return hallados


def comprobar_raiz():
    apps = [p for p in RAIZ.rglob("*.py")
            if not any(parte in FUERA for parte in p.relative_to(RAIZ).parts)
            and "FastAPI(" in p.read_text(encoding="utf-8", errors="replace")]
    if (RAIZ / "main.py").exists() and (RAIZ / "main.py") in apps:
        ok("main.py con la aplicación FastAPI está en la raíz")
    elif apps:
        falta(f"la aplicación está en {apps[0].relative_to(RAIZ)}; el servicio va en la RAÍZ, como main.py")
    else:
        falta("no se encuentra ningún archivo que instancie FastAPI(")


def comprobar_historia():
    if git("rev-parse", "--is-inside-work-tree") != "true":
        falta("esto no es un repositorio git (¿descargaron un .zip?)")
        return None
    commits = git("log", "--format=%H%x1f%ae%x1f%s", "--reverse") or ""
    semilla = None
    for linea in commits.splitlines():
        sha, correo, asunto = linea.split("\x1f")
        if correo == DOCENTE and asunto.startswith(ASUNTO_SEMILLA):
            semilla = sha
            break
    if not semilla:
        falta("la historia no contiene el commit del semilla: no clonaron el repositorio "
              "semilla (copiaron los archivos). Clónenlo y traigan su trabajo encima.")
        return None
    ok(f"la historia desciende del semilla ({semilla[:10]})")
    # la batería visible debe llegar intacta
    orig = git_bytes("show", f"{semilla}:tests/test_contrato.py")
    actual = (RAIZ / "tests/test_contrato.py")
    if orig is None or not actual.exists():
        falta("tests/test_contrato.py no existe")
    elif hashlib.sha256(orig).hexdigest() != hashlib.sha256(actual.read_bytes()).hexdigest():
        falta("tests/test_contrato.py fue modificado: debe llegar intacto")
    else:
        ok("tests/test_contrato.py intacto")
    # commits del grupo, después del semilla
    n = git("rev-list", "--count", f"{semilla}..HEAD")
    if n == "0":
        aviso("no hay ningún commit después del semilla todavía")
    return semilla


def comprobar_equipo(semilla):
    p = RAIZ / "EQUIPO.md"
    if not p.exists():
        return
    identidades = set()
    filas = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip().startswith("| ")]
    personas = 0
    for l in filas[1:]:
        c = celdas(l)
        if len(c) != 3 or not c[0] or c[0].startswith("<") or c[0].startswith("---"):
            continue
        personas += 1
        for ident in c[2].split(";"):
            m = re.search(r"<([^>]+)>", ident)
            if m:
                identidades.add(m.group(1).strip().lower())
    if not personas:
        falta("EQUIPO.md no tiene ninguna persona declarada")
        return
    ok(f"EQUIPO.md declara {personas} persona(s) y {len(identidades)} correo(s) git")
    if semilla:
        autores = git("log", "--format=%ae", f"{semilla}..HEAD") or ""
        no_declarados = sorted({a.lower() for a in autores.splitlines() if a} - identidades)
        if no_declarados:
            falta("identidades git sin declarar en EQUIPO.md: " + ", ".join(no_declarados)
                  + " (cada una cuenta como una persona extra)")
        else:
            ok("todas las identidades git de los commits están declaradas")


def comprobar_entregables():
    for nombre in ENTREGABLES:
        if (RAIZ / nombre).exists():
            continue
        otros = [h for h in buscar(nombre) if str(h) != nombre]
        if otros:
            falta(f"{nombre} está en {otros[0]} y debe estar en {nombre}")
        else:
            falta(f"falta {nombre}")
    presentes = [n for n in ENTREGABLES if (RAIZ / n).exists()]
    ok(f"{len(presentes)} de {len(ENTREGABLES)} entregables en su sitio")
    if not (RAIZ / "alembic").is_dir():
        falta("falta el directorio alembic/ con al menos una revisión")
    elif not list((RAIZ / "alembic" / "versions").glob("*.py")):
        falta("alembic/versions/ no tiene ninguna revisión")
    else:
        ok("alembic/ con revisión")


def comprobar_hallazgos():
    p = RAIZ / "HALLAZGOS.md"
    if not p.exists():
        return
    filas = [l for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*H\d+\s*\|", l)]
    malas = [l[:40] for l in filas if len(celdas(l)) != 8]
    if malas:
        falta(f"HALLAZGOS.md: {len(malas)} fila(s) sin ocho columnas (¿una tubería sin escapar?): {malas[0]}…")
    reales = [l for l in filas if len(celdas(l)) == 8 and "ejemplo de FORMATO" not in l
              and any(celdas(l)[1:])]
    if any("ejemplo de FORMATO" in l for l in filas):
        aviso("HALLAZGOS.md conserva la fila de ejemplo H1: bórrenla antes de entregar")
    if not 8 <= len(reales) <= 14:
        falta(f"HALLAZGOS.md tiene {len(reales)} hallazgos rellenados; se piden entre 8 y 14")
    else:
        ok(f"HALLAZGOS.md: {len(reales)} hallazgos con ocho columnas")
    secciones = re.findall(r"^## `?(/[\w/{}-]+)`?", p.read_text(encoding="utf-8"), re.M)
    if set(secciones) != ENDPOINTS:
        falta(f"HALLAZGOS.md · Parte C: se esperan las secciones {sorted(ENDPOINTS)}, hay {secciones}")


def comprobar_consultas():
    p = RAIZ / "CONSULTAS.csv"
    if not p.exists():
        return
    with p.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.reader(fh))
    if not filas or filas[0] != COLUMNAS_CSV:
        falta(f"CONSULTAS.csv: la cabecera debe ser exactamente {','.join(COLUMNAS_CSV)}")
        return
    datos = filas[1:]
    if len(datos) != 8:
        falta(f"CONSULTAS.csv tiene {len(datos)} filas de datos; se exigen 8 (4 endpoints × 2 tamaños)")
    vacias = [f for f in datos if len(f) == 5 and not f[1]]
    fuera = [f[1] for f in datos if len(f) == 5 and f[1] and f[1] not in ESTRATEGIAS]
    if vacias:
        falta(f"CONSULTAS.csv: {len(vacias)} fila(s) sin `estrategia` (eso es lo que se califica)")
    if fuera:
        falta(f"CONSULTAS.csv: estrategia fuera del vocabulario: {sorted(set(fuera))}")
    no_num = [f for f in datos if len(f) == 5 and not f[3].isdigit()]
    if no_num:
        falta(f"CONSULTAS.csv: {len(no_num)} fila(s) sin `consultas_sql` numérico")
    if not (vacias or fuera or no_num) and len(datos) == 8:
        ok("CONSULTAS.csv: 8 filas, vocabulario y conteos en orden")


def comprobar_dictamen():
    p = RAIZ / "DICTAMEN_IA.md"
    if not p.exists():
        return
    t = p.read_text(encoding="utf-8")
    defectos = re.split(r"^## Defecto\s+\d+\s*$", t, flags=re.M)[1:]
    if len(defectos) != 3:
        falta(f"DICTAMEN_IA.md declara {len(defectos)} defectos; deben ser 3")
        return
    incompletos = 0
    for d in defectos:
        for etq in ("Qué está mal", "Por qué es un defecto", "Cómo lo comprobamos", "Corrección"):
            m = re.search(r"\*\*" + etq + r"\*\*[^\n]*:\**\s*(.*)", d)
            if not m or not m.group(1).strip():
                incompletos += 1
    if incompletos:
        aviso(f"DICTAMEN_IA.md: {incompletos} sección(es) todavía vacía(s) en la misma línea del rótulo")
    if t.count("```") < 6:
        aviso("DICTAMEN_IA.md: se esperan bloques de código con la mutación y las dos salidas por defecto")
    ok("DICTAMEN_IA.md: 3 defectos con sus cuatro secciones")


def comprobar_bitacora():
    p = RAIZ / "BITACORA_IA.md"
    if not p.exists():
        return
    t = p.read_text(encoding="utf-8")
    secs = re.findall(r"^## (\w+)", t, re.M)
    if secs != ["Prompts", "Aceptado", "Rechazado"]:
        falta(f"BITACORA_IA.md: secciones {secs}; deben ser Prompts / Aceptado / Rechazado en ese orden")
        return
    # partir por la LÍNEA de encabezado: la cita de arriba también dice «## Rechazado»
    rechazado = re.split(r"^## Rechazado\s*$", t, flags=re.M)[1]
    filas = [l for l in rechazado.splitlines() if l.strip().startswith("|")][2:]
    if not any(sum(1 for c in celdas(l) if c) >= 3 for l in filas):
        aviso("BITACORA_IA.md: `## Rechazado` sin ninguna fila rellenada, y es la que se califica")
    else:
        ok("BITACORA_IA.md con las tres secciones y rechazos")


def comprobar_basura():
    tracked = (git("ls-files") or "").splitlines()
    malos = sorted({t for t in tracked if BASURA.search(t)})
    if malos:
        falta("archivos versionados que no deben estarlo (git rm --cached): " + ", ".join(malos[:6])
              + (" …" if len(malos) > 6 else ""))
    else:
        ok("nada de venv, __pycache__, .env ni *.db versionado")


def comprobar_ejecucion():
    py = sys.executable
    if not (RAIZ / ".env").exists() and (RAIZ / ".env.example").exists():
        shutil.copy(RAIZ / ".env.example", RAIZ / ".env")
        aviso(".env no existía: se copió .env.example, igual que hará el calificador")
    r = subprocess.run([py, "-m", "pytest", "tests/test_contrato.py", "-q", "-p", "no:cacheprovider"],
                       cwd=RAIZ, capture_output=True, text=True)
    resumen = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l]
    (ok if r.returncode == 0 else aviso)("pytest tests/test_contrato.py → " + (resumen[-1] if resumen else r.stderr[-200:]))
    if (RAIZ / "alembic.ini").exists():
        tmp = Path(tempfile.mkdtemp())
        r = subprocess.run([py, "-m", "alembic", "upgrade", "head"], cwd=RAIZ, capture_output=True, text=True,
                           env={**__import__("os").environ, "DATABASE_URL": f"sqlite:///{tmp / 'vacia.db'}"})
        if r.returncode == 0 and (tmp / "vacia.db").exists():
            ok("alembic upgrade head crea el esquema en una base vacía apuntada por DATABASE_URL")
        else:
            falta("alembic upgrade head falla sobre una base vacía (¿env.py no lee DATABASE_URL?): "
                  + (r.stderr.strip().splitlines() or ["sin salida"])[-1][:160])
        shutil.rmtree(tmp, ignore_errors=True)
    if shutil.which("docker") and subprocess.run(["docker", "info"], capture_output=True).returncode == 0:
        r = subprocess.run(["docker", "build", "-q", "-t", "verificar-entrega", "."], cwd=RAIZ,
                           capture_output=True, text=True)
        (ok if r.returncode == 0 else falta)("docker build " + ("construye" if r.returncode == 0
                                                                 else "falla: " + r.stderr.strip()[-200:]))
    else:
        aviso("Docker no disponible en esta máquina: no se comprueba el Dockerfile")


def main():
    print(f"verificando {RAIZ}\n")
    comprobar_raiz()
    semilla = comprobar_historia()
    comprobar_equipo(semilla)
    comprobar_entregables()
    comprobar_hallazgos()
    comprobar_consultas()
    comprobar_dictamen()
    comprobar_bitacora()
    comprobar_basura()
    comprobar_ejecucion()
    for estado, msg in informe:
        print(f"  {estado:<6} {msg}")
    n = sum(1 for e, _ in informe if e == "FALTA")
    print(f"\n{n} cosa(s) por resolver" if n else "\nTodo en su sitio. Lo que sigue es la calidad, y eso lo lee el docente.")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
