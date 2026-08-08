# Ka Education Backend

Modular monolith for the **Ka Education Body**: nine organ-aligned route groups, PostgreSQL, constitutional boot rules, and Blood event persistence. **MaatBench** is external (not implemented here).

## UKMT primary canon (curriculum pipeline)

The **University of KMT** step-by-step table (Preschool / K–12 through Post-PhD) is the **product canon** for stage content:

- `docs/canon/UKMT_EDUCATION_PIPELINE.md` — text mirror  
- `docs/canon/UKMT_PIPELINE_TABLE.png` — source graphic  
- `StageDefinition.canonReference` = `UKMT_EDUCATION_PIPELINE_TABLE_V1`  
- `StageDefinition.stepwiseBuildActions` = implementation checklist column from canon  

## Layers (do not flatten)

| Layer | Meaning |
|--------|---------|
| 42 Nomes | Structural registry (`/soul/nomes`) |
| Maat principles | Evaluation inputs — **not** nome count (`/soul/maat/principles`, `/voice/dashboard/maat`) |
| 9 Organs | API / module boundaries (soul, brain, memory, …) |
| Education stages | Domain workflow (`StageDefinition`, `/skeleton/stages`) |

## Quick start

```bash
cp .env.example .env
# Set DATABASE_URL and JWT_SECRET (≥32 chars)

npx prisma migrate dev
npx prisma db seed

npm run dev
```

- **API:** `http://localhost:3001` (or `API_PORT`)
- **OpenAPI UI:** `http://localhost:3001/docs`
- **Seed admin:** `admin@ka-education.local` / `ChangeMe!KaEdu` (change immediately)

## Key endpoints

| Area | Examples |
|------|-----------|
| DNA | `GET /manifest` |
| Health | `GET /health` |
| Soul | `GET /soul/constitution`, `GET /soul/nomes`, `GET /soul/maat/principles` |
| Skeleton | `GET /skeleton/stages`, `GET /skeleton/schema/Learner` |
| Memory | `POST /memory/learners/search` (auth) |
| Voice | `GET /voice/dashboard/overview`, `GET /voice/learners/:id/transcript` |
| Ka | `GET /ka/health`, `POST /ka/pain` (auth) |
| Progression | `POST /progression/evaluate`, `POST /progression/promote` (auth + active constitution) |

## Constitutional rule

Creating learners, enrollments, cohorts, promotions, and several writes **require an active constitution** row (`Constitution.isActive`). Seed creates one.

## Build phases (spec)

- **Phase 1** (this drop): skeleton + soul + memory foundation, institutions, learners, faculty, cohorts, enrollment, curriculum/assessments MVP, progression + transcript, Ka pain + events, Voice dashboards.
- **Phase 2–5:** see your build spec (`hands` full certs, research, drift, healing engine, etc.) — many routes return `501` with `PHASE_*` codes.

## Project layout

```
src/
  app.ts              # Fastify + organ route registration
  routes/             # HTTP handlers by concern
  guards/             # requireConstitution
  blood/              # Event bus → EventLog
  config/
  lib/
prisma/
  schema.prisma
  seed.ts
MANIFEST.ka           # Ka body DNA for this repo
docs/
```

## License

Specify per your governance — default for Tehuti Lab projects often MIT; align with institutional policy.
