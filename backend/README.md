# DEMOCRAC.IA (PEIRS) — Backend Core

**Predictive Electoral Integrity & Risk System**

Sistema de inteligencia electoral OSINT con enjambre de agentes de IA orquestados por LangGraph.

## Quick Start

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. (Opcional) Configurar Claude para generación de reportes con LLM
export ANTHROPIC_API_KEY="sk-ant-..."

# 3a. Ejecutar como API
uvicorn app:app --reload --port 8000

# 3b. Ejecutar análisis CLI directo
python app.py VEN    # Venezuela
python app.py NIC    # Nicaragua
python app.py GTM    # Guatemala
python app.py URY    # Uruguay
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check del sistema |
| `GET` | `/api/countries` | Lista de países disponibles |
| `POST` | `/api/analyze` | Ejecuta pipeline completo |
| `GET` | `/api/report/{run_id}` | Obtiene reporte completo (JSON) |
| `GET` | `/api/report/{run_id}/markdown` | Obtiene reporte en Markdown |

### Ejemplo: Ejecutar análisis

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"country_code": "VEN"}'
```

Respuesta:
```json
{
  "run_id": "uuid-...",
  "country": "Venezuela",
  "risk_score": 87.2,
  "risk_level": "critical",
  "violation_count": 7,
  "status": "completed"
}
```

## Arquitectura: Pipeline de Agentes

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│  Agente 1   │───▶│    Agente 2      │───▶│    Agente 3     │───▶│    Agente 4      │
│  OSINT      │    │  Político-Digital │    │  Legal (RAG)    │    │  Report Gen      │
│  Ingestion  │    │  Analyst          │    │  Compliance     │    │  VIP Writer      │
└─────────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘
      │                    │                       │                       │
      ▼                    ▼                       ▼                       ▼
  PostgreSQL           Neo4j              Pinecone/Qdrant            LaTeX/PDF
  (context)          (grafos)             (vector DB)              (reportes)
```

## Estado actual vs Producción

| Componente | Ahora (v0.1) | Producción |
|------------|-------------|------------|
| Agente 1 - OSINT | Datos mock | APIs Freedom House, V-Dem, Playwright scraping |
| Agente 2 - Político | Datos mock | Neo4j, APIs sociales, análisis NLP |
| Agente 3 - Legal | Reglas estáticas | RAG con Vector DB + 300 documentos EOS |
| Agente 4 - Reporte | Templates Markdown | Claude LLM + exportación LaTeX/PDF |
| Base de datos | Diccionarios en memoria | PostgreSQL + Neo4j + Pinecone |
| API | FastAPI funcional | FastAPI + auth + rate limiting |

## Países disponibles (mock data)

- 🇻🇪 Venezuela (VEN) — Risk: CRITICAL
- 🇳🇮 Nicaragua (NIC) — Risk: CRITICAL  
- 🇬🇹 Guatemala (GTM) — Risk: MODERATE
- 🇺🇾 Uruguay (URY) — Risk: LOW
