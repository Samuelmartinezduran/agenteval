# Architecture Decision Records

## Runs en background con BackgroundTasks de FastAPI
- **Decisión:** `POST /runs` inserta el run en estado `running`, lo ejecuta en un `BackgroundTask` (threadpool) y el cliente hace polling; sin cola externa (Celery/RQ).
- **Reason:** Evita timeouts HTTP con suites grandes sin añadir infraestructura; una cola externa sería sobreingeniería para el volumen actual. El task abre su propia sesión de BD.
- **Source:** Agent assumption

## Ciclo de vida del run: running / completed / failed
- **Decisión:** Columna `status` en `eval_runs` con esos tres valores, más `finished_at` y `error` (fallo a nivel de run). Los runs históricos migran como `completed`.
- **Reason:** El frontend necesita distinguir "en curso" de "terminado" para el polling; los errores por caso ya se guardan en `eval_results.error`.
- **Source:** Agent assumption

## Concurrencia limitada en el runner (default 5)
- **Decisión:** `run_suite` acepta `concurrency` (semáforo asyncio), expuesto como `--concurrency` en la CLI y `AGENTEVAL_CONCURRENCY` en la API.
- **Reason:** `asyncio.gather` sin límite disparaba todos los casos a la vez → rate limits del agente y del juez garantizados en suites grandes.
- **Source:** Agent assumption

## Juez OpenAI: una sola llamada LLM por caso + retry
- **Decisión:** `Judge.score_case()` puntúa quality y safety juntos; `OpenAIJudge` lo resuelve en una única llamada JSON. Retry con backoff exponencial (3 intentos) ante 429/red/5xx.
- **Reason:** Mitad de coste y latencia por caso; los errores transitorios del proveedor no deben marcar el caso como fallido. La interfaz de dos métodos se conserva para jueces custom.
- **Source:** Agent assumption

## Matchers en expected.params: contains y regex
- **Decisión:** Un valor esperado puede ser `{contains: "texto"}` o `{regex: "patrón"}` (dict de una sola clave reservada); cualquier otro valor se compara por igualdad normalizada.
- **Reason:** La igualdad exacta era demasiado rígida para params generados por un LLM ("Madrid" vs "Madrid, España") sin necesitar un mini-lenguaje de asserts.
- **Source:** Agent assumption

## Frontend con react-router-dom
- **Decisión:** Navegación con rutas (`/`, `/runs/:id`, `/runs/:id/compare/:otherId`) en lugar de estado local, con fallback SPA en nginx.
- **Reason:** URLs compartibles y enlazables a un run concreto; es la librería estándar de routing en React.
- **Source:** Agent assumption

## Makefile: PYTHONPATH explícito en vez de depender del editable install
- **Decisión:** `run-cli` y `api` pasan `PYTHONPATH` con los `src` de ambos paquetes y usan `python -m` (igual que los tests con `pythonpath` de pytest); `fix-pth` queda como best-effort.
- **Reason:** En macOS, uv re-marca los `.pth` editables como ocultos en **cada** `uv run` (incluso con `--no-sync`) y CPython los ignora; además el `chflags` puede fallar silenciosamente. Con PYTHONPATH los targets funcionan siempre.
- **Source:** User instruction

## Comparación de runs por case_name
- **Decisión:** `GET /runs/{id}/compare/{other_id}` empareja resultados por `case_name` y devuelve deltas; en CLI, `--baseline <json>` compara contra un run previo guardado con `--output`.
- **Reason:** Responde a "¿mi agente mejoró o empeoró?" sin introducir un concepto nuevo de baseline persistido; el nombre del caso ya es el identificador estable de la suite.
- **Source:** User instruction (plan aprobado)
