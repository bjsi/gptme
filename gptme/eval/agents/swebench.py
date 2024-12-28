import logging
import time
import uuid

from gptme.cli import get_name
from gptme.dirs import get_logs_dir
from gptme.eval.agents.fix import Fix
from gptme.eval.agents.reproduce import Reproduce
from gptme.eval.agents.understand import Understand
from gptme.eval.swe_extra.swe_bench_test_spec import instance_to_trajectory_info, make_test_spec
from gptme.tools.read import reset_file_read_cache
from swebench.harness.constants import SWEbenchInstance

logger = logging.getLogger(__name__)

class SWEBenchAgent:
    def act(
        self,
        model: str,
        instance: SWEbenchInstance,
        repo_dir: str,
        log_dir: str,
        steps: list[str] = ["understand", "reproduce", "fix"],
        **kwargs
    ):
        reset_file_read_cache()
        init_info = instance_to_trajectory_info(instance, model)
        init_info.save_to_log_dir(log_dir)
        files = Understand().act(model=model, instance=instance, repo_dir=repo_dir, log_dir=log_dir, **kwargs.get("understand", {}))
        init_info.artifacts.update(files)
        init_info.save_to_log_dir(log_dir)
        files = Reproduce().act(model=model, instance=instance, repo_dir=repo_dir, log_dir=log_dir, context=init_info.artifacts, **kwargs.get("reproduce", {}))
        init_info.artifacts.update(files)
        init_info.save_to_log_dir(log_dir)
        files = Fix().act(model=model, instance=instance, repo_dir=repo_dir, log_dir=log_dir, **kwargs.get("fix", {}))
        init_info.artifacts.update(files)
        init_info.save_to_log_dir(log_dir)
        return files

    def evaluate_instance(
        self,
        instance: SWEbenchInstance,
        model: str = "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        **kwargs
    ):
        instance_id = instance["instance_id"]
        problem_statement = instance["problem_statement"]
        test_spec = make_test_spec(instance)

        logger.info(f"Evaluating instance: {instance_id}")
        logger.debug(f"Problem statement: {problem_statement}")

        _id = uuid.uuid4().hex[:8]
        name = get_name(f"gptme-evals-{model.replace('/', '--')}-{_id}")
        log_dir = get_logs_dir() / name

        start_time = time.time()
        try:
            logger.info(f"Executing agent for instance {instance_id}")
            logger.info(f"Setting up repo for instance {instance_id}")
            repo_dir = test_spec.setup_repo()
            logger.info(f"Finished setting up repo for instance {instance_id} {repo_dir}")
            SWEBenchAgent().act(model=model, instance=instance, repo_dir=repo_dir, log_dir=log_dir, **kwargs)
            gen_time = time.time() - start_time
            logger.info(
                f"Agent execution completed for instance {instance_id} in {gen_time:.2f} seconds"
            )
            passed = test_spec.eval_repo()
            logger.info(f"Evaluation completed for instance {instance_id}. Passed: {passed}")
        except Exception as e:
            import traceback
            logger.error(f"Error during agent execution for instance {instance_id}: {e}\n{''.join(traceback.format_tb(e.__traceback__))}")

