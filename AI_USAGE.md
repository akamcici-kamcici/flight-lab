# AI Usage Disclosure

## Tools used
Claude (Anthropic), web chat interface.

## What I used it for
- Understanding the assignment requirements and planning the order of work.
- Writing and debugging the code in the four modules.
- Fixing a syntax error in query.py that appeared after pasting the code.

## Parts of the code that were AI-generated or substantially AI-assisted
- validator.py: load_airports, validate_row, to_record
- csv_loader.py: parse_files
- query.py: run_query, run_queries and helper functions
- flight_parser.py: main() and its helper functions (argparse setup, logging, JSON output)

## Conversation link
https://claude.ai/share/ed863390-d31b-467b-9e2d-efa0408a074d

## Key prompts
- I pasted the full assignment text and asked Claude to work through it step by step with me.
- I pasted each starter file and asked Claude to fill in only the required code, without changing existing comments or adding new ones.
- I pasted the public test output and asked Claude to fix the failing parts.

## What I changed or verified myself
I ran the public test script after each module and fixed the problems it reported. All public tests pass. I set the student constants myself.