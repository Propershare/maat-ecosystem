# Ka Education Backend — Architecture Overview

## Runtime

- **Node 20+**, **TypeScript**, **Fastify 5**
- **PostgreSQL** via **Prisma**
- **JWT** auth (`POST /auth/login`)
- **OpenAPI** at `/docs`

## Organ → implementation map

| Organ | Responsibility | Code |
|--------|----------------|------|
| Soul | Constitution, nomes, Maat principles, policies | `routes/soul.ts` |
| Brain | Progression evaluation (MVP rules), future recommendations | `routes/brain.ts` |
| Memory | Search, record fetches | `routes/memory.ts` |
| Hands | Workflows, certs (stub) | `routes/hands.ts` |
| Senses | Raw intake → `EventLog` | `routes/senses.ts` |
| Voice | Dashboard read models | `routes/voice.ts` |
| Ka | Health, pain, alerts | `routes/ka.ts` |
| Skeleton | Stages, schemas, institution types | `routes/skeleton.ts` |
| Blood | `BloodEventBus` → `event_logs` | `blood/event-bus.ts` |

Domain tables (learners, institutions, enrollments, curriculum) are **education** concerns wired through the routes above — not a tenth organ.

## Boot order (engineering)

1. Load env (`JWT_SECRET`, `DATABASE_URL`)
2. Connect Prisma
3. Expose `GET /health` (checks DB + active constitution)
4. Register routes; writes that require soul order use `buildRequireConstitution`

## Maat score

MVP exposes **principle definitions** and labels them as **evaluation components**. No opaque `score: 49` without pillar breakdown — Phase 5 fills calculators per metric.

## UKMT canon linkage

Pipeline stages (`StageDefinition`) are seeded from the **University of KMT** primary table — see `docs/canon/README.md`. Fields **`canonReference`** and **`stepwiseBuildActions`** tie each stage row to that source; **nine stages ≠ 42 nomes** (structural registry is separate).
