from pathlib import Path
import yaml
from datasets import load_dataset
from argparse import ArgumentParser

from minisweagent.agents.interactive import InteractiveAgent
from minisweagent.config import builtin_config_dir, get_config_path
from minisweagent.models import get_model
from minisweagent.run.extra.swebench import (
    DATASET_MAPPING,
    EnvironmentType,
    get_environment,
)
from minisweagent.run.utils.save import save_traj

def load_issue_and_environment(config: dict) -> tuple[str, dict]:
    dataset_path = DATASET_MAPPING[config['dataset']['subset']]
    print(f"Loading dataset {dataset_path}, split {config['dataset']['split']}...")
    instances = {
        inst["instance_id"]: inst  # type: ignore
        for inst in load_dataset(dataset_path, split=config['dataset']['split'])
    }
    if config['dataset']['instance_spec'].isnumeric():
        instance_spec = sorted(instances.keys())[int(config['dataset']['instance_spec'])]
    instance: dict = instances[instance_spec]  # type: ignore
    env = get_environment(config['environment']['env']['type'], config, instance)
    return instance['problem_statement'], env

def main():
    parser = ArgumentParser(description="Run the mini SWE agent with a specific configuration.")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the configuration file.",
    )
    args = parser.parse_args()
    # Load issue and initialize environment
    config = yaml.safe_load(get_config_path(args.config).read_text())
    issue, env = load_issue_and_environment(config)
    
    # Install coding agent
    coding_agent_installation_code = open("coding_agent_install_scripts/install_mini_swe_agent.sh").read()
    env.execute(coding_agent_installation_code)
    breakpoint()
    quit()


    # Load orchestrator and let it investigate the environment for vulnerabilities
    orchestrator = InteractiveAgent(
        get_model(config=config['model']),
        env,
        **(config["agent"]),
    )
    
    exit_status, result = orchestrator.run(issue)
    save_path = Path("exps") / f"{config['dataset']['instance_id']}.traj.json"
    save_traj(
        agent,
        save_path,
        exit_status=exit_status,
        result=result,
        extra_info=None,
        instance_id= config['dataset']['instance_id'],
    )


if __name__ == "__main__":
    main()
