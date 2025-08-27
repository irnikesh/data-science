import argparse, os, time, pathlib
from .llm import LLM
from .agent import run_agent

def main():
    parser = argparse.ArgumentParser(description="Agent LLM Starter")
    parser.add_argument("--task", required=True, help="What should the agent do?")
    parser.add_argument("--model", default=os.getenv("MODEL", ""), help="Override model (e.g., 'qwen2.5:3b' or 'openai/gpt-4o-mini')")
    parser.add_argument("--max_steps", type=int, default=5)
    args = parser.parse_args()

    model = args.model or os.getenv("MODEL", "qwen2.5:3b")
    # normalize to ollama shorthand if needed
    if not model.startswith("openai/") and not model.startswith("ollama/"):
        model = model  # allow "qwen2.5:3b" style
    llm = LLM(model=model)

    final, transcript = run_agent(llm, args.task, max_steps=args.max_steps, verbose=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = pathlib.Path("outputs"); out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"report-{ts}.md"
    out_file.write_text(final, encoding="utf-8")
    print(f"\nSaved report to {out_file}")

if __name__ == "__main__":
    main()
