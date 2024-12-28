import argparse
from pathlib import Path
import glob
import os
from gptme.eval.agents.swebench import SWEBenchAgent
from gptme.eval.swe_extra.swe_bench_extra_data import load_instance_by_id, load_top_50_easiest_task_instances
from gptme.dirs import get_logs_dir
from gptme.logmanager import SWEBenchInfo

def get_most_recent_log_dir():
    """Get the most recent log directory from the gptme logs folder."""
    logs_dir = get_logs_dir()
    log_dirs = glob.glob(str(logs_dir / "*gptme-evals-*"))
    if not log_dirs:
        return None
    return Path(max(log_dirs, key=os.path.getctime))

def main(resume_dir: str | Path | None = None, **kwargs):
    """
    Run SWE-bench evaluation.
    
    Args:
        resume_dir: Path to resume from. If 'auto', uses most recent run. If None, starts new run.
        **kwargs: Additional arguments passed to evaluate_instance
    """
    agent = SWEBenchAgent()
    
    eval_kwargs = {"understand": {"max_turns": 25}}
    eval_kwargs.update(kwargs)
    
    if resume_dir:
        if resume_dir == 'auto':
            resume_dir = get_most_recent_log_dir()
            if not resume_dir:
                print("No previous runs found to resume")
                return
            print(f"Auto-resuming from most recent run: {resume_dir}")
        else:
            resume_dir = Path(resume_dir).expanduser()
        info = SWEBenchInfo.load_from_log_dir(resume_dir)
        if not info: raise ValueError(f"No info found in {resume_dir}")
        instance = load_instance_by_id(info.instance_id)
        agent.evaluate_instance(instance, resume_dir=resume_dir, **eval_kwargs)
    else:
        agent.evaluate_instance(instance, **eval_kwargs)

def cli():
    """Command-line interface entry point"""
    parser = argparse.ArgumentParser(description='Run SWE-bench evaluation')
    parser.add_argument('-r', '--resume', 
                       help='Resume from a previous run directory. If no directory specified, resumes most recent run.',
                       nargs='?',
                       const='auto',
                       type=str)
    args = parser.parse_args()
    main(resume_dir=args.resume)

if __name__ == "__main__":
    main("auto")
