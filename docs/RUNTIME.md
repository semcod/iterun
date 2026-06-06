# Runtime — markpact + pactown (odchudzony iterun)

ITERUN generuje kod i **orchestruje** cykl życia. Uruchomienie może być delegowane do **pactown** (uniwersalne sandboxy), a artefakt przenośny to **stack.markpact.md** (markpact).

## Podział odpowiedzialności

| Warstwa | Narzędzie | Rola |
|---------|-----------|------|
| Generacja + plan | **iterun** | prompt → iterun.yaml → Dockerfile/compose |
| Pakowanie | **markpact** | cały `generated/` → jeden `stack.markpact.md` |
| Uruchomienie | **pactown** | sandboxy, porty, zależności, health |
| Naprawa LLM | **iterun** `--verify` | regeneracja YAML po błędach kontraktu |

## Instalacja

```bash
cd ~/github/wronai/iterun
source venv/bin/activate
pip install -e ".[ai,runtime]"
# lub lokalnie z repo:
pip install -e ../markpact -e ../pactown
pip install -e ".[ai]"
```

## Użycie

```bash
# Docker (domyślnie, jak dotąd)
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute

# Pactown — bez docker compose w iterun
export ITERUN_RUNTIME=pactown
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --verify

# lub flaga
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --runtime pactown
```

## Artefakty po planie / execute

| Plik | Opis |
|------|------|
| `generated/stack.markpact.md` | **Cały stack w jednym pliku** (markpact:file bloki) |
| `generated/services/*/README.md` | Per-service markpact (dla pactown) |
| `generated/pactown.yaml` | Konfiguracja ekosystemu (porty, depends_on, health) |
| `generated/pactown.urls.json` | URL usług po starcie |

## Ręczne uruchomienie pactown

```bash
cd generated
pactown run pactown.yaml   # jeśli CLI dostępne
# lub Python:
python -c "
from pactown.orchestrator import run_ecosystem
run_ecosystem('pactown.yaml', wait=False)
"
```

## Naprawa LLM

Pętla regeneracji wymaga `--verify` (testql + intract). Iterun **nie uruchamia** ponownie dockera sam — zatrzymuje runtime (`stop_runtime_for_intent`) i regeneruje YAML.

```bash
iterun generate "$(cat prompt.txt)" -o generated/ --run --execute --verify --runtime pactown
```

## Zmienne środowiskowe

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `ITERUN_RUNTIME` | `docker` | `docker` lub `pactown` |
