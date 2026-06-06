# Rejestr usług i artefaktów ITERUN

## Rekomendacja (standardy branżowe)

| Warstwa | Standard | Rola w iterun |
|---------|----------|---------------|
| **Katalog usług** | [Backstage Software Catalog](https://backstage.io/docs/features/software-catalog/) | `catalog/component-*.yaml` — komponenty do portalu dev |
| **Etykiety kontenerów** | [OCI Image Spec](https://github.com/opencontainers/image-spec/blob/main/annotations.md) + `dev.iterun.*` | Docker / Compose — filtrowanie `docker ps` |
| **Obserwowalność** | [OpenTelemetry Resource](https://opentelemetry.io/docs/specs/semconv/resource/) | `otel.resources.json` — `service.name`, namespace |
| **Kontrakty** | Intract + OpenAPI | `intract.yaml`, `openapi.yaml` (już w pipeline) |
| **Testy** | TestQL | `service.testql.toon.yaml` |
| **SBOM (opcjonalnie)** | CycloneDX / SPDX | przyszły adapter — checksumy już w rejestrze |

**Nie polecam** na start własnego mikroserwisu discovery — wystarczy plik `iterun.registry.json` w `generated/` + eksporty Backstage/OTel. Integracja z Prometheus/Grafana/Datadog to kolejny krok przez OTel Collector.

## Architektura

```
generator/pipeline  ──► integrations/bridges/pipeline
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
            iterun.registry.json  catalog/  otel.resources.json
                    │
        adapters: filesystem │ docker (live state)
        exporters: backstage │ opentelemetry
```

## Plik kanoniczny: `iterun.registry.json`

```json
{
  "api_version": "iterun.dev/v1",
  "kind": "Registry",
  "metadata": {
    "name": "shop-stack",
    "workspace": "/path/to/generated",
    "is_stack": true
  },
  "spec": {
    "deployment": "stack",
    "services": [
      {
        "name": "api-gateway",
        "urls": ["http://localhost:18081"],
        "labels": { "dev.iterun.intent": "shop-stack" },
        "otel": { "resource": { "attributes": { "service.name": "api-gateway" } } }
      }
    ],
    "artifacts": [
      {
        "name": "iterun.yaml",
        "role": "intent",
        "checksum_sha256": "…"
      }
    ]
  },
  "status": {
    "phase": "verified",
    "success": true,
    "endpoints": ["http://localhost:18081/ping"]
  }
}
```

Fazy (`status.phase`): `planned` → `running` → `verified` / `failed`.

## Użycie

### CLI

```bash
iterun registry -o generated/
iterun registry list
iterun registry list examples/*/generated --json
```

### REST

```bash
curl http://localhost:8000/api/registry?workspace=generated
curl -X POST http://localhost:8000/api/registry/refresh \
  -H 'Content-Type: application/json' \
  -d '{"workspace":"generated"}'
curl 'http://localhost:8000/api/registry/list?pattern=examples/*/generated'
```

### SDK

```python
from sdk import IterunClient

client = IterunClient()
client.registry_refresh("generated")
print(client.registry_get("generated")["spec"]["services"])
```

### MCP

- `iterun_registry_refresh(workspace="generated")`
- `iterun_registry_list(pattern="examples/*/generated")`

## Monitorowanie

1. **Artefakty** — `jq '.spec.artifacts[] | {name, role, checksum_sha256}' generated/iterun.registry.json`
2. **Usługi** — `jq '.spec.services[] | {name, urls, phase}' generated/iterun.registry.json`
3. **Docker** — `docker ps --filter label=dev.iterun.managed-by=iterun`
4. **Backstage** — zaimportuj `generated/catalog/*.yaml` do katalogu Backstage
5. **OTel** — przekaż `otel.resources.json` do collectora (resource attributes)

## Adaptery (rozszerzenia)

| Adapter | Plik | Opis |
|---------|------|------|
| `FilesystemAdapter` | `integrations/adapters/filesystem.py` | skan `generated/` |
| `DockerAdapter` | `integrations/adapters/docker.py` | wzbogaca o `docker ps` |
| `BackstageExporter` | `integrations/adapters/backstage.py` | eksport katalogu |
| `OpenTelemetryExporter` | `integrations/adapters/opentelemetry.py` | resource descriptors |

Nowy adapter: dziedzicz po `RegistryAdapter` lub `RegistryExporter` w `integrations/adapters/`.

## Kolejne kroki (opcjonalnie)

- **CycloneDX SBOM** z Dockerfile → adapter `sbom.py`
- **CloudEvents** przy `refresh_registry` (webhook po deploy)
- **Prometheus** — metryki z labeli `dev.iterun.*` przez cAdvisor
- **Centralny indeks** — `.iterun/index.json` agregujący wiele workspace’ów
