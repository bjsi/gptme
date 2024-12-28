import json
import logging
import os
from pathlib import Path
import time
import uuid

from gptme.cli import get_name
from gptme.dirs import get_logs_dir
from gptme.eval.agents.fix import Fix
from gptme.eval.agents.reproduce import Reproduce
from gptme.eval.agents.understand import Understand
from gptme.eval.swe_extra.swe_bench_test_spec import instance_to_trajectory_info, make_test_spec
from gptme.logmanager import LogManager, SWEBenchInfo 
from gptme.message import print_msg
from gptme.tools import execute_msg, init_tools
from gptme.tools.read import reset_file_read_cache, save_file_read_cache
from swebench.harness.constants import SWEbenchInstance

logger = logging.getLogger(__name__)

class SWEBenchAgent:
    stages = ["understand", "reproduce", "fix"]
    def act(
        self,
        model: str,
        instance: SWEbenchInstance,
        repo_dir: str,
        log_dir: str,
        resume: bool = False,
        start_stage: str = "understand",
        **kwargs
    ):

        # Initialize or load trajectory info
        trajectory_info = instance_to_trajectory_info(
            instance, 
            model, 
            repo_dir=repo_dir,
            log_dir=log_dir if resume else None
        )
        
        if not resume:
            trajectory_info.save_to_log_dir(log_dir)
            
        # Understand
        if self.stages.index(start_stage) <= self.stages.index("understand"): 
            Understand().act(model=model, instance=instance, repo_dir=repo_dir, log_dir=log_dir, info=trajectory_info, **kwargs.get("understand", {}))
            
        # Reproduce
        if self.stages.index(start_stage) <= self.stages.index("reproduce"):
            Reproduce().act(model=model, instance=instance, repo_dir=repo_dir, log_dir=log_dir, info=trajectory_info, **kwargs.get("reproduce", {}))

        # Fix
        if self.stages.index(start_stage) <= self.stages.index("fix"):
            Fix().act(model=model, instance=instance, repo_dir=repo_dir, log_dir=log_dir, info=trajectory_info, **kwargs.get("fix", {}))
            
        # reset_file_read_cache() # maybe remove
        return trajectory_info.artifacts
    
    def get_resume_stage(self, log_dir: str) -> str:
        understand_manager = LogManager.load(log_dir, lock=False, create=True, branch="understand")
        reproduce_manager = LogManager.load(log_dir, lock=False, create=True, branch="reproduce")
        fix_manager = LogManager.load(log_dir, lock=False, create=True, branch="fix")
        if not understand_manager.log.messages:
            return "understand"
        elif not reproduce_manager.log.messages:
            return "reproduce"
        elif not fix_manager.log.messages:
            return "fix"
        return "understand"
    
    def replay(self, log_dir: str):
        logger.info(f"Replaying from log directory: {log_dir}")
        info = SWEBenchInfo.load_from_log_dir(log_dir)
        os.chdir(info.repo_dir)
        init_tools()
        understand_manager = LogManager.load(log_dir, lock=False, create=True, branch="understand")
        reproduce_manager = LogManager.load(log_dir, lock=False, create=True, branch="reproduce")
        fix_manager = LogManager.load(log_dir, lock=False, create=True, branch="fix")
        for msg in understand_manager.log.messages:
            if msg.role == "assistant":
                for reply_msg in execute_msg(msg, lambda _: True):
                    print_msg(reply_msg, oneline=False)
        files = {}
        save_file_read_cache(ignore_files=["understanding.md", "read_cache.json"])
        read_file_json = Path(info.repo_dir) / "read_cache.json"
        with open(read_file_json, "r") as f: files.update({"read_cache.json": json.load(f)})
        info.artifacts.update(files)
        info.save_to_log_dir(log_dir)
        for msg in reproduce_manager.log.messages:
            if msg.role == "assistant":
                for reply_msg in execute_msg(msg, lambda _: True):
                    print_msg(reply_msg, oneline=False)
        for msg in fix_manager.log.messages:
            if msg.role == "assistant":
                for reply_msg in execute_msg(msg, lambda _: True):
                    print_msg(reply_msg, oneline=False)

    def evaluate_instance(
        self,
        instance: SWEbenchInstance,
        model: str = "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        resume_dir: Path | None = None,
        **kwargs
    ):
        instance_id = instance["instance_id"]
        problem_statement = instance["problem_statement"]
        info = SWEBenchInfo.load_from_log_dir(resume_dir) if resume_dir else None
        if resume_dir and not info: raise ValueError(f"No info found in {resume_dir}")

        test_spec = make_test_spec(instance, info.repo_dir if info else None)

        logger.info(f"Evaluating instance: {instance_id}")
        logger.debug(f"Problem statement: {problem_statement}")

        if resume_dir:
            log_dir = resume_dir
            logger.info(f"Resuming from log directory: {log_dir}")
            test_spec.reset_repo()
            self.replay(log_dir)
            repo_dir = info.repo_dir
        else:
            _id = uuid.uuid4().hex[:8]
            name = get_name(f"gptme-evals-{model.replace('/', '--')}-{_id}")
            log_dir = get_logs_dir() / name
            repo_dir = test_spec.setup_repo()

        start_time = time.time()
        try:
            logger.info(f"Executing agent for instance {instance_id}")
            logger.info(f"Setting up repo for instance {instance_id}")
            logger.info(f"Finished setting up repo for instance {instance_id} {repo_dir}")
            
            SWEBenchAgent().act(
                model=model, 
                instance=instance, 
                repo_dir=repo_dir, 
                log_dir=log_dir,
                resume=bool(resume_dir),
                start_stage=self.get_resume_stage(log_dir) if resume_dir else "understand",
                **kwargs
            )
            
            gen_time = time.time() - start_time
            logger.info(
                f"Agent execution completed for instance {instance_id} in {gen_time:.2f} seconds"
            )
            passed = test_spec.eval_repo()
            logger.info(f"Evaluation completed for instance {instance_id}. Passed: {passed}")
        except Exception as e:
            import traceback
            logger.error(f"Error during agent execution for instance {instance_id}: {e}\n{''.join(traceback.format_tb(e.__traceback__))}")

