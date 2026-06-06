# Changelog

## [Unreleased]

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
- Initial release of AMEN (DSL-based intent execution system)
- Intent parsing with iterative refinement
- AI gateway integration
- CLI interface
- DSL executor with AMEN boundary support
- IR (Intermediate Representation) layer
- Planner module
- Example configurations
