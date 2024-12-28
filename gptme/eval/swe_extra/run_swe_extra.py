import argparse
from pathlib import Path
from gptme.eval.agents.swebench import SWEBenchAgent
from gptme.eval.swe_extra.swe_bench_extra_data import load_top_50_easiest_task_instances

def main():
    parser = argparse.ArgumentParser(description='Run SWE-bench evaluation')
    parser.add_argument('-r', '--resume', 
                       help='Resume from a previous run directory',
                       type=str)
    args = parser.parse_args()

    instance = load_top_50_easiest_task_instances()[0]
    agent = SWEBenchAgent()
    
    kwargs = {"understand": {"max_turns": 25}}
    if args.resume:
        agent.evaluate_instance(instance, resume_dir=Path(args.resume).expanduser(), **kwargs)
    else:
        agent.evaluate_instance(instance, **kwargs)

if __name__ == "__main__":
    main()
    log_dir = Path("~/.local/share/gptme/logs/2024-12-28-gptme-evals-openrouter--qwen--qwen-2.5-coder-32b-instruct-609a2ae1").expanduser()
