# Lesson 8

## Overview

This project demonstrates an **Autonomous Iterative Improvement Process** using Aider. It guides you through a complete workflow where an AI model helps refine a high-level idea into structured, actionable code changes. The process includes:

- **Input:** A high-level idea provided by the user.
- **Prompt Refinement:** Iterative improvement of the idea into a detailed, structured prompt.
- **Code Generation:** AI-assisted code updates based on the refined prompt.
- **Execution & Evaluation:** Running the generated code and automatically evaluating its output.
- **Final Verification:** Both automated and human reviews to confirm success.

## Key Components

- **Configuration & Prompts:**  
  - Uses a YAML configuration file (`auto_aider_config.yaml`) and an external prompt file to set up the project.
  
- **AiderAgent Class:**  
  - Orchestrates the process from prompt refinement through code generation, execution, and evaluation.
  
- **Iterative Improvement:**  
  - The system loops through generating, executing, and evaluating code until the objectives are met.

## Getting Started

1. **Prerequisites:**  
   - Python 3.x installed.
   - Required Python packages (e.g., `pyyaml`, `pydantic`, `rich`).

2. **Setup:**  
   - Ensure `auto_aider_config.yaml` and the prompt file (e.g., `prompt.md`) are available in the project directory.

3. **Run the Project:**  
   - Execute the script using:
     ```bash
     python3 <script_name>.py
     ```
   - Follow the prompts to enter your high-level idea and monitor the iterative process.
