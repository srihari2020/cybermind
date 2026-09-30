# CyberMind — Training Strategy

## 1. Purpose

This document defines how CyberMind will transform an open-weight base language model into a cybersecurity-specialized model.

The objective is not simply to increase cybersecurity knowledge.

The objective is to improve:

- Cybersecurity reasoning
- Evidence interpretation
- Security terminology
- Secure coding
- Log analysis
- Network analysis
- Incident reasoning
- Tool selection
- Tool-use behavior
- Teaching ability
- Uncertainty awareness

while preserving useful general capabilities of the base model.

---

# 2. Fundamental Principle

Fine-tuning is only one component of CyberMind.

The final system consists of:

Base Model
    +
Domain Adaptation
    +
Instruction Fine-Tuning
    +
Preference Optimization
    +
RAG
    +
Tool Use
    +
Cyber Lab
    +
Evaluation

No single component should be expected to solve every problem.

---

# 3. Base Model Selection

The initial base model must be selected using measurable criteria.

Candidate models should be evaluated for:

- License
- Parameter count
- Context length
- Architecture
- Tokenizer
- Coding ability
- Reasoning ability
- Instruction following
- Quantization support
- GPU memory requirements
- Inference speed
- Fine-tuning support
- Community/tooling support
- Model quality

The project must benchmark multiple candidate models where resources permit.

---

# 4. Baseline Before Training

No fine-tuning should begin before establishing a baseline.

Pipeline:

Candidate Model
      |
      v
CyberBench
      |
      v
Baseline Results

The baseline must measure:

- General cybersecurity knowledge
- Domain reasoning
- Code understanding
- Security analysis
- Evidence interpretation
- Tool planning
- Hallucination
- Uncertainty
- Response latency

The baseline becomes the reference point for all later experiments.

---

# 5. Model Selection Experiment

Candidate models will be compared using the same evaluation dataset.

Example:

Model A
Model B
Model C
Model D

Each receives identical:

- Prompts
- Evaluation scenarios
- Context
- Tool availability

The model should be selected using the project's requirements rather than parameter count alone.

---

# 6. Training Stages

CyberMind training will be progressive.

Stage 0
Baseline

Stage 1
Domain-adaptive experimentation

Stage 2
Supervised fine-tuning

Stage 3
Tool-use training

Stage 4
Preference optimization

Stage 5
Cyber Lab scenario training

Stage 6
Final evaluation

Stage 7
Inference optimization

---

# 7. Stage 0 — Baseline

Run the base model against CyberBench.

Record:

- Model identifier
- Model revision
- Hardware
- Quantization
- Prompt format
- Temperature
- Context size
- Generation parameters
- Evaluation results

Store results in:

cyberbench/reports/

---

# 8. Stage 1 — Domain Adaptation Experiment

Domain-adaptive training may be evaluated using high-quality cybersecurity text.

Potential material:

- Cybersecurity standards
- Technical documentation
- Security frameworks
- Approved educational material
- Security research

The purpose is to investigate whether additional domain exposure improves cybersecurity language understanding.

This stage must be evaluated carefully for:

- Catastrophic forgetting
- Repetition
- Over-specialization
- Reduced general reasoning
- Dataset contamination

Domain adaptation should not automatically be assumed to improve performance.

---

# 9. Stage 2 — Supervised Fine-Tuning

SFT will teach CyberMind desired response behaviors.

Training examples may include:

- Questions and answers
- Security scenarios
- Code analysis
- Log analysis
- Network analysis
- Incident scenarios
- Teaching examples
- Evidence-based reasoning
- Tool selection
- Uncertainty expression

Example:

Scenario
    |
    v
Evidence
    |
    v
Analysis
    |
    v
Conclusion
    |
    v
Recommended next step

---

# 10. SFT Techniques

Initial experiments should prioritize parameter-efficient fine-tuning.

Primary candidates:

- LoRA
- QLoRA

Benefits:

- Lower VRAM requirements
- Faster experiments
- Easier checkpoint management
- Multiple adapters
- Lower storage requirements

Full-parameter fine-tuning should only be considered after evidence justifies it.

---

# 11. Training Configuration

Every training run must store:

- Base model
- Dataset version
- Dataset mixture
- LoRA configuration
- Quantization configuration
- Learning rate
- Scheduler
- Batch size
- Gradient accumulation
- Number of epochs
- Maximum sequence length
- Warmup
- Weight decay
- Precision
- Random seed
- Hardware
- Training framework
- Git commit

Example experiment:

cybermind-exp-0001

---

# 12. Dataset Mixing

Training data should be deliberately mixed.

Example conceptual mixture:

General instruction data
        +
Cybersecurity knowledge
        +
Security reasoning
        +
Secure coding
        +
Evidence analysis
        +
Tool-use examples
        +
Teaching examples

The exact proportions will be determined experimentally.

The model should retain enough general capability to avoid becoming narrowly specialized.

---

# 13. Curriculum Strategy

Training may be organized from simpler to more complex capabilities.

Level 1:

Fundamentals

Level 2:

Domain reasoning

Level 3:

Evidence analysis

Level 4:

Multi-step investigation

Level 5:

Tool use

Level 6:

Controlled Cyber Lab scenarios

The curriculum should be evaluated experimentally rather than assumed to be optimal.

---

# 14. Reasoning Data

CyberMind should be trained to produce useful reasoning behavior.

Examples should encourage:

- Evidence identification
- Hypothesis generation
- Alternative explanations
- Missing evidence
- Verification
- Confidence estimation

The model should not be trained to fabricate hidden reasoning or claim that it performed actions it did not perform.

The desired output is an auditable reasoning summary.

Example:

Evidence:
...

Hypothesis:
...

Supporting evidence:
...

Contradicting evidence:
...

Missing evidence:
...

Recommended investigation:
...

Conclusion:
...

---

# 15. Tool-Use Training

Tool-use examples should teach the model:

1. Recognize when a tool is required.
2. Select the appropriate authorized tool.
3. Construct valid tool input.
4. Interpret tool output.
5. Determine whether additional evidence is needed.
6. Produce a conclusion.

Example:

Task
  |
  v
Need external evidence?
  |
  +-- No --> Reason directly
  |
  +-- Yes
       |
       v
Select tool
       |
       v
Execute authorized tool
       |
       v
Analyze result
       |
       v
Verify

---

# 16. Tool-Use Dataset

Training examples may use structured records.

Example:

{
    "task": "...",
    "available_tools": [
        "log_analyzer",
        "code_analyzer"
    ],
    "selected_tool": "log_analyzer",
    "tool_input": {},
    "tool_output": {},
    "interpretation": "...",
    "next_action": "..."
}

The actual tool execution environment remains separate from the training dataset.

---

# 17. Preference Optimization

After SFT, preference optimization may be evaluated.

Potential preference criteria:

Preferred responses should be:

- Correct
- Evidence-based
- Clear
- Relevant
- Explicit about uncertainty
- Secure
- Non-hallucinatory
- Actionable within authorization boundaries

Less desirable responses may contain:

- Fabricated facts
- Unsupported certainty
- Incorrect security advice
- Tool-use hallucinations
- Missing evidence
- Irrelevant information

Potential methods may include:

- DPO
- Other preference optimization approaches supported by the selected training stack

The method will be selected experimentally.

---

# 18. Preference Dataset

Example:

Prompt:
Analyze this authentication event.

Response A:
...

Response B:
...

Preference:
A

Reason:

- Better evidence usage
- Correct uncertainty
- No unsupported conclusion

Preference data must be reviewed for quality.

---

# 19. Catastrophic Forgetting

Fine-tuning must be evaluated for loss of general capabilities.

Evaluation should include:

Cybersecurity benchmark
+
General reasoning benchmark
+
Coding benchmark
+
Instruction-following benchmark

A model that improves cybersecurity but severely degrades general capability must not automatically be considered successful.

---

# 20. Hallucination Evaluation

CyberMind should be tested against:

- Fake CVEs
- Nonexistent vulnerabilities
- Invalid security configurations
- Incorrect assumptions
- Missing evidence
- Ambiguous incidents

The model should recognize uncertainty instead of inventing facts.

Example:

Input:

"CVE-2099-99999"

If the identifier cannot be verified, the model should not fabricate a vulnerability description.

---

# 21. Temporal Knowledge

Changing information should not be baked into model weights unnecessarily.

Examples:

- CVEs
- Vendor advisories
- Product versions
- Active threats

These should primarily be retrieved from the knowledge system.

Fine-tuning should focus on:

- How to reason about the information
- How to interpret it
- How to connect it to security concepts
- How to use retrieved evidence

---

# 22. Knowledge RAG Integration

Final system:

User Query
    |
    v
Intent analysis
    |
    +--------+
    |        |
    v        v
Model     Retrieval
             |
             v
        Evidence
             |
             +------+
                    |
                    v
                  Model
                    |
                    v
                 Answer

The model should distinguish retrieved evidence from its own prior knowledge.

---

# 23. Cyber Lab Training

Cyber Lab scenarios will provide realistic controlled training environments.

Example:

Scenario
    |
    v
Lab state
    |
    v
Events
    |
    v
Evidence
    |
    v
Expected investigation
    |
    v
Verification

The system can learn:

- Investigation planning
- Evidence gathering
- Tool selection
- Incident reasoning
- Verification

All experimentation remains within isolated authorized environments.

---

# 24. Multi-Agent Training

The initial model should not be split into separate fine-tuned models immediately.

First build a strong general cybersecurity model.

Then evaluate whether specialized adapters/agents are useful.

Potential specializations:

- SOC
- AppSec
- Network
- Forensics
- Cloud
- Threat Intelligence

Architecture:

                    CyberMind Core
                          |
              +-----------+-----------+
              |           |           |
             SOC        AppSec      Network
           adapter      adapter      adapter

Specialization should be justified through evaluation.

---

# 25. Training Data Versioning

Every model must reference:

- Dataset version
- Data hash
- Training configuration
- Base model revision

Example:

Model:

cybermind-sft-v0.1

Training:

cybermind-data-v0.3

Base:

base-model@revision

---

# 26. Checkpoint Strategy

Checkpoints must be saved at controlled intervals.

Each checkpoint should be evaluated.

Example:

checkpoint-100
checkpoint-250
checkpoint-500
checkpoint-1000

Do not assume the final checkpoint is the best checkpoint.

Select based on validation performance.

---

# 27. Validation

Validation data must remain separate from training.

Validation is used for:

- Hyperparameter tuning
- Checkpoint selection
- Training decisions

The final test set must remain untouched until final evaluation.

---

# 28. Final Test

The final CyberBench test set should be locked.

After training decisions are complete:

Model
    |
    v
Locked CyberBench
    |
    v
Final Results

No tuning should occur based on final test results.

---

# 29. Ablation Studies

The project should test which components actually help.

Examples:

Base Model

Base + SFT

Base + SFT + RAG

Base + SFT + Tool Use

Base + SFT + RAG + Tool Use

Base + SFT + Preference Optimization

Full System

This identifies the contribution of each component.

---

# 30. Experiment Matrix

Every major experiment should have:

Experiment ID
Base model
Dataset
Training method
Configuration
Hardware
Results
Observations

Example:

exp-0001
Base
CyberBench
Baseline

exp-0002
Base + LoRA
Cybersecurity SFT
...

exp-0003
Base + LoRA
Cybersecurity SFT + RAG
...

---

# 31. Training Hardware

Training hardware will be selected according to model size.

Initial experiments should favor parameter-efficient methods.

Potential environments:

- Local GPU
- Cloud GPU
- Kaggle
- Google Colab
- Dedicated GPU server

Hardware should be recorded for every experiment.

---

# 32. Resource Scaling

Start small.

Phase 1:

Small model
Small dataset
Short experiment

Phase 2:

Larger dataset
Longer training

Phase 3:

Larger model

Phase 4:

Full CyberMind training experiments

The project must not spend large compute resources before validating the pipeline.

---

# 33. Training Pipeline

Expected pipeline:

Dataset
   |
   v
Validation
   |
   v
Tokenizer
   |
   v
Training
   |
   v
Checkpoint
   |
   v
Validation
   |
   v
CyberBench
   |
   v
Experiment report

---

# 34. Reproducibility

Every experiment must be reproducible.

Store:

- Code commit
- Data version
- Model revision
- Configuration
- Seed
- Hardware
- Environment
- Dependencies

Environment files should be version controlled.

---

# 35. Training Safety

Training data must be filtered for:

- Malicious instructions
- Poisoning attempts
- Incorrect security information
- Fabricated vulnerabilities
- Unsafe automation instructions
- Data contamination

Cybersecurity datasets require stronger validation than ordinary instruction datasets.

---

# 36. Model Registry

Trained models should be registered.

Example:

models:

cybermind-baseline-v0.1
cybermind-sft-v0.1
cybermind-sft-v0.2
cybermind-pref-v0.1
cybermind-final-v1.0

Each model must reference its training experiment.

---

# 37. Deployment Optimization

After the best model is selected:

- Quantization
- KV-cache optimization
- Batch optimization
- Context optimization
- Inference engine optimization

Potential deployment technologies:

- Transformers
- vLLM
- Other compatible inference engines

Optimization must preserve acceptable evaluation performance.

---

# 38. Definition of Success

Training is successful only when evaluation demonstrates measurable improvement.

Minimum comparison:

Base Model
vs.
CyberMind Fine-Tuned Model

Evaluate:

- Cybersecurity knowledge
- Cybersecurity reasoning
- Evidence analysis
- Code security
- Log analysis
- Tool use
- Hallucination
- Uncertainty
- General capability
- Latency

The project must report both improvements and regressions.

---

# 39. Final Training Philosophy

The objective is not:

"Train the biggest model."

The objective is:

"Train the smallest practical model that provides the required cybersecurity capability with measurable reliability, while using RAG, tools, memory, and controlled environments where they are more appropriate than additional model parameters."