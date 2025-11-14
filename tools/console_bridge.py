#!/usr/bin/env python3
"""
Supersonic Console Bridge - Bidirectional Shell Command Executor
Executes shell commands from Replit Agent console OR repo shell root.

Usage:
    python tools/console_bridge.py "git status"  # Single command
    python tools/console_bridge.py               # Interactive mode
    ./rs console "git status"                    # Via RS CLI
    ./rs console                                 # Interactive via RS CLI
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Colors for output
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[36m'
RED = '\033[31m'
BOLD = '\033[1m'
RESET = '\033[0m'

def ensure_log_dir():
    """Ensure logs directory exists"""
    Path("logs").mkdir(exist_ok=True)

def log_command(command, exit_code, source="agent"):
    """Log command execution to logs/console_bridge.log"""
    ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{source}] exit={exit_code} | {command}\n"
    
    with open("logs/console_bridge.log", "a") as f:
        f.write(log_entry)

def execute_command(command, source="agent"):
    """Execute a shell command and stream output in real-time"""
    if not command or not command.strip():
        return 0
    
    command = command.strip()
    
    # Print command being executed
    print(f"{BLUE}🚀 Executing:{RESET} {BOLD}{command}{RESET}")
    print()
    
    try:
        # Execute command with real-time output streaming
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output line by line
        if process.stdout:
            for line in process.stdout:
                print(line, end='')
        
        # Wait for process to complete
        exit_code = process.wait()
        
        # Log the command
        log_command(command, exit_code, source)
        
        # Print result
        print()
        if exit_code == 0:
            print(f"{GREEN}✅ Command completed successfully (exit code: {exit_code}){RESET}")
        else:
            print(f"{RED}❌ Command failed with exit code: {exit_code}{RESET}")
        
        return exit_code
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Command interrupted by user{RESET}")
        log_command(command, -1, source)
        return -1
    except Exception as e:
        print(f"{RED}❌ Error executing command: {e}{RESET}")
        log_command(command, -99, source)
        return -99

def interactive_mode():
    """Run in interactive REPL mode"""
    print(f"{BOLD}{BLUE}🎯 Supersonic Console Bridge - Interactive Mode{RESET}")
    print(f"{YELLOW}Type shell commands to execute them in repo root{RESET}")
    print(f"{YELLOW}Type 'exit' or press Ctrl+D to quit{RESET}")
    print()
    
    command_count = 0
    
    while True:
        try:
            # Show prompt
            prompt = f"{GREEN}supersonic${RESET} "
            command = input(prompt)
            
            # Handle empty input
            if not command.strip():
                continue
            
            # Handle exit commands
            if command.strip().lower() in ['exit', 'quit']:
                print(f"{BLUE}👋 Exiting console bridge. Executed {command_count} commands.{RESET}")
                break
            
            # Execute command
            execute_command(command, source="interactive")
            command_count += 1
            print()
            
        except EOFError:
            # Ctrl+D pressed
            print(f"\n{BLUE}👋 Exiting console bridge. Executed {command_count} commands.{RESET}")
            break
        except KeyboardInterrupt:
            # Ctrl+C pressed
            print(f"\n{YELLOW}⚠️  Interrupted. Type 'exit' to quit.{RESET}")
            continue

def main():
    """Main entrypoint for console bridge"""
    # Change to repo root if not already there
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)
    
    # Check if command provided as argument
    if len(sys.argv) > 1:
        # Single command mode
        command = ' '.join(sys.argv[1:])
        exit_code = execute_command(command, source="agent")
        sys.exit(exit_code)
    else:
        # Interactive mode
        interactive_mode()
        sys.exit(0)

if __name__ == "__main__":
    main()
