#!/usr/bin/env python3
"""
INTENT-ITERATIVE: Command Line Interface
Main entry point for shell-based interaction.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

CONSTANT_5 = 5
CONSTANT_12 = 12.0
CONSTANT_15 = 15
PORT_20 = 20
CONSTANT_30 = 30
CONSTANT_60 = 60
CONSTANT_70 = 70


# Add parent to path for imports

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR
from parser.dsl_parser import DSLParser, parse_dsl, parse_dsl_file, ParseError, ValidationError
from planner.simulator import Planner, plan_intent
from executor.runner import Executor, execute_intent

# AI Gateway imports (optional)
try:
    from ai_gateway.gateway import AIGateway, GatewayConfig, get_gateway, OLLAMA_MODELS
    from ai_gateway.feedback_loop import FeedbackLoop, create_feedback_loop
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    
    @classmethod
    def disable(cls):
        cls.RESET = cls.BOLD = cls.RED = cls.GREEN = ""
        cls.YELLOW = cls.BLUE = cls.CYAN = ""


class CLI:
    """Interactive CLI for Intent-Iterative system."""
    
    def __init__(self, no_color: bool = False):
        if no_color:
            Colors.disable()
        self.current_ir: Optional[IntentIR] = None
        self.parser = DSLParser()
        self.planner = Planner()
    
    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*CONSTANT_60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    def print_success(self, text: str):
        print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")
    
    def print_error(self, text: str):
        print(f"{Colors.RED}✗ {text}{Colors.RESET}")
    
    def print_warning(self, text: str):
        print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")
    
    def print_info(self, text: str):
        print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")
    
    def cmd_new(self, name: str = "my-intent", goal: str = ""):
        """Create a new intent from scratch."""
        self.print_header("Creating New Intent")
        
        if not goal:
            goal = input("Enter goal: ").strip() or "No goal specified"
        
        dsl_template = f"""INTENT:
  name: {name}
  goal: {goal}

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /health

EXECUTION:
  mode: dry-run
"""
        
        try:
            self.current_ir = parse_dsl(dsl_template)
            self.print_success(f"Created new intent: {name}")
            self.print_info(f"ID: {self.current_ir.id}")
            return self.current_ir
        except (ParseError, ValidationError) as e:
            self.print_error(f"Failed to create intent: {e}")
            return None
    
    def cmd_load(self, filepath: str):
        """Load intent from DSL file."""
        self.print_header(f"Loading Intent: {filepath}")
        
        try:
            self.current_ir = parse_dsl_file(filepath)
            self.print_success(f"Loaded intent: {self.current_ir.intent.name}")
            self.print_info(f"Goal: {self.current_ir.intent.goal}")
            self.print_info(f"Actions: {len(self.current_ir.implementation.actions)}")
            return self.current_ir
        except FileNotFoundError:
            self.print_error(f"File not found: {filepath}")
        except (ParseError, ValidationError) as e:
            self.print_error(f"Parse error: {e}")
        return None
    
    def cmd_parse(self, content: str):
        """Parse DSL content directly."""
        self.print_header("Parsing DSL Content")
        
        try:
            self.current_ir = parse_dsl(content)
            self.print_success(f"Parsed intent: {self.current_ir.intent.name}")
            return self.current_ir
        except (ParseError, ValidationError) as e:
            self.print_error(f"Parse error: {e}")
            return None
    
    def cmd_plan(self, ir: IntentIR = None):
        """Run dry-run planning/simulation."""
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded. Use 'load' or 'new' first.")
            return None
        
        self.print_header(f"Planning: {ir.intent.name}")
        
        result = plan_intent(ir)
        
        print(f"\n{Colors.BOLD}Dry-run Logs:{Colors.RESET}")
        for log in result.logs:
            print(f"  {log}")
        
        if result.warnings:
            print(f"\n{Colors.BOLD}Warnings:{Colors.RESET}")
            for warning in result.warnings:
                self.print_warning(warning)
        
        print(f"\n{Colors.BOLD}Generated Code Preview:{Colors.RESET}")
        code_lines = result.generated_code.split('\n')[:15]
        for i, line in enumerate(code_lines, 1):
            print(f"  {Colors.CYAN}{i:3}{Colors.RESET} │ {line}")
        if len(result.generated_code.split('\n')) > 15:
            print(f"  ... ({len(result.generated_code.split(chr(10)))} total lines)")
        
        print(f"\n{Colors.BOLD}Dockerfile Preview:{Colors.RESET}")
        for line in result.dockerfile.split('\n')[:10]:
            print(f"  {line}")
        
        print(f"\n{Colors.BOLD}Estimated Resources:{Colors.RESET}")
        for key, value in result.estimated_resources.items():
            print(f"  {key}: {value}")
        
        self.print_success("Planning completed")
        return result
    
    def cmd_iterate(self, changes: dict = None, ir: IntentIR = None):
        """Apply iterative changes to current intent."""
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded.")
            return None
        
        self.print_header(f"Iteration #{ir.iteration_count + 1}")
        
        if not changes:
            print("Enter changes (JSON format or simple key=value):")
            print("Example: action=api.expose POST /users")
            print("         framework=flask")
            print("Type 'done' when finished.\n")
            
            changes = {}
            while True:
                line = input(f"{Colors.CYAN}>{Colors.RESET} ").strip()
                if line.lower() == 'done':
                    break
                if '=' in line:
                    key, value = line.split('=', 1)
                    changes[key.strip()] = value.strip()
        
        if changes:
            # Apply simple changes
            if 'action' in changes:
                action_str = changes['action']
                action = self.parser._parse_action(action_str)
                if action:
                    ir.implementation.actions.append(action)
                    self.print_success(f"Added action: {action_str}")
            
            if 'framework' in changes:
                ir.implementation.framework = changes['framework']
                self.print_success(f"Changed framework to: {changes['framework']}")
            
            if 'language' in changes:
                ir.implementation.language = changes['language']
                self.print_success(f"Changed language to: {changes['language']}")
            
            ir.add_iteration(changes, source="cli")
            self.print_info(f"Total iterations: {ir.iteration_count}")
        
        return ir
    
    def cmd_amen(self, ir: IntentIR = None, force: bool = False):
        """Approve intent for execution (AMEN boundary)."""
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded.")
            return False
        
        # Check config for auto-approval
        try:
            from config import get_config
            config = get_config()
            skip_confirmation = config.skip_amen_confirmation
        except ImportError:
            skip_confirmation = False
        
        self.print_header("AMEN Boundary")
        
        print(f"{Colors.BOLD}Intent Summary:{Colors.RESET}")
        print(f"  Name: {ir.intent.name}")
        print(f"  Goal: {ir.intent.goal}")
        print(f"  Actions: {len(ir.implementation.actions)}")
        print(f"  Runtime: {ir.environment.runtime.value}")
        print(f"  Iterations: {ir.iteration_count}")
        
        # Auto-approve if configured or forced
        if skip_confirmation or force:
            ir.approve_amen()
            self.print_success("AMEN auto-approved (SKIP_AMEN_CONFIRMATION=true)")
            return True
        
        print(f"\n{Colors.YELLOW}This will execute the intent with real side effects.{Colors.RESET}")
        confirm = input(f"\n{Colors.BOLD}Type 'AMEN' to confirm execution: {Colors.RESET}").strip()
        
        if confirm == 'AMEN':
            ir.approve_amen()
            self.print_success("AMEN approved. Intent ready for execution.")
            return True
        else:
            self.print_warning("Execution cancelled.")
            return False
    
    def cmd_execute(self, ir: IntentIR = None, workspace: str = None, validate: bool = True, auto_fix: bool = True):
        """Execute approved intent with validation."""
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded.")
            return None
        
        # Check config for auto-execution
        try:
            from config import get_config
            config = get_config()
            skip_amen = config.skip_amen_confirmation
        except ImportError:
            skip_amen = False
        
        # Auto-approve if not yet approved and skip is enabled
        if not ir.amen_approved:
            if skip_amen:
                ir.approve_amen()
                self.print_info("Auto-approved intent (SKIP_AMEN_CONFIRMATION=true)")
            else:
                self.print_error("Intent not approved. Run 'amen' first.")
                return None
        
        self.print_header(f"Executing: {ir.intent.name}")
        
        result = execute_intent(ir, workspace, skip_amen_check=skip_amen, validate=validate, auto_fix=auto_fix)
        
        print(f"\n{Colors.BOLD}Execution Logs:{Colors.RESET}")
        for log in result.logs:
            if "✓" in log or "success" in log.lower():
                status = Colors.GREEN
            elif "✗" in log or "error" in log.lower() or "ERROR" in log:
                status = Colors.RED
            elif "⚠" in log or "warning" in log.lower():
                status = Colors.YELLOW
            else:
                status = Colors.RESET
            print(f"  {status}{log}{Colors.RESET}")
        
        if result.success:
            self.print_success(f"Execution completed in {result.execution_time:.2f}s")
            
            if result.container_id:
                print(f"\n{Colors.BOLD}Container ID:{Colors.RESET} {result.container_id}")
            
            if result.endpoints:
                print(f"\n{Colors.BOLD}Available Endpoints:{Colors.RESET}")
                for endpoint in result.endpoints:
                    print(f"  → {endpoint}")
            
            if result.artifacts:
                print(f"\n{Colors.BOLD}Generated Artifacts:{Colors.RESET}")
                for name, path in result.artifacts.items():
                    print(f"  {name}: {path}")
            
            # Show validation results
            if result.validation:
                print(f"\n{Colors.BOLD}Validation:{Colors.RESET}")
                if result.validation.success:
                    print(f"  {Colors.GREEN}✓ All endpoints validated{Colors.RESET}")
                else:
                    print(f"  {Colors.YELLOW}⚠ Some issues detected{Colors.RESET}")
                    for check in result.validation.checks:
                        if check["ok"]:
                            print(f"    {Colors.GREEN}✓{Colors.RESET} {check['endpoint']}")
                        else:
                            print(f"    {Colors.RED}✗{Colors.RESET} {check['endpoint']} - {check.get('error', 'Failed')}")
            
            if result.auto_fix_applied:
                print(f"\n{Colors.CYAN}Auto-fix applied ({result.fix_iterations} iteration(s)){Colors.RESET}")
        else:
            self.print_error(f"Execution failed: {result.error}")
            
            # Show validation errors if any
            if result.validation and result.validation.errors:
                print(f"\n{Colors.BOLD}Validation Errors:{Colors.RESET}")
                for error in result.validation.errors:
                    print(f"  {Colors.RED}✗{Colors.RESET} {error}")
            
            # Show suggestions
            if result.validation and result.validation.suggestions:
                print(f"\n{Colors.BOLD}Suggestions:{Colors.RESET}")
                for suggestion in result.validation.suggestions:
                    print(f"  • {suggestion}")
            
            # Show container logs if available
            if result.container_id:
                try:
                    from executor.runner import Executor
                    executor = Executor()
                    logs = executor.get_container_logs(result.container_id, tail=20)
                    if logs:
                        print(f"\n{Colors.BOLD}Container Logs:{Colors.RESET}")
                        for line in logs.split('\n')[-10:]:
                            if line.strip():
                                print(f"  {line}")
                except:
                    pass
        
        return result
    
    def cmd_show(self, ir: IntentIR = None, format: str = "summary"):
        """Show current IR state."""
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded.")
            return
        
        if format == "json":
            print(ir.to_json())
        elif format == "full":
            self.print_header(f"Intent IR: {ir.intent.name}")
            print(ir.to_json())
        else:
            self.print_header(f"Intent: {ir.intent.name}")
            print(f"  ID: {ir.id}")
            print(f"  Goal: {ir.intent.goal}")
            print(f"  Version: {ir.version}")
            print(f"  Mode: {ir.execution_mode.value}")
            print(f"  AMEN Approved: {ir.amen_approved}")
            print(f"\n{Colors.BOLD}Environment:{Colors.RESET}")
            print(f"  Runtime: {ir.environment.runtime.value}")
            print(f"  Base Image: {ir.environment.base_image}")
            print(f"\n{Colors.BOLD}Implementation:{Colors.RESET}")
            print(f"  Language: {ir.implementation.language}")
            print(f"  Framework: {ir.implementation.framework}")
            print(f"  Actions ({len(ir.implementation.actions)}):")
            for action in ir.implementation.actions:
                print(f"    - {action.type.value} {action.method or ''} {action.target or ''}")
    
    def cmd_save(self, filepath: str, ir: IntentIR = None):
        """Save IR to JSON file."""
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded.")
            return
        
        with open(filepath, 'w') as f:
            f.write(ir.to_json())
        
        self.print_success(f"Saved to: {filepath}")
    
    def interactive_mode(self):
        """Run interactive shell."""
        self.print_header("INTENT-ITERATIVE Shell")
        print("Commands: new, load, plan, iterate, amen, execute, show, save, help, exit")
        if AI_AVAILABLE:
            print(f"{Colors.CYAN}AI Commands: suggest, apply, chat, models, ai-health{Colors.RESET}")
        print()
        
        while True:
            try:
                prompt = f"{Colors.BOLD}intent{Colors.RESET}"
                if self.current_ir:
                    prompt += f":{Colors.CYAN}{self.current_ir.intent.name}{Colors.RESET}"
                prompt += "> "
                
                line = input(prompt).strip()
                if not line:
                    continue
                
                parts = line.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd in ('exit', 'quit', 'q'):
                    print("Goodbye!")
                    break
                elif cmd == 'new':
                    self.cmd_new(args or "my-intent")
                elif cmd == 'load':
                    if args:
                        self.cmd_load(args)
                    else:
                        self.print_error("Usage: load <filepath>")
                elif cmd == 'plan':
                    self.cmd_plan()
                elif cmd == 'iterate':
                    self.cmd_iterate()
                elif cmd == 'amen':
                    self.cmd_amen()
                elif cmd in ('exec', 'execute', 'run'):
                    self.cmd_execute()
                elif cmd == 'show':
                    self.cmd_show(format=args or "summary")
                elif cmd == 'save':
                    if args:
                        self.cmd_save(args)
                    else:
                        self.print_error("Usage: save <filepath>")
                elif cmd == 'help':
                    self._show_help()
                # AI Commands
                elif cmd == 'suggest':
                    self.cmd_ai_suggest(focus=args if args else None)
                elif cmd == 'apply':
                    self.cmd_ai_apply()
                elif cmd == 'chat':
                    self.cmd_ai_chat(message=args if args else None)
                elif cmd == 'models':
                    max_p = float(args) if args else 12.0
                    self.cmd_models(max_p)
                elif cmd in ('ai-health', 'aihealth', 'health'):
                    self.cmd_ai_health()
                else:
                    self.print_error(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n")
                continue
            except EOFError:
                print("\nGoodbye!")
                break
    
    def cmd_ai_suggest(self, focus: str = None, ir: IntentIR = None):
        """Get AI-powered suggestions for the current intent."""
        if not AI_AVAILABLE:
            self.print_error("AI Gateway not available. Install litellm: pip install litellm")
            return None
        
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded.")
            return None
        
        self.print_header("AI Suggestions")
        self.print_info(f"Analyzing intent with LLM...")
        
        try:
            loop = create_feedback_loop()
            result = loop.analyze(ir, focus)
            
            if not result.success:
                self.print_error(f"Analysis failed: {result.error}")
                return result
            
            self.print_success(f"Analysis complete (model: {result.model_used})")
            
            if result.suggestions:
                print(f"\n{Colors.BOLD}Suggestions ({len(result.suggestions)}):{Colors.RESET}")
                for i, s in enumerate(result.suggestions, 1):
                    priority_color = {
                        "high": Colors.RED,
                        "medium": Colors.YELLOW,
                        "low": Colors.CYAN
                    }.get(s.priority, Colors.RESET)
                    
                    print(f"\n  {Colors.BOLD}{i}. [{priority_color}{s.priority.upper()}{Colors.RESET}] {s.type}")
                    print(f"     {s.description}")
                    if s.action_code:
                        print(f"     {Colors.GREEN}→ {s.action_code}{Colors.RESET}")
            else:
                self.print_info("No suggestions - intent looks good!")
            
            # Show next steps
            next_steps = loop.suggest_next_steps(ir)
            if next_steps:
                print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
                for step in next_steps[:5]:
                    print(f"  • {step}")
            
            return result
        
        except Exception as e:
            self.print_error(f"Error: {e}")
            return None
    
    def cmd_ai_apply(self, ir: IntentIR = None):
        """Apply AI suggestions automatically."""
        if not AI_AVAILABLE:
            self.print_error("AI Gateway not available.")
            return None
        
        ir = ir or self.current_ir
        if not ir:
            self.print_error("No intent loaded.")
            return None
        
        self.print_header("Auto-Apply AI Suggestions")
        
        loop = create_feedback_loop()
        result = loop.iterate(ir, auto_apply=True)
        
        if result.applied_changes:
            for change in result.applied_changes:
                self.print_success(change)
            self.print_info(f"Total changes: {len(result.applied_changes)}")
        else:
            self.print_info("No changes applied.")
        
        if result.warnings:
            for warning in result.warnings:
                self.print_warning(warning)
        
        return result
    
    def cmd_ai_chat(self, message: str = None, ir: IntentIR = None):
        """Chat with AI about the intent."""
        if not AI_AVAILABLE:
            self.print_error("AI Gateway not available.")
            return None
        
        ir = ir or self.current_ir
        
        self.print_header("AI Chat")
        
        if not message:
            print("Chat with AI about your intent. Type 'exit' to quit.\n")
            
            gateway = get_gateway()
            context = ""
            if ir:
                context = f"Current intent: {ir.intent.name}\nGoal: {ir.intent.goal}\nActions: {len(ir.implementation.actions)}"
            
            while True:
                try:
                    user_input = input(f"{Colors.CYAN}You>{Colors.RESET} ").strip()
                    if user_input.lower() in ('exit', 'quit', 'q'):
                        break
                    if not user_input:
                        continue
                    
                    prompt = user_input
                    if context:
                        prompt = f"{context}\n\nUser: {user_input}"
                    
                    response = gateway.complete(prompt, temperature=0.7)
                    
                    if response["success"]:
                        print(f"\n{Colors.GREEN}AI>{Colors.RESET} {response['content']}\n")
                    else:
                        self.print_error(f"Error: {response.get('error')}")
                
                except KeyboardInterrupt:
                    print()
                    break
        else:
            gateway = get_gateway()
            response = gateway.complete(message)
            if response["success"]:
                print(f"\n{response['content']}\n")
            else:
                self.print_error(f"Error: {response.get('error')}")
    
    def cmd_models(self, max_params: float = 12.0):
        """List available AI models."""
        if not AI_AVAILABLE:
            self.print_error("AI Gateway not available.")
            return
        
        self.print_header(f"Available Models (≤{max_params}B)")
        
        gateway = get_gateway()
        models = gateway.list_models(max_params)
        
        print(f"{'Model':<20} {'Size':<8} {'Context':<10} {'Description'}")
        print("-" * 70)
        
        for m in models:
            size = f"{m['parameters_billions']}B"
            ctx = f"{m['context_window']//1000}K"
            print(f"{m['name']:<20} {size:<8} {ctx:<10} {m['description'][:30]}")
        
        print(f"\n{Colors.CYAN}Default:{Colors.RESET} {gateway.config.default_model}")
        print(f"{Colors.CYAN}Ollama URL:{Colors.RESET} {gateway.config.ollama_base_url}")
    
    def cmd_ai_health(self):
        """Check AI Gateway health."""
        if not AI_AVAILABLE:
            self.print_error("AI Gateway not available. Install: pip install litellm")
            return
        
        self.print_header("AI Gateway Health Check")
        
        gateway = get_gateway()
        health = gateway.health_check()
        
        print(f"LiteLLM Available: {Colors.GREEN if health['litellm_available'] else Colors.RED}{health['litellm_available']}{Colors.RESET}")
        print(f"Ollama URL: {health['ollama_url']}")
        print(f"Default Model: {health['default_model']}")
        print(f"Available Models: {health['available_models']}")
        
        if health.get('ollama_connected'):
            self.print_success("Ollama connection: OK")
        else:
            self.print_error(f"Ollama connection: FAILED - {health.get('error', 'Unknown error')}")
    
    def _show_help(self):
        help_text = """
Available Commands:
  new [name]     - Create a new intent
  load <file>    - Load intent from DSL file
  plan           - Run dry-run simulation
  iterate        - Apply changes to current intent
  amen           - Approve intent for execution
  execute        - Execute approved intent
  show [json]    - Show current intent state
  save <file>    - Save intent to JSON file
  help           - Show this help
  exit           - Exit shell

AI Commands (requires Ollama):
  suggest        - Get AI-powered improvement suggestions
  apply          - Auto-apply AI suggestions
  chat           - Interactive chat with AI
  models         - List available AI models
  ai-health      - Check AI Gateway status

Workflow:
  1. new/load → 2. plan → 3. suggest → 4. iterate → 5. amen → 6. execute
"""
        print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="INTENT-ITERATIVE: DSL-based intent execution system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Start interactive shell
  %(prog)s plan myintent.yaml        # Run dry-run on file
  %(prog)s new my-api                # Create new intent
  %(prog)s execute myintent.yaml     # Plan, approve and execute
        """
    )
    
    parser.add_argument('command', nargs='?', default='shell',
                        choices=['shell', 'new', 'plan', 'execute', 'parse'],
                        help='Command to run')
    parser.add_argument('file', nargs='?', help='DSL file path or intent name')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--goal', '-g', help='Goal for new intent')
    parser.add_argument('--workspace', '-w', help='Workspace directory for execution')
    
    args = parser.parse_args()
    
    cli = CLI(no_color=args.no_color)
    
    if args.command == 'shell':
        cli.interactive_mode()
    
    elif args.command == 'new':
        name = args.file or 'my-intent'
        ir = cli.cmd_new(name, args.goal or '')
        if ir and args.json:
            print(ir.to_json())
    
    elif args.command == 'plan':
        if not args.file:
            cli.print_error("Usage: intent-cli plan <file.yaml>")
            sys.exit(1)
        ir = cli.cmd_load(args.file)
        if ir:
            result = cli.cmd_plan(ir)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
    
    elif args.command == 'execute':
        if not args.file:
            cli.print_error("Usage: intent-cli execute <file.yaml>")
            sys.exit(1)
        ir = cli.cmd_load(args.file)
        if ir:
            cli.cmd_plan(ir)
            # Auto-approve and execute (respects SKIP_AMEN_CONFIRMATION from config)
            cli.cmd_amen(ir, force=True)
            result = cli.cmd_execute(ir, args.workspace)
            if args.json and result:
                print(json.dumps(result.to_dict(), indent=2))
    
    elif args.command == 'parse':
        if args.file and Path(args.file).exists():
            ir = cli.cmd_load(args.file)
        else:
            # Read from stdin
            content = sys.stdin.read()
            ir = cli.cmd_parse(content)
        
        if ir:
            if args.json:
                print(ir.to_json())
            else:
                cli.cmd_show(ir)


if __name__ == "__main__":
    main()
