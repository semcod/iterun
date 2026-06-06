"""CLI command dispatch — keeps main() argument parsing separate from handlers."""

from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path

from cli.plan_artifacts import write_plan_artifacts


def dispatch_command(args: Namespace, cli) -> None:
    """Run the subcommand selected by argparse."""
    if args.command == "shell":
        cli.interactive_mode()
        return

    if args.command == "new":
        name = args.file or "my-intent"
        ir = cli.cmd_new(name, args.goal or "")
        if ir and args.json:
            print(ir.to_json())
        return

    if args.command == "plan":
        _dispatch_plan(args, cli)
        return

    if args.command == "execute":
        _dispatch_execute(args, cli)
        return

    if args.command == "parse":
        _dispatch_parse(args, cli)
        return

    if args.command == "schema":
        from dsl.schema import get_json_schema

        print(json.dumps(get_json_schema(), indent=2))
        return

    if args.command == "validate":
        _dispatch_validate(args, cli)
        return

    if args.command == "generate":
        _dispatch_generate(args, cli)
        return

    if args.command == "registry":
        _dispatch_registry(args, cli)


def _dispatch_plan(args: Namespace, cli) -> None:
    if not args.file:
        cli.print_error("Usage: intent-cli plan <file.yaml>")
        sys.exit(1)
    ir = cli.cmd_load(args.file)
    if not ir:
        return
    result = cli.cmd_plan(ir)
    written = None
    if args.output_dir:
        written = write_plan_artifacts(ir, result, args.output_dir)
        if not args.json and not args.quiet:
            cli.print_info(f"Artifacts written to {args.output_dir}")
            for name, path in written.items():
                print(f"  {name}: {path}")
    if args.quiet and not args.json and written:
        print(f"OK {ir.intent.name} -> {args.output_dir}")
    if args.json:
        payload = result.to_dict()
        if written:
            payload["artifacts"] = written
        print(json.dumps(payload, indent=2))


def _dispatch_execute(args: Namespace, cli) -> None:
    if not args.file:
        cli.print_error("Usage: intent-cli execute <file.yaml>")
        sys.exit(1)
    ir = cli.cmd_load(args.file)
    if not ir:
        return
    ws = Path(args.workspace) if args.workspace else None
    skip_plan = (
        args.quiet
        and ws
        and ((ws / "docker-compose.yaml").is_file() or (ws / "Dockerfile").is_file())
    )
    if not skip_plan:
        plan_result = cli.cmd_plan(ir)
        if args.output_dir and plan_result:
            write_plan_artifacts(ir, plan_result, args.output_dir)
    cli.cmd_iterun(ir, force=True)
    result = cli.cmd_execute(ir, args.workspace)
    if args.quiet and result and result.success and not args.json:
        workspace = args.workspace or "."
        print(f"OK {ir.intent.name} executed -> {workspace}")
    if args.json and result:
        print(json.dumps(result.to_dict(), indent=2))


def _dispatch_parse(args: Namespace, cli) -> None:
    if args.file and Path(args.file).exists():
        ir = cli.cmd_load(args.file)
    else:
        content = sys.stdin.read()
        ir = cli.cmd_parse(content)

    if not ir:
        return
    if args.output_dir:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        ir_file = out / "ir.json"
        ir_file.write_text(ir.to_json(), encoding="utf-8")
        if args.quiet and not args.json:
            print(f"OK {ir.intent.name} -> {ir_file}")
        elif not args.json:
            cli.print_info(f"IR written to {ir_file}")
    if args.json:
        print(ir.to_json())
    elif not args.quiet:
        cli.cmd_show(ir)


def _dispatch_validate(args: Namespace, cli) -> None:
    path = args.file
    if not path:
        cli.print_error("Usage: iterun validate <file.yaml>")
        sys.exit(1)
    from dsl.schema import validate_yaml_document

    content = Path(path).read_text(encoding="utf-8")
    doc, errors = validate_yaml_document(content)
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    elif errors:
        for err in errors:
            cli.print_error(err)
        sys.exit(1)
    else:
        cli.print_success(f"Valid: {doc.INTENT.name if doc else path}")


def _dispatch_generate(args: Namespace, cli) -> None:
    prompt = args.prompt or args.file
    if not prompt:
        cli.print_error(
            'Usage: iterun generate "Create a REST API..." [-o dir] [--run] [--execute]'
        )
        sys.exit(1)
    try:
        from generator.pipeline import run_pipeline
    except ImportError as e:
        cli.print_error(f"Generator unavailable: {e}")
        sys.exit(1)

    output_dir = args.output_dir or args.workspace or "generated"
    if args.execute or args.run:
        _dispatch_generate_pipeline(args, cli, prompt, output_dir, run_pipeline)
    else:
        _dispatch_generate_yaml_only(args, cli, prompt, output_dir)


def _dispatch_generate_pipeline(args, cli, prompt: str, output_dir: str, run_pipeline) -> None:
    result = run_pipeline(
        prompt,
        output_dir=output_dir,
        execute=args.execute,
        verify=args.verify,
        max_iterations=args.max_iterations,
        max_verify_iterations=args.max_verify_iterations,
        model=args.model,
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    elif args.quiet and result.success:
        msg = f"OK {result.yaml_path or output_dir}"
        if result.verification and result.verification.get("service_url"):
            msg += f" verified={result.verification['service_url']}"
        print(msg)
    elif result.success:
        cli.print_success(f"Generated: {result.yaml_path}")
        if result.execution:
            cli.print_info("Service executed (see execution logs in JSON with --json)")
        if result.verification:
            url = result.verification.get("service_url", "")
            n = result.verify_iterations
            cli.print_success(f"Contract verified at {url} (round {n})")
    else:
        cli.print_error(result.error or "Generation failed")
        if result.execution and not args.verify:
            cli.print_info(
                "Tip: add --verify to regenerate iterun.yaml with LLM when contracts fail"
            )
        if result.generate and result.generate.attempts:
            last = result.generate.attempts[-1]
            for err in last.errors[:5]:
                cli.print_error(err)
        sys.exit(1)


def _dispatch_generate_yaml_only(args, cli, prompt: str, output_dir: str) -> None:
    from config import PACKAGE_FILENAME
    from generator.intract_manifest import write_intract_manifest
    from generator.intent_generator import IntentGenerator
    from generator.testql_scenario import write_testql_scenario

    gen = IntentGenerator(max_iterations=args.max_iterations, model=args.model)
    gen_result = gen.generate(prompt)
    if gen_result.success and gen_result.yaml_content:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        yaml_path = out / PACKAGE_FILENAME
        yaml_path.write_text(gen_result.yaml_content, encoding="utf-8")
        write_intract_manifest(yaml_path, out / "intract.yaml", prompt=prompt)
        write_testql_scenario(yaml_path, out / "service.testql.toon.yaml")
        (out / "prompt.txt").write_text(prompt, encoding="utf-8")
        if args.json:
            print(json.dumps(gen_result.to_dict(), indent=2))
        elif args.quiet:
            print(f"OK {yaml_path}")
        else:
            cli.print_success(f"Generated ({gen_result.iterations} iter): {yaml_path}")
    else:
        cli.print_error(gen_result.error or "Generation failed")
        sys.exit(1)


def _dispatch_registry(args: Namespace, cli) -> None:
    from integrations.bridges.pipeline import refresh_registry
    from registry.catalog import discover_glob

    if args.file == "list":
        pattern = args.workspace or "examples/*/generated"
        items = discover_glob(pattern)
        if args.json:
            print(json.dumps({"registries": items}, indent=2))
        else:
            for item in items:
                print(
                    f"{item['name']:20} {item['phase']:10} "
                    f"svc={item['services']} art={item['artifacts']} "
                    f"{item['workspace']}"
                )
        return

    workspace = args.output_dir or args.workspace or args.file or "generated"
    result = refresh_registry(workspace, include_docker=not args.quiet)
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.quiet:
        print(f"OK registry -> {result['written']['registry']}")
    else:
        m = result["manifest"]
        cli.print_success(f"Registry: {result['written']['registry']}")
        cli.print_info(
            f"{m['metadata']['name']} — "
            f"{len(m['spec']['services'])} services, "
            f"{len(m['spec']['artifacts'])} artifacts, "
            f"phase={m['status']['phase']}"
        )
