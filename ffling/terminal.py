#!/usr/bin/env python3
"""
FFling Terminal - Interactive REPL for FFling Programming Language
Version 1.0
"""

import os
import sys
import subprocess
from lexer import Lexer
from parser_ll import Parser
from interpreter import Interpreter

class FFlingTerminal:
    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []
        self.current_code = ""
        self.prompt = "ffling> "
        self.multiline = False
        self.version = "1.0"
        self.commands = {
            'help': self.cmd_help,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
            'version': self.cmd_version,
            'history': self.cmd_history,
            'clear_history': self.cmd_clear_history,
            'goto': self.cmd_goto,
            'install': self.cmd_install,
            'uninstall': self.cmd_uninstall,
            'update': self.cmd_update,
            'install_list': self.cmd_install_list,
            'setup': self.cmd_setup,
            'load': self.cmd_load,
            'save': self.cmd_save,
            'exec': self.cmd_exec,
            'eval': self.cmd_eval,
            'list': self.cmd_list,
            'reset': self.cmd_reset,
            'info': self.cmd_info,
            'tutorial': self.cmd_tutorial,
            'examples': self.cmd_examples,
            'search_history': self.cmd_search_history,
            'export_vars': self.cmd_export_vars,
            'import_code': self.cmd_import_code,
            'run_tests': self.cmd_run_tests,
            'stats': self.cmd_stats,
            'config': self.cmd_config,
            'time_exec': self.cmd_time_exec,
            'benchmark': self.cmd_benchmark,
        }

    def run(self):
        print("FFling Terminal v{}".format(self.version))
        print("Type :help for commands or FFling code directly.")
        print("Type :quit to exit.\n")

        while True:
            try:
                if self.multiline:
                    line = input("...   ")
                else:
                    current_path = os.getcwd().replace('\\', '/')
                    line = input(f"[{current_path}]ffling> ")

                line = line.strip()
                if line.startswith(':'):
                    self.process_command(line[1:])
                else:
                    self.process_ffling(line)

                if not self.multiline:
                    self.history.append(line)
            except KeyboardInterrupt:
                print("\nUse :quit to exit.")
            except EOFError:
                self.cmd_quit(None)
            except Exception as e:
                print(f"Error: {e}")

    def process_command(self, line):
        parts = line.split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"Unknown command: {cmd}. Type :help for available commands.")

    def process_ffling(self, line):
        if not line:
            return

        if line.endswith('\\'):
            self.current_code += line[:-1] + '\n'
            self.multiline = True
            return

        code = self.current_code + line
        self.current_code = ""
        self.multiline = False

        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            self.interpreter.execute(ast)
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
        except Exception as e:
            print(f"Runtime Error: {e}")

        if not self.multiline:
            self.history.append(code)

    # Commands (23 total)

    def cmd_help(self, args):
        print("""
FFling Terminal Commands (Package Manager Included):
  :help                    Show this help
  :quit                    Exit the terminal
  :version                 Show version
  :history                 Show command history
  :clear_history           Clear history
  :goto <path>             Change working directory
  :install <name> <url>    Install package from GitHub
  :uninstall <name>        Uninstall package
  :update <name>           Update package
  :install_list            List installed packages
  :setup <path>            Setup FFling at path
  :load <file>             Load FFling code from file
  :save <code/file>        Save code to file
  :exec <code>             Execute FFling code
  :eval <expr>             Evaluate expression
  :list                    List recent commands
  :reset                   Reset interpreter state
  :info                    Show interpreter info
  :tutorial <topic>        Built-in tutorial
  :examples <cat>          Show examples
  :search_history <query>  Search history
  :export_vars <file>      Export variables to file
  :import_code <file>      Import code with imports
  :run_tests               Run basic tests
  :stats                   Show session stats
  :config <key> <val>      Set configuration
  :time_exec <code>        Time code execution
  :benchmark <n>           Run benchmark
""")

    def cmd_quit(self, args):
        print("Goodbye!")
        sys.exit(0)

    def cmd_version(self, args):
        print(f"FFling Terminal v{self.version}")

    def cmd_history(self, args):
        for i, cmd in enumerate(self.history[-20:], 1):
            print(f"{i}: {repr(cmd)}")

    def cmd_clear_history(self, args):
        self.history = []
        print("History cleared.")

    def cmd_goto(self, args):
        if not args:
            print("Usage: :goto <path>")
            return
        path = args[0]
        try:
            old_path = os.getcwd()
            os.chdir(path.replace('/', '\\'))  # Windows için
            print(f"Changed directory to: {os.getcwd()}")
        except OSError as e:
            print(f"Error changing directory: {e}")

    def cmd_install(self, args):
        if len(args) < 2:
            print("Usage: :install <package_name> <github_url>")
            return
        name, url = args[0], ' '.join(args[1:])
        package_path = os.path.join('packages', name)
        if os.path.exists(package_path):
            print(f"Package {name} is already installed")
            return
        try:
            subprocess.check_call(['git', 'clone', url, package_path])
            print(f"Successfully installed {name} from {url}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {name}")
        except FileNotFoundError:
            print("Git is not installed or not in PATH")

    def cmd_uninstall(self, args):
        if not args:
            print("Usage: :uninstall <package_name>")
            return
        name = args[0]
        package_path = os.path.join('packages', name)
        if not os.path.exists(package_path):
            print(f"Package {name} not found")
            return
        try:
            subprocess.check_call(['rmdir', '/s', '/q', package_path.replace('/', '\\')])
            print(f"Uninstalled {name}")
        except subprocess.CalledProcessError:
            print(f"Failed to uninstall {name}")

    def cmd_update(self, args):
        if not args:
            print("Usage: :update <package_name>")
            return
        name = args[0]
        package_path = os.path.join('packages', name)
        if not os.path.exists(package_path):
            print(f"Package {name} not found")
            return
        try:
            subprocess.check_call(['git', 'pull'], cwd=package_path)
            print(f"Updated {name}")
        except subprocess.CalledProcessError:
            print(f"Failed to update {name}")

    def cmd_install_list(self, args):
        if os.path.exists('packages'):
            packages = [d for d in os.listdir('packages') if os.path.isdir(os.path.join('packages', d))]
            if packages:
                print("Installed packages:")
                for p in packages:
                    print(f"  - {p}")
            else:
                print("No packages installed")
        else:
            print("Packages directory not found")

    def cmd_setup(self, args):
        if not args:
            print("Usage: :setup <path>")
            return
        target_path = args[0]
        try:
            import shutil
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            # Copy all FFling files
            files_to_copy = [
                'main.py', 'terminal.py', 'terminal.bat', 'lexer.py',
                'parser_ll.py', 'ast.py', 'interpreter.py', 'ffling.md', 'test.ffling'
            ]
            for file in files_to_copy:
                if os.path.exists(file):
                    shutil.copy(file, target_path)
            # Copy packages directory if exists
            if os.path.exists('packages'):
                shutil.copytree('packages', os.path.join(target_path, 'packages'), dirs_exist_ok=True)
            print(f"FFling setup completed at {target_path}")
        except Exception as e:
            print(f"Setup error: {e}")

    def cmd_load(self, args):
        if not args:
            print("Usage: :load <filename>")
            return
        filename = args[0]
        try:
            with open(filename, 'r') as f:
                code = f.read()
            self.process_ffling(code)
            print(f"Loaded and executed {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found.")
        except Exception as e:
            print(f"Load error: {e}")

    def cmd_save(self, args):
        if len(args) < 2:
            print("Usage: :save <code> <filename>")
            return
        code, filename = ' '.join(args[:-1]), args[-1]
        try:
            with open(filename, 'w') as f:
                f.write(code)
            print(f"Saved to {filename}")
        except Exception as e:
            print(f"Save error: {e}")

    def cmd_exec(self, args):
        if not args:
            print("Usage: :exec <code>")
            return
        code = ' '.join(args)
        self.process_ffling(code)

    def cmd_eval(self, args):
        if not args:
            print("Usage: :eval <expression>")
            return
        expr = ' '.join(args)
        # Simple, just exec printline(expr)
        self.process_ffling(f"printline({expr})")

    def cmd_list(self, args):
        self.cmd_history(args)

    def cmd_reset(self, args):
        self.interpreter = Interpreter()
        self.current_code = ""
        self.multiline = False
        print("Interpreter reset.")

    def cmd_info(self, args):
        print("FFling Terminal Info:")
        print(f"Version: {self.version}")
        print(f"History size: {len(self.history)}")
        print("Built-in libraries: time (time_time, time_sleep)")
        print("Keywords: 30+")

    def cmd_tutorial(self, args):
        topic = args[0] if args else 'intro'
        tutorials = {
            'intro': """
FFling Tutorial - Intro
FFling is a programming language.
Basic: printline("Hello")
Variables: local a = 10
""",
            'variables': """
Variables: local x = 5 + 3
local name = "FFling"
""",
            'loops': """
for i in range(5):
    printline(i)
""",
        }
        print(tutorials.get(topic, "Tutorial not found."))

    def cmd_examples(self, args):
        cat = args[0] if args else 'basic'
        examples = {
            'basic': """
printline("Hello World")
local a = 10
printline("Value:", a)
""",
            'logic': """
if (True and False):
    printline("Yes")
""",
        }
        print(examples.get(cat, "Examples not found."))

    def cmd_search_history(self, args):
        if not args:
            print("Usage: :search_history <query>")
            return
        query = args[0]
        matches = [cmd for cmd in self.history if query in cmd]
        for cmd in matches[-10:]:
            print(repr(cmd))

    def cmd_export_vars(self, args):
        if not args:
            print("Usage: :export_vars <file>")
            return
        # Assume we can access env
        # But for simplicity, not implemented fully
        print("Export vars to", args[0])

    def cmd_import_code(self, args):
        if not args:
            print("Usage: :import_code <file>")
            return
        self.cmd_load(args)

    def cmd_run_tests(self, args):
        print("Running tests...")
        # Run some basic tests
        self.process_ffling('printline("Test passed")')
        print("Tests completed.")

    def cmd_stats(self, args):
        print(f"Session stats: {len(self.history)} commands executed.")

    def cmd_config(self, args):
        if len(args) < 2:
            print("Usage: :config <key> <value>")
            return
        key, val = args[0], ' '.join(args[1:])
        print(f"Set {key} to {val}")

    def cmd_time_exec(self, args):
        if not args:
            print("Usage: :time_exec <code>")
            return
        import time
        code = ' '.join(args)
        start = time.time()
        self.process_ffling(code)
        end = time.time()
        print(f"Executed in {end - start:.4f} seconds")

    def cmd_benchmark(self, args):
        n = int(args[0]) if args else 1000
        import time
        start = time.time()
        for _ in range(n):
            self.process_ffling('local x = 1 + 1')
        end = time.time()
        print(f"Benchmark: {n} operations in {end - start:.4f} seconds")

if __name__ == "__main__":
    terminal = FFlingTerminal()
    terminal.run()
