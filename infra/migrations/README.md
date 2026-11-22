# Database migrations

Alembic revisions are the canonical schema history. The initial revision creates the V0 identity, planning, world, analysis and infrastructure tables, plus the schema namespaces reserved for later domains.

The current SQLAlchemy metadata maps the shared infrastructure tables and organization root. Domain tables are still introduced through explicit Alembic SQL revisions. Do not use `alembic revision --autogenerate` to generate destructive changes until every domain table has a corresponding mapped model and the schema comparison has been reviewed.

Apply migrations with:

```powershell
uv run alembic -c infra/migrations/alembic.ini upgrade head
```

Check the current revision with:

```powershell
uv run alembic -c infra/migrations/alembic.ini current
```
