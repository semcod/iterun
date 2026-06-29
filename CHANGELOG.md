# Changelog

## [0.1.10] - 2026-06-06

### Fixed
- Fix unused-imports issues (ticket-a7ae9a42)
- Fix magic-numbers issues (ticket-cc2f7cb3)
- Fix unused-imports issues (ticket-e803bc29)

## [0.1.10] - 2026-06-06

### Fixed
- Fix string-concat issues (ticket-a2d11e40)
- Fix unused-imports issues (ticket-bab201a8)
- Fix magic-numbers issues (ticket-0aef330e)

## [0.1.10] - 2026-06-06

### Fixed
- Fix unused-imports issues (ticket-6d2431df)
- Fix magic-numbers issues (ticket-7bc68b39)
- Fix unused-imports issues (ticket-153639af)
- Fix unused-imports issues (ticket-0d5a22a5)
- Fix smart-return-type issues (ticket-6f2fa210)
- Fix string-concat issues (ticket-9220df93)
- Fix unused-imports issues (ticket-d63b5f0b)
- Fix magic-numbers issues (ticket-31eff1cb)
- Fix unused-imports issues (ticket-e7236ef7)
- Fix string-concat issues (ticket-46fac2ee)

## [0.1.10] - 2026-06-06

### Fixed
- Fix unused-imports issues (ticket-a1f212f1)
- Fix unused-imports issues (ticket-535a7727)
- Fix unused-imports issues (ticket-1b769156)
- Fix magic-numbers issues (ticket-ca30ddd7)
- Fix unused-imports issues (ticket-9f5356d0)
- Fix unused-imports issues (ticket-1114a179)
- Fix unused-imports issues (ticket-e291c26e)
- Fix unused-imports issues (ticket-ea8c4817)
- Fix unused-imports issues (ticket-e9e6354c)
- Fix magic-numbers issues (ticket-a22d5bb9)
- Fix unused-imports issues (ticket-e4bb5697)
- Fix unused-imports issues (ticket-12fa8f86)
- Fix magic-numbers issues (ticket-a6622dbd)
- Fix unused-imports issues (ticket-1a493952)
- Fix magic-numbers issues (ticket-69ed1465)
- Fix smart-return-type issues (ticket-58ce5bd8)
- Fix unused-imports issues (ticket-908d08bc)
- Fix ai-boilerplate issues (ticket-4be949b7)
- Fix unused-imports issues (ticket-163ba927)
- Fix magic-numbers issues (ticket-0b17203d)
- Fix string-concat issues (ticket-b8a53a20)

## [0.1.10] - 2026-06-06

### Fixed
- Fix smart-return-type issues (ticket-aabd8ad8)

## [0.1.10] - 2026-06-06

### Fixed
- Fix magic-numbers issues (ticket-2497d410)
- Fix smart-return-type issues (ticket-24da5573)

## [0.1.10] - 2026-06-06

### Fixed
- Fix ai-boilerplate issues (ticket-0e16010e)
- Fix duplicate-imports issues (ticket-0c07b2b0)
- Fix string-concat issues (ticket-cfee50f1)
- Fix unused-imports issues (ticket-6278136c)
- Fix magic-numbers issues (ticket-149a1fc0)
- Fix duplicate-imports issues (ticket-5efcabc3)
- Fix unused-imports issues (ticket-1ca7844d)
- Fix magic-numbers issues (ticket-144fd557)
- Fix unused-imports issues (ticket-57734f46)
- Fix magic-numbers issues (ticket-b21aa0ba)
- Fix string-concat issues (ticket-87e12bd5)
- Fix unused-imports issues (ticket-7662f1ea)
- Fix magic-numbers issues (ticket-92002fbe)
- Fix unused-imports issues (ticket-cf5f965a)
- Fix string-concat issues (ticket-59fa2f75)
- Fix unused-imports issues (ticket-6e572529)
- Fix magic-numbers issues (ticket-fa8065fc)
- Fix unused-imports issues (ticket-d9daae22)
- Fix unused-imports issues (ticket-d4251da0)
- Fix smart-return-type issues (ticket-768de0b2)
- Fix unused-imports issues (ticket-9d48e886)
- Fix ai-boilerplate issues (ticket-55b88512)
- Fix smart-return-type issues (ticket-6e5cc9f1)
- Fix unused-imports issues (ticket-562cd9a2)
- Fix magic-numbers issues (ticket-3fa837c6)
- Fix smart-return-type issues (ticket-3649a11e)
- Fix smart-return-type issues (ticket-0dad7005)
- Fix string-concat issues (ticket-edb2e6df)
- Fix unused-imports issues (ticket-35e0bec7)
- Fix smart-return-type issues (ticket-3fe6ecd0)
- Fix smart-return-type issues (ticket-29196399)

## [Unreleased]

### Added
- **Integration surfaces** — `interfaces/IterunService` (REST, SDK, MCP, CLI)
- **REST API** — `/api/health`, `/api/interfaces`, `/api/pipeline/run`, `/api/registry`, `/api/intents/plan-yaml`
- **MCP** — `iterun_mcp/` + `iterun-mcp` (fix konfliktu z PyPI `mcp`); tools: pipeline, registry, plan
- **Registry** — `registry/`, `integrations/`; `iterun.registry.json`, Backstage + OTel export; `iterun registry` CLI
- **Runtime** — `ITERUN_RUNTIME` / `--runtime pactown`; markpact `stack.markpact.md`; pactown orchestration
- **STACK** — examples 17–19, `run-stacks.sh`, compose labels (`dev.iterun.*`)
- **Docs** — `docs/API.md`, `docs/REGISTRY.md`, `docs/RUNTIME.md`; examples 01–19 „Nowe opcje”
- **Tests** — `test_interfaces.py`, `test_registry.py`, `test_pactown_config.py`, `test_executor_validation.py`

### Changed
- Pipeline auto-packs markpact po planie; registry refresh po `session.json`
- Executor: pomija walidację bare root URL gdy są jawne trasy; compose logs dla STACK
- `examples/_common.sh` — przekazuje `ITERUN_RUNTIME` do `generate`
- SDK: `run_pipeline()`, `registry_*()`; MCP renamed to `iterun_mcp`

### Fixed
- `iterun-mcp` ImportError (konflikt `mcp.server` z pakietem PyPI)
- Registry crash gdy `session.verification` jest `null`
- Pipeline `success` odzwierciedla fail walidacji endpointów (bez `--verify`)

## [0.1.13] - 2026-06-29

### Docs
- Update README.md

### Other
- Update project/planfile-tickets.yaml

## [0.1.12] - 2026-06-06

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/e2e/test_expectations.py
- Update tests/e2e/test_shell.py
- Update tests/e2e/test_stack_planner.py

### Other
- Update .code2llm_cache/Makefile_1780755568355196027_7781.pkl
- Update .code2llm_cache/__init___1780762327442126044_307.pkl
- Update .code2llm_cache/_common_1780755175625802172_3024.pkl
- Update .code2llm_cache/_verify_1780755175839804589_4982.pkl
- Update .code2llm_cache/_verify_1780755565608165512_5142.pkl
- Update .code2llm_cache/contract_verify_1780755565163160569_7557.pkl
- Update .code2llm_cache/expectations_1780755177469822993_3539.pkl
- Update .code2llm_cache/goal_1780754872450340895_12383.pkl
- Update .code2llm_cache/pipeline_1780755183617892395_8828.pkl
- Update .code2llm_cache/planfile_1780754884007803798_28207.pkl
- ... and 47 more files

## [0.1.11] - 2026-06-06

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/_common_1780759272721600311_4925.pkl
- Update .code2llm_cache/discover_context_1780761268730490759_2685.pkl
- Update .code2llm_cache/dispatch_1780759113785920253_9177.pkl
- Update .code2llm_cache/dispatch_1780761308793935119_9935.pkl
- Update .code2llm_cache/filesystem_1780761309222939874_498.pkl
- Update .code2llm_cache/iterun_1780759116308946857_864.pkl
- Update .code2llm_cache/pipeline_1780761267218473977_230.pkl
- Update .code2llm_cache/pipeline_1780761276451576441_11499.pkl
- Update .code2llm_cache/pipeline_1780761305284896221_1582.pkl
- Update .code2llm_cache/pipeline_1780761305821300356_11311.pkl
- ... and 57 more files

## [0.1.10] - 2026-06-06

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/API.md
- Update docs/INTENT_DSL_SPEC.md
- Update docs/README.md
- Update docs/REGISTRY.md
- Update docs/RUNTIME.md
- ... and 3 more files

### Test
- Update tests/e2e/test_ai_gateway.py
- Update tests/e2e/test_executor_validation.py
- Update tests/e2e/test_shell.py

### Other
- Update .code2llm_cache/__init___1780758515999720150_29.pkl
- Update .code2llm_cache/__init___1780758706349665627_73.pkl
- Update .code2llm_cache/__init___1780758720285809395_645.pkl
- Update .code2llm_cache/_common_1780758285522318956_4816.pkl
- Update .code2llm_cache/ai_1780758523125792288_4867.pkl
- Update .code2llm_cache/app_1780758523966800805_1469.pkl
- Update .code2llm_cache/discover_1780758491464472251_3066.pkl
- Update .code2llm_cache/discover_artifacts_1780758487621789090_3598.pkl
- Update .code2llm_cache/discover_io_1780758488689111738_1913.pkl
- Update .code2llm_cache/discover_services_1780758490257460076_3265.pkl
- ... and 64 more files

## [0.1.9] - 2026-06-06

### Docs
- Update README.md
- Update docs/API.md
- Update docs/REGISTRY.md
- Update docs/RUNTIME.md
- Update examples/01-user-api/README.md
- Update examples/02-ping-smoke/README.md
- Update examples/03-flask-api/README.md
- Update examples/04-express-api/README.md
- Update examples/05-ir-show/README.md
- Update examples/06-iterate-workflow/README.md
- ... and 17 more files

### Test
- Update tests/e2e/test_executor_validation.py
- Update tests/test_interfaces.py
- Update tests/test_pactown_config.py
- Update tests/test_registry.py

### Other
- Update .gitignore
- Update cli/main.py
- Update config.py
- Update examples/17-stack-shop-gateway/iterun.yaml
- Update examples/17-stack-shop-gateway/run-generate.sh
- Update examples/17-stack-shop-gateway/run.sh
- Update examples/18-stack-blog/run.sh
- Update examples/19-stack-api-cache/run.sh
- Update examples/_common.sh
- Update executor/runner.py
- ... and 46 more files

## [0.1.8] - 2026-06-06

### Docs
- Update .testql-auto/summary.md

### Test
- Update tests/e2e/test_contract_verify.py
- Update tests/e2e/test_pipeline_repair.py

### Other
- Update .code2llm_cache/Makefile_1780755568355196027_7781.pkl
- Update .code2llm_cache/_common_1780755175625802172_3024.pkl
- Update .code2llm_cache/_verify_1780755175839804589_4982.pkl
- Update .code2llm_cache/_verify_1780755565608165512_5142.pkl
- Update .code2llm_cache/contract_verify_1780755565163160569_7557.pkl
- Update .code2llm_cache/expectations_1780755177469822993_3539.pkl
- Update .code2llm_cache/pipeline_1780755183617892395_8828.pkl
- Update .code2llm_cache/planfile_1780755557914080033_28951.pkl
- Update .code2llm_cache/run_1780755182301877541_326.pkl
- Update .code2llm_cache/run_1780755182368878297_1463.pkl
- ... and 17 more files

## [0.1.8] - 2026-06-06

### Docs
- Update .testql-auto/summary.md
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/INTENT_DSL_SPEC.md
- Update examples/17-stack-shop-gateway/README.md
- Update examples/18-stack-blog/README.md
- Update examples/19-stack-api-cache/README.md
- ... and 3 more files

### Test
- Update tests/e2e/test_contract_verify.py
- Update tests/e2e/test_expectations.py
- Update tests/e2e/test_pipeline_repair.py
- Update tests/e2e/test_stack_planner.py
- Update tests/e2e/test_testql_scenario.py

### Other
- Update .code2llm_cache/Makefile_1780755568355196027_7781.pkl
- Update .code2llm_cache/_common_1780755175625802172_3024.pkl
- Update .code2llm_cache/_verify_1780755175839804589_4982.pkl
- Update .code2llm_cache/_verify_1780755565608165512_5142.pkl
- Update .code2llm_cache/contract_verify_1780755565163160569_7557.pkl
- Update .code2llm_cache/expectations_1780755177469822993_3539.pkl
- Update .code2llm_cache/pipeline_1780755183617892395_8828.pkl
- Update .code2llm_cache/planfile_1780755557914080033_28951.pkl
- Update .code2llm_cache/run_1780755182301877541_326.pkl
- Update .code2llm_cache/run_1780755182368878297_1463.pkl
- ... and 68 more files

## [0.1.7] - 2026-06-06

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update examples/13-resilience-vague/README.md
- Update examples/14-resilience-inventory/README.md
- Update examples/15-resilience-nested-paths/README.md
- Update examples/16-resilience-framework-trap/README.md
- Update examples/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/e2e/test_expectations.py

### Other
- Update app.doql.less
- Update examples/13-resilience-vague/expectations.yaml
- Update examples/13-resilience-vague/prompt.txt
- Update examples/13-resilience-vague/run.sh
- Update examples/14-resilience-inventory/expectations.yaml
- Update examples/14-resilience-inventory/prompt.txt
- Update examples/14-resilience-inventory/run.sh
- Update examples/15-resilience-nested-paths/expectations.yaml
- Update examples/15-resilience-nested-paths/prompt.txt
- Update examples/15-resilience-nested-paths/run.sh
- ... and 24 more files

## [0.1.6] - 2026-06-06

### Docs
- Update README.md
- Update examples/01-user-api/README.md
- Update examples/02-ping-smoke/README.md
- Update examples/03-flask-api/README.md
- Update examples/04-express-api/README.md
- Update examples/05-ir-show/README.md
- Update examples/06-iterate-workflow/README.md
- Update examples/07-execution-smoke/README.md
- Update examples/08-llm-generate/README.md
- Update examples/09-e2e-ping-verify/README.md
- ... and 4 more files

### Test
- Update tests/e2e/test_intent_generator.py
- Update tests/e2e/test_intract_manifest.py
- Update tests/e2e/test_shell.py
- Update tests/e2e/test_testql_scenario.py

### Other
- Update .gitignore
- Update cli/main.py
- Update config.py
- Update examples/01-user-api/intent.yaml
- Update examples/01-user-api/prompt.txt
- Update examples/01-user-api/run.sh
- Update examples/02-ping-smoke/intent.yaml
- Update examples/02-ping-smoke/prompt.txt
- Update examples/02-ping-smoke/run.sh
- Update examples/03-flask-api/intent.yaml
- ... and 52 more files

## [0.1.5] - 2026-06-06

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/INTENT_DSL_SPEC.md
- Update examples/06-iterate-workflow/README.md
- Update examples/08-llm-generate/README.md
- Update project/context.md

### Test
- Update tests/e2e/test_ai_gateway.py
- Update tests/e2e/test_shell.py
- Update tests/e2e/test_web.py

### Other
- Update .env.example
- Update .pyqual/ruff.json
- Update Makefile
- Update ai_gateway/gateway.py
- Update app.doql.less
- Update cli/main.py
- Update config.py
- Update executor/runner.py
- Update generator/pipeline.py
- Update ir/models.py
- ... and 15 more files

## [0.1.4] - 2026-06-06

### Docs
- Update README.md
- Update docs/INTENT_DSL_SPEC.md
- Update examples/01-user-api/README.md
- Update examples/02-ping-smoke/README.md
- Update examples/03-flask-api/README.md
- Update examples/04-express-api/README.md
- Update examples/05-ir-show/README.md
- Update examples/06-iterate-workflow/README.md
- Update examples/07-execution-smoke/README.md
- Update examples/08-llm-generate/README.md
- ... and 1 more files

### Test
- Update tests/e2e/test_intent_generator.py

### Other
- Update .gitignore
- Update Makefile
- Update cli/__init__.py
- Update cli/__main__.py
- Update cli/main.py
- Update dsl/__init__.py
- Update dsl/schema.py
- Update examples/01-user-api/intent.yaml
- Update examples/01-user-api/run.sh
- Update examples/02-ping-smoke/intent.yaml
- ... and 25 more files

## [0.1.3] - 2026-06-06

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/context.md

### Test
- Update tests/conftest.py
- Update tests/e2e/test_ai_gateway.py
- Update tests/e2e/test_shell.py
- Update tests/e2e/test_web.py

### Other
- Update .env.example
- Update Makefile
- Update ai_gateway/feedback_loop.py
- Update ai_gateway/gateway.py
- Update app.doql.less
- Update cli/main.py
- Update config.py
- Update executor/runner.py
- Update ir/models.py
- Update parser/dsl_parser.py
- ... and 7 more files

## [0.1.2] - 2026-06-06

### Docs
- Update README.md

## [0.1.1] - 2026-06-06

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/generated-api-integration.testql.toon.yaml
- Update testql-scenarios/generated-api-smoke.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml
- Update tests/e2e/test_web.py

### Other
- Update .code2llm_cache/Makefile_1766748982000000000_7684.pkl
- Update .code2llm_cache/__init___1766747252000000000_259.pkl
- Update .code2llm_cache/__init___1766747283000000000_179.pkl
- Update .code2llm_cache/__init___1766747324000000000_112.pkl
- Update .code2llm_cache/__init___1766747357000000000_157.pkl
- Update .code2llm_cache/__init___1766747417000000000_55.pkl
- Update .code2llm_cache/__init___1766747512000000000_66.pkl
- Update .code2llm_cache/__init___1766748307000000000_604.pkl
- Update .code2llm_cache/app_1780744339286299986_13769.pkl
- Update .code2llm_cache/config_1771510248700373942_5561.pkl
- ... and 51 more files


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.10] - 2026-06-06

### Fixed
- Fix smart-return-type issues (ticket-2db5cbf9)
- Fix llm-hallucinations issues (ticket-6a4ab02a)
- Fix llm-generated-code issues (ticket-0ac0847e)
- Fix smart-return-type issues (ticket-747a5b4e)
- Fix string-concat issues (ticket-86643417)
- Fix unused-imports issues (ticket-feda516a)
- Fix ai-boilerplate issues (ticket-51956d32)
- Fix ai-boilerplate issues (ticket-03f3ff2c)
- Fix smart-return-type issues (ticket-79b34bfa)
- Fix unused-imports issues (ticket-53c12036)
- Fix llm-hallucinations issues (ticket-5ebc257d)
- Fix llm-generated-code issues (ticket-342cfa83)
- Fix ai-boilerplate issues (ticket-ae543d78)
- Fix smart-return-type issues (ticket-571c5f7d)
- Fix string-concat issues (ticket-41e50884)
- Fix ai-boilerplate issues (ticket-2ca10b80)

## [0.1.10] - 2026-03-30

### Fixed
- Fix relative-imports issues (ticket-43e56fcb)
- Fix relative-imports issues (ticket-f32bc97a)
- Fix unused-imports issues (ticket-117eb918)
- Fix llm-generated-code issues (ticket-f8d91ce2)
- Fix smart-return-type issues (ticket-352c3755)
- Fix magic-numbers issues (ticket-2bfdea8d)
- Fix relative-imports issues (ticket-4f3f1948)
- Fix smart-return-type issues (ticket-1b2bc89b)
- Fix string-concat issues (ticket-450308a3)
- Fix unused-imports issues (ticket-e2cd2bf7)
- Fix duplicate-imports issues (ticket-4a44eb7b)
- Fix magic-numbers issues (ticket-ce00975e)
- Fix ai-boilerplate issues (ticket-c84df10c)
- Fix relative-imports issues (ticket-9f1b4c93)
- Fix smart-return-type issues (ticket-a0e5e8a8)
- Fix string-concat issues (ticket-98d5cffd)
- Fix unused-imports issues (ticket-c1a4ab4d)
- Fix magic-numbers issues (ticket-1e40a3b5)
- Fix llm-generated-code issues (ticket-d7af8c15)
- Fix ai-boilerplate issues (ticket-5301dd71)
- Fix relative-imports issues (ticket-b8b93858)
- Fix relative-imports issues (ticket-0df92379)
- Fix smart-return-type issues (ticket-d7be6ad9)
- Fix smart-return-type issues (ticket-c3a53878)
- Fix string-concat issues (ticket-b1876d66)
- Fix magic-numbers issues (ticket-96061a71)
- Fix ai-boilerplate issues (ticket-be996d4c)
- Fix unused-imports issues (ticket-2120f855)
- Fix relative-imports issues (ticket-0b666d4f)
- Fix magic-numbers issues (ticket-751d0e08)
- Fix llm-generated-code issues (ticket-dbeae813)
- Fix unused-imports issues (ticket-990f5c35)
- Fix duplicate-imports issues (ticket-3251e7af)
- Fix magic-numbers issues (ticket-9a11f507)
- Fix ai-boilerplate issues (ticket-10243061)

## [0.1.0] - 2025-01-01

### Added
- Initial release of ITERUN (DSL-based intent execution system)
- Intent parsing with iterative refinement
- AI gateway integration
- CLI interface
- DSL executor with ITERUN boundary support
- IR (Intermediate Representation) layer
- Planner module
- Example configurations
