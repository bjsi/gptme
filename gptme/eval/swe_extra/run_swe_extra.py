from gptme.eval.swe_extra.swe_bench_extra_data import load_top_50_easiest_task_instances
import logging
from gptme.eval.agents.swebench import SWEBenchAgent


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    instance = load_top_50_easiest_task_instances()[0]
    agent = SWEBenchAgent()
    agent.evaluate_instance(instance, **{"understand": {"max_turns": 20}})
