from gptme.eval.swe_extra.swe_bench_extra_data import load_top_50_easiest_task_instances
import json
import logging
import time
from swebench.harness.constants import SWEbenchInstance

from gptme.eval.agents import UnderstandAgent
from gptme.eval.swe_extra.swe_bench_test_spec import make_test_spec
from gptme.eval.types import CaseResult, EvalResult


logger = logging.getLogger(__name__)


def evaluate_instance(
    instance: SWEbenchInstance,
    model: str = "openrouter/qwen/qwen-2.5-coder-32b-instruct",
) -> EvalResult:
    instance_id = instance["instance_id"]
    problem_statement = instance["problem_statement"]
    test_spec = make_test_spec(instance)

    logger.info(f"Evaluating instance: {instance_id}")
    logger.debug(f"Problem statement: {problem_statement}")

    start_time = time.time()
    try:
        agent = UnderstandAgent()
        logger.info(f"Executing agent for instance {instance_id}")
        logger.info(f"Setting up repo for instance {instance_id}")
        repo_dir = test_spec.setup_repo()
        logger.info(f"Finished setting up repo for instance {instance_id} {repo_dir}")
        files = agent.act(model=model, instance=instance, repo_dir=repo_dir)
    except Exception as e:
        import traceback
        logger.error(f"Error during agent execution for instance {instance_id}: {e}\n{''.join(traceback.format_tb(e.__traceback__))}")
        return EvalResult(
            name=instance_id,
            status="error",
            results=[],
            timings={"gen": time.time() - start_time, "run": 0, "eval": 0},
            gen_stdout="",
            gen_stderr=str(e),
            run_stdout="",
            run_stderr="",
        )

    gen_time = time.time() - start_time
    logger.info(
        f"Agent execution completed for instance {instance_id} in {gen_time:.2f} seconds"
    )

    # Evaluate the result
    logger.info(f"Evaluating patch for instance {instance_id}")
    eval_start = time.time()
    diff = str(files.get("diff", ""))
    passed = evaluate_patch(instance, diff)
    eval_time = time.time() - eval_start

    logger.info(f"Evaluation completed for instance {instance_id}. Passed: {passed}")

    return EvalResult(
        name=instance_id,
        status="success",
        results=[
            CaseResult(name="patch_correctness", passed=passed, duration=eval_time)
        ],
        timings={"gen": gen_time, "run": 0, "eval": eval_time},
        gen_stdout="",
        gen_stderr="",
        run_stdout=diff,
        run_stderr="",
    )


def evaluate_patch(instance: dict, generated_patch: str) -> bool:
    logger.debug(f"Instance keys: {instance.keys()}")
    logger.debug(f"Instance content: {json.dumps(instance, indent=2)}")

    if "expected_spans" not in instance:
        logger.warning(
            "'expected_spans' not found in instance data. Using 'patch' instead."
        )
        expected_patch = instance.get("patch", "")
        logger.debug(f"Expected patch: {expected_patch}")
        logger.debug(f"Generated patch: {generated_patch}")
        return expected_patch.strip() == generated_patch.strip()

    expected_spans = instance["expected_spans"]
    generated_spans = get_file_spans_from_patch(generated_patch)

    logger.debug(f"Expected spans: {expected_spans}")
    logger.debug(f"Generated spans: {generated_spans}")

    for file_path in expected_spans.keys():
        if file_path not in generated_spans:
            logger.info(f"File {file_path} not found in generated patch")
            return False

    logger.info("All expected files found in generated patch")
    return True


if __name__ == "__main__":
    instance = load_top_50_easiest_task_instances()[0]
    test_spec = make_test_spec(instance)
    test_spec.setup_repo()
    test_spec.eval_repo()
