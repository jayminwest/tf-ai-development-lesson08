#!/usr/bin/env python3
"""
Autonomous Iterative Improvement Process with Aider

This tool first asks the user for a high-level idea. It then uses Aider’s chat
(as a substitute for the /ask command) to inspect the code and determine what is
needed to implement the idea. A structured prompt is generated that includes:
  - High-Level Prompt: The overall vision and objectives.
  - Mid-Level Prompt: A breakdown into components and intermediate steps.
  - Low-Level Prompt: Detailed actionable tasks with examples.

The tool then shows the generated prompt to the user and asks for confirmation
to run it. Once confirmed, it uses the structured prompt for code generation,
execution, and evaluation in an iterative process.
"""

from pydantic import BaseModel
from typing import Optional, List, Literal
from pathlib import Path
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
import yaml
import subprocess
import argparse
import json

# Define the structure for the evaluation result (for automated evaluation)
class EvaluationResult(BaseModel):
    success: bool
    feedback: Optional[str]

# Configuration schema for the Aider Agent
class AiderAgentConfig(BaseModel):
    prompt: str
    coder_model: str
    evaluator_model: str
    max_iterations: int
    execution_command: str
    context_editable: List[str]
    context_read_only: List[str]
    evaluator: Literal["default"]

class AiderAgent:
    """Autonomous Code Generation and Iterative Improvement System"""

    def __init__(self, config_path: str = "aider_agent_config.yaml", prompt_path: Optional[str] = None):
        self.config = self._validate_config(Path(config_path), prompt_path)
        # Initialize Aider's coder (using the model specified in the config)
        self.coder = Coder.create(
            main_model=Model(self.config.coder_model),
            io=InputOutput(yes=True),
            fnames=self.config.context_editable,
            read_only_fnames=self.config.context_read_only,
            auto_commits=False,
            suggest_shell_commands=False,
        )

    def _validate_config(self, config_path: Path, prompt_path: Optional[str] = None) -> AiderAgentConfig:
        """Load and validate configuration from YAML and prompt file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            config_dict = yaml.safe_load(f)

        # Use CLI provided prompt path if available, otherwise use the prompt path from config
        prompt_path = Path(prompt_path) if prompt_path else Path(config_dict["prompt"])
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path) as f:
            config_dict["prompt"] = f.read()

        return AiderAgentConfig(**config_dict)

    def build_structured_prompt(self, high_level_idea: str) -> str:
        """
        Use Aider's run command to generate a structured prompt.
        The response is expected to be JSON with keys: "high_level", "mid_level", "low_level".
        """
        ask_prompt = f"""I have the following high-level idea: "{high_level_idea}".
Please analyze this idea and return a JSON response with the following structure:
{{
    "high_level_goals": ["List of high level goals"],
    "mid_level_goals": ["List of concrete, measurable objectives"],
    "implementation_guidelines": {{
        "technical_details": ["Important technical details"],
        "dependencies": ["Dependencies and requirements"],
        "coding_standards": ["Coding standards to follow"],
        "other_guidance": ["Other technical guidance"]
    }},
    "project_context": {{
        "beginning_files": ["List of files that exist at start"],
        "ending_files": ["List of files that will exist at end"]
    }},
    "low_level_goals": [
        {{
            "task": "Task description",
            "prompt": "What prompt would run to complete this task",
            "file": "What file to work on",
            "function": "What function to work on",
            "details": "Additional details for consistency"
        }}
    ]
}}

Do not make any code changes. Only return the JSON response.
"""
        response = self.coder.run(ask_prompt)
        try:
            prompt_json = json.loads(response)
            structured_prompt = "# Architect Prompt Template\n"
            structured_prompt += "Process this file working through each step to ensure each objective is met.\n\n"
            
            # High Level Goals
            structured_prompt += "## High Level Goals\n\n"
            for goal in prompt_json.get('high_level_goals', []):
                structured_prompt += f"- {goal}\n"
            
            # Mid Level Goals
            structured_prompt += "\n## Mid Level Goals\n\n"
            for goal in prompt_json.get('mid_level_goals', []):
                structured_prompt += f"- {goal}\n"
            
            # Implementation Guidelines
            structured_prompt += "\n## Implementation Guidelines\n"
            impl = prompt_json.get('implementation_guidelines', {})
            for detail in impl.get('technical_details', []):
                structured_prompt += f"- {detail}\n"
            for dep in impl.get('dependencies', []):
                structured_prompt += f"- {dep}\n"
            for std in impl.get('coding_standards', []):
                structured_prompt += f"- {std}\n"
            for guide in impl.get('other_guidance', []):
                structured_prompt += f"- {guide}\n"
            
            # Project Context
            structured_prompt += "\n## Project Context\n\n"
            structured_prompt += "### Beginning files\n"
            for file in prompt_json.get('project_context', {}).get('beginning_files', []):
                structured_prompt += f"- {file}\n"
            
            structured_prompt += "\n### Ending files\n"
            for file in prompt_json.get('project_context', {}).get('ending_files', []):
                structured_prompt += f"- {file}\n"
            
            # Low Level Goals
            structured_prompt += "\n## Low Level Goals\n"
            structured_prompt += "> Ordered from first to last\n\n"
            for i, task in enumerate(prompt_json.get('low_level_goals', []), 1):
                structured_prompt += f"{i}. **{task.get('task', '')}**  \n"
                structured_prompt += "```code-example\n"
                structured_prompt += f"What prompt would you run to complete this task? {task.get('prompt', '')}\n"
                structured_prompt += f"What file do you want to work on? {task.get('file', '')}\n"
                structured_prompt += f"What function do you want to work on? {task.get('function', '')}\n"
                structured_prompt += f"What are details you want to add to ensure consistency? {task.get('details', '')}\n"
                structured_prompt += "```\n\n"
        except Exception as e:
            print("Error parsing structured prompt:", e)
            structured_prompt = response  # fallback to raw response
        return structured_prompt

    def generate_code(self, prompt: str):
        """
        Generate code using Aider's Deepseek model.
        This step includes the high-, mid-, and low-level details contained in the prompt.
        """
        print("[A-C] Generating/updating code based on the prompt...")
        self.coder.run(prompt)

    def execute_code(self) -> str:
        """
        Execute the generated code.
        (Steps D & E: Command execution and applying changes.)
        """
        print("[D-E] Executing the generated code...")
        result = subprocess.run(
            self.config.execution_command.split(),
            capture_output=True,
            text=True,
        )
        return result.stdout + result.stderr

    def evaluate_output(self, execution_output: str) -> EvaluationResult:
        """
        Evaluate the execution output.
        (Steps G & H: Automated verification and overall evaluation.)
        """
        evaluation_prompt = f"""Evaluate the following execution output:
{execution_output}

Return JSON with the structure: {{
    "success": bool,
    "feedback": string or null
}}"""
        response = self.coder.chat(evaluation_prompt)
        try:
            evaluation_json = json.loads(response)
            evaluation = EvaluationResult(**evaluation_json)
        except Exception as e:
            print("Error parsing evaluation response:", e)
            evaluation = EvaluationResult(success=False, feedback="Parsing error")
        return evaluation

    def final_review(self) -> bool:
        """
        Perform a final automated review.
        (Step K: Final automated review.)
        """
        review_prompt = "Perform a final automated review of the updated project. Return JSON with structure: {\"review_passed\": bool}"
        print("[K] Performing final automated review...")
        response = self.coder.chat(review_prompt)
        try:
            review_json = json.loads(response)
            return review_json.get("review_passed", False)
        except Exception as e:
            print("Error parsing final review response:", e)
            return False

    def human_final_verification(self) -> bool:
        """
        Request human final verification.
        (Step L: Human final verification.)
        """
        response = input("Does the final review meet your expectations? (y/n): ").strip().lower()
        return response == "y"

    def run(self):
        """
        Run the autonomous iterative improvement process.
        First, prompt the user for a high-level idea, generate a structured prompt,
        and ask for confirmation before running the iterative process.
        (Steps I & J: Iteratively generate, execute, and evaluate until success.)
        """
        # Step 1: Get high-level idea from the user.
        high_level_idea = input("Enter your high-level idea: ").strip()
        if not high_level_idea:
            print("No idea provided. Exiting.")
            return

        # Step 2: Build a structured prompt using Aider's chat (simulating /ask).
        structured_prompt = self.build_structured_prompt(high_level_idea)
        
        # Save the prompt to JSON file
        prompt_data = json.loads(self.coder.run(f"""I have the following high-level idea: "{high_level_idea}".
Please analyze this idea and return a JSON response with the following structure:
{{
    "high_level": "Overall vision and objectives",
    "mid_level": "Components and intermediate steps",
    "low_level": "Detailed actionable tasks with examples"
}}

Do not make any code changes. Only return the JSON response.
"""))
        
        with open('aider_auto_prompt.json', 'w') as f:
            json.dump(prompt_data, f, indent=2)
            
        print("\nGenerated Structured Prompt:\n")
        print(structured_prompt)
        print("\nPrompt saved to: aider_auto_prompt.json")
        confirm = input("Do you want to run this prompt? (y/n): ").strip().lower()
        if confirm != "y":
            print("Prompt execution canceled.")
            return

        # Use the structured prompt for the iterative improvement process.
        evaluation = EvaluationResult(success=False, feedback=None)
        for i in range(self.config.max_iterations):
            print(f"\n--- Iteration {i+1}/{self.config.max_iterations} ---")

            # Generate (and update) code based on the structured prompt
            self.generate_code(structured_prompt)

            # Execute the generated code
            output = self.execute_code()
            print("Execution Output:\n", output)

            # Evaluate the output
            evaluation = self.evaluate_output(output)
            print("Evaluation Result:", evaluation)

            if evaluation.success:
                print("Automated evaluation indicates success!")
                break
            else:
                print("Automated evaluation did not meet goals.")
                if evaluation.feedback:
                    print("Feedback:", evaluation.feedback)
                print("Repeating the automated process with updated code generation...\n")

        if evaluation.success:
            # Final automated review (Step K)
            if self.final_review():
                print("Final automated review PASSED!")
            else:
                print("Final automated review FAILED.")
                return

            # Human final verification (Step L)
            if self.human_final_verification():
                print("Human verification PASSED!")
                print("Project updated successfully! (Step M)")
            else:
                print("Human verification FAILED. Please review the changes.")
        else:
            print("Failed to achieve success within maximum iterations")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Autonomous Code Generation and Iterative Improvement System using Aider"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Path to the prompt markdown file",
        default=None
    )
    args = parser.parse_args()

    agent = AiderAgent(prompt_path=args.prompt)
    agent.run()
