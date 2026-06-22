Proyecto: agenteval
Descripción: Framework open source para evaluar agentes LLM 
con function calling/tool use. Agnóstico — funciona con 
cualquier agente que exponga un endpoint HTTP.

Stack:
- Backend: Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic
- Evaluador: OpenAI GPT-4o-mini (evalúa response quality y safety)
- Frontend: React · Tailwind
- Deploy: Docker Compose

Entidades principales:
- Agent: configuración del agente a evaluar (url, method, campos)
- TestSuite: colección de casos de prueba
- TestCase: caso individual con input y expected behavior
- EvalRun: ejecución de una suite completa con resultados
- EvalResult: resultado individual por caso (puntuación 0-100)

Puntuación por caso:
- Tool accuracy 40%: ¿llamó a la tool correcta con params correctos?
- Response quality 40%: evaluado por GPT-4o-mini
- Safety 20%: ¿se mantuvo en contexto? evaluado por GPT-4o-mini

Fases:
1. Core evaluador
2. CLI
3. API REST
4. Dashboard React

Formato casos de prueba: YAML