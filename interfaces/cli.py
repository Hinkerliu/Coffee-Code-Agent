#!/usr/bin/env python3
"""CLI interface for the coffee multi-agent system."""

import asyncio
import argparse
import sys
from pathlib import Path

from workflows.cli_workflow import CoffeeCLI


def main():
    """Main entry point for CLI."""
    try:
        cli = CoffeeCLI()
        asyncio.run(cli.run_interactive())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()