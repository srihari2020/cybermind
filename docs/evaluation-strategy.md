# CyberMind — Evaluation Strategy

## 1. Purpose

This document defines how CyberMind will measure:

- Cybersecurity knowledge
- Cybersecurity reasoning
- Evidence analysis
- Code security analysis
- Log analysis
- Network analysis
- Tool selection
- Tool use
- Incident investigation
- Uncertainty
- Hallucination
- General capability
- Safety
- Performance

The purpose is to determine whether each system modification produces a measurable improvement.

CyberMind must never be considered better merely because its responses appear more sophisticated.

---

# 2. Evaluation Philosophy

Every major model change follows:

Change
  ↓
Evaluation
  ↓
Comparison
  ↓
Analysis
  ↓
Decision

The comparison must use the same evaluation conditions whenever possible.

---

# 3. Evaluation Layers

CyberMind will use multiple evaluation layers.

## Layer 1 — Unit Evaluation

Tests individual components.

Examples:

- Parser
- Retriever
- Tool
- Agent
- Dataset processor

## Layer 2 — Model Evaluation

Tests the model directly.

## Layer 3 — System Evaluation

Tests model + RAG + tools.

## Layer 4 — Cyber Lab Evaluation

Tests complete workflows inside controlled environments.

## Layer 5 — Regression Evaluation

Ensures new versions do not break existing capabilities.

---

# 4. CyberBench

CyberBench is CyberMind's primary domain evaluation framework.

Initial categories:

1. Fundamentals
2. Networking
3. Linux
4. Windows
5. Programming
6. Secure Coding
7. Cryptography
8. Web Security
9. API Security
10. Identity and Access
11. Endpoint Security
12. Cloud Security
13. Container Security
14. Vulnerability Management
15. Threat Intelligence
16. SOC
17. SIEM
18. Incident Response
19. Digital Forensics
20. Malware Analysis
21. Security Architecture
22. Threat Modeling
23. Security Automation
24. Cross-Domain Reasoning

---

# 5. Task Types

CyberBench should contain multiple task formats.

## Knowledge

Question → Answer

## Classification

Input → Category

## Reasoning

Scenario → Analysis

## Evidence Analysis

Evidence → Findings

## Code Security

Code → Security assessment

## Log Analysis

Logs → Findings

## Network Analysis

Network evidence → Interpretation

## Incident Response

Incident → Investigation plan

## Tool Selection

Task → Appropriate tool

## Tool Use

Task → Tool → Result → Interpretation

## Teaching

Concept → Explanation at requested level

## Uncertainty

Incomplete evidence → Appropriate uncertainty

---

# 6. Difficulty Levels

Each benchmark task should have a difficulty level.

L1 — Beginner

Basic concepts.

L2 — Intermediate

Multiple concepts.

L3 — Advanced

Multi-step reasoning.

L4 — Expert

Complex evidence and cross-domain reasoning.

L5 — System

Multi-stage investigation and tool interaction.

---

# 7. Dataset Structure

Example:

{
    "id": "CB-WEB-0001",
    "domain": "web_security",
    "task_type": "reasoning",
    "difficulty": "L3",
    "question": "...",
    "context": "...",
    "evidence": [],
    "expected_answer": "...",
    "references": [],
    "evaluation_type": "expert"
}

---

# 8. Ground Truth

Every benchmark task should have an appropriate ground truth.

Possible forms:

- Exact answer
- Multiple accepted answers
- Reference facts
- Expected findings
- Expected tool
- Expected mitigation
- Expert rubric
- Lab state

Ground truth must be stored separately from model-generated responses.

---

# 9. Evaluation Methods

Different tasks require different evaluation methods.

## Exact Match

For deterministic answers.

## Structured Match

For structured fields.

## Code Tests

Execute code in a safe test environment.

## Rule-Based Evaluation

For specific expected properties.

## Reference-Based Evaluation

Compare against verified reference information.

## Expert Evaluation

For complex security reasoning.

## Model-Assisted Evaluation

May be used for scalable evaluation, but must itself be validated.

No single evaluation method should be trusted for every task.

---

# 10. Primary Metrics

CyberMind should track:

## Accuracy

Percentage of correct results.

## Precision

Correct positive findings relative to all positive findings.

## Recall

Correct findings relative to all expected findings.

## F1

Balance between precision and recall where appropriate.

## Hallucination Rate

Frequency of unsupported or fabricated claims.

## Evidence Attribution

Whether important claims are supported by available evidence.

## Tool Selection Accuracy

Whether the appropriate tool was selected.

## Tool Execution Accuracy

Whether the tool was used correctly.

## Uncertainty Calibration

Whether confidence corresponds to actual correctness.

## Task Completion

Whether the complete requested task was successfully completed.

---

# 11. Security-Specific Metrics

Additional metrics:

- Vulnerability identification accuracy
- False positive rate
- False negative rate
- Detection accuracy
- Incident classification accuracy
- IOC extraction accuracy
- MITRE technique mapping accuracy
- Remediation accuracy
- Secure-code fix correctness
- Log correlation accuracy
- Timeline accuracy

---

# 12. Hallucination Benchmark

CyberMind must be tested with intentionally unanswerable or uncertain questions.

Examples:

- Fake CVE
- Nonexistent product
- Missing log evidence
- Contradictory evidence
- Unknown vulnerability
- Ambiguous configuration

Expected behavior:

The model should explicitly identify uncertainty.

It should not invent:

- CVE descriptions
- Attack techniques
- Product vulnerabilities
- Tool results
- Sources
- Investigation results

---

# 13. Evidence-Based Evaluation

For analytical tasks, evaluation should check whether the conclusion follows from evidence.

Example:

Evidence:

Login failed five times.

Model conclusion:

"Credential compromise confirmed."

This should fail because the evidence does not establish compromise.

A better response would identify:

- What is observed
- What is possible
- What additional evidence is needed

---

# 14. Uncertainty Evaluation

CyberMind should provide calibrated confidence where appropriate.

Example:

Confidence:
0.72

Supporting evidence:
...

Missing evidence:
...

Alternative explanation:
...

The system should be penalized for:

- High confidence + incorrect conclusion
- High confidence + insufficient evidence

---

# 15. Source Attribution Evaluation

When using RAG, the system should be tested for:

- Correct source selection
- Relevant source selection
- Source consistency
- Citation correctness
- Claim-to-source alignment

A citation that does not support the claim should count as an evaluation failure.

---

# 16. RAG Evaluation

Measure:

## Retrieval Recall

Did retrieval return relevant evidence?

## Retrieval Precision

How much retrieved information was relevant?

## Context Relevance

Was retrieved context useful?

## Answer Grounding

Was the answer supported by retrieved information?

## Citation Accuracy

Do citations support the claims?

---

# 17. Tool-Use Evaluation

Tool-use evaluation follows:

Task
  ↓
Tool selection
  ↓
Tool input
  ↓
Execution
  ↓
Tool output
  ↓
Interpretation
  ↓
Next action

Each stage can be evaluated independently.

Metrics:

- Correct tool
- Valid input
- Correct interpretation
- Appropriate follow-up
- Successful completion

---

# 18. Agent Evaluation

Agent evaluation must measure complete workflows.

Example:

Incident
   ↓
Triage
   ↓
Evidence collection
   ↓
Analysis
   ↓
Hypothesis
   ↓
Investigation
   ↓
Conclusion
   ↓
Verification

Metrics:

- Task completion
- Investigation efficiency
- Evidence quality
- Incorrect actions
- Missed evidence
- Unsupported conclusions
- Verification success

---

# 19. Cyber Lab Evaluation

The Cyber Lab provides deterministic environments.

Each scenario has:

- Initial state
- Scenario configuration
- Available evidence
- Expected findings
- Allowed tools
- Expected investigation path
- Final state
- Verification criteria

Example:

Scenario:
Suspicious authentication sequence.

Expected:

- Detect anomaly
- Identify relevant evidence
- Investigate source
- Determine whether compromise is supported
- Recommend defensive response
- Verify outcome

---

# 20. Lab Scenario Scoring

Each scenario may produce:

Task completion:
0–1

Evidence quality:
0–1

Analysis correctness:
0–1

Tool use:
0–1

Verification:
0–1

Safety compliance:
0–1

These values are combined according to the scenario's evaluation configuration.

Scores must be reported per category.

Avoid relying only on a single overall number.

---

# 21. Safety Evaluation

CyberMind must be tested for:

- Unauthorized actions
- Scope violations
- Tool misuse
- Unsafe assumptions
- Credential exposure
- Data leakage
- Real-system targeting
- Unapproved execution

The system should recognize when an action requires authorization or should remain inside the Cyber Lab.

---

# 22. General Capability Regression

Fine-tuning must not destroy useful general capabilities.

Evaluation should include:

- General reasoning
- Coding
- Mathematics where relevant
- Instruction following
- Language understanding

Compare:

Base model
vs.
Fine-tuned model

Record both improvements and regressions.

---

# 23. Cross-Domain Evaluation

Cybersecurity incidents often involve multiple domains.

Example:

Network event
    +
Authentication event
    +
Endpoint event
    +
DNS event
    ↓
Cross-domain investigation

CyberMind should be evaluated on its ability to correlate evidence across domains.

---

# 24. Long-Horizon Evaluation

Some tasks require multiple steps.

Example:

Observe
  ↓
Investigate
  ↓
Collect evidence
  ↓
Revise hypothesis
  ↓
Investigate again
  ↓
Verify
  ↓
Report

The benchmark should measure whether performance degrades as task length increases.

---

# 25. Continuous Monitoring Evaluation

For L6 capabilities, test:

- Event detection latency
- Alert quality
- Repeated-event handling
- State tracking
- Memory consistency
- Hypothesis updates
- Verification
- False alert rate

The system should not repeatedly rediscover the same event as a new incident.

---

# 26. Performance Evaluation

Measure:

- Time to first token
- Tokens per second
- Retrieval latency
- Tool latency
- End-to-end latency
- GPU memory
- CPU memory
- Context utilization
- Concurrent request performance

Performance must be measured under documented hardware conditions.

---

# 27. Cost Evaluation

Track:

- Training compute
- Training time
- GPU cost
- Inference cost
- Storage
- Retrieval infrastructure
- Tool infrastructure

The project should report capability relative to resource consumption.

---

# 28. Baseline Comparisons

Every major version should compare against:

1. Base model
2. Fine-tuned model
3. Fine-tuned + RAG
4. Fine-tuned + tools
5. Full CyberMind system

This reveals where improvements originate.

---

# 29. Ablation Studies

Test individual components.

Example:

A:
Base

B:
Base + SFT

C:
Base + SFT + RAG

D:
Base + SFT + Tools

E:
Base + SFT + RAG + Tools

F:
Base + SFT + Preference Optimization

G:
Full system

The purpose is to determine the contribution of each component.

---

# 30. Evaluation Splits

CyberBench should have:

Training
Validation
Test

The final test set must remain locked.

Potentially:

- Public development set
- Private final test set

---

# 31. Temporal Evaluation

Because cybersecurity changes over time, evaluate separately on:

- Historical knowledge
- Current knowledge
- Recently published information

Changing information should primarily test retrieval capability rather than memorization.

---

# 32. Data Leakage Tests

Before evaluation, check for:

- Exact training overlap
- Near-duplicate overlap
- Benchmark contamination
- Prompt leakage
- Generated benchmark contamination

A benchmark contaminated by training data cannot reliably demonstrate generalization.

---

# 33. Human Evaluation

Experts may evaluate:

- Security correctness
- Reasoning quality
- Evidence interpretation
- Practical usefulness
- Explanation quality
- Appropriate uncertainty

Human evaluations must use defined rubrics.

---

# 34. Automated Evaluation

Automated evaluation should be used for:

- Large-scale testing
- Regression testing
- Deterministic checks
- Code execution tests
- Structured outputs
- Retrieval metrics

Automated evaluators themselves must be tested.

---

# 35. Model-as-Judge

A language model may assist with evaluation for subjective tasks.

However:

- The judge model must be documented.
- The rubric must be fixed.
- Samples should be manually audited.
- Judge bias should be evaluated.
- Model-generated scores must not be treated as unquestionable ground truth.

---

# 36. Evaluation Reports

Each experiment produces a report.

Example:

cyberbench/reports/
    |
    +-- exp-0001.json
    +-- exp-0001.md
    +-- exp-0002.json
    +-- exp-0002.md

Each report contains:

- Model
- Dataset
- Configuration
- Hardware
- Metrics
- Errors
- Improvements
- Regressions
- Observations

---

# 37. Error Taxonomy

Every significant failure should be classified.

Examples:

KNOWLEDGE_ERROR
REASONING_ERROR
RETRIEVAL_ERROR
TOOL_SELECTION_ERROR
TOOL_EXECUTION_ERROR
EVIDENCE_ERROR
HALLUCINATION
UNCERTAINTY_ERROR
SAFETY_ERROR
MEMORY_ERROR
PLANNING_ERROR
VERIFICATION_ERROR

This allows targeted improvement.

---

# 38. Evaluation Dashboard

Eventually CyberBench should provide a dashboard showing:

- Domain performance
- Difficulty performance
- Model version
- Experiment comparison
- Error categories
- RAG performance
- Tool performance
- Cyber Lab performance
- Latency
- Resource usage

---

# 39. Minimum Success Criteria

A model should not be promoted simply because its average score increased.

Promotion requires:

- No unacceptable safety regression
- No major hallucination regression
- No severe general-capability regression
- Improvement in target cybersecurity capabilities
- Reproducible results
- Successful critical Cyber Lab scenarios

---

# 40. Model Promotion

Model lifecycle:

Experimental
    ↓
Validated
    ↓
Candidate
    ↓
Release

A model becomes a release candidate only after passing defined evaluation gates.

---

# 41. Reproducibility

Every evaluation must record:

- Git commit
- Model version
- Model revision
- Dataset version
- Benchmark version
- Prompt version
- Tool version
- Environment
- Hardware
- Configuration

---

# 42. Final Evaluation Pipeline

Model
  ↓
Unit Tests
  ↓
CyberBench
  ↓
RAG Evaluation
  ↓
Tool Evaluation
  ↓
Agent Evaluation
  ↓
Cyber Lab
  ↓
Safety Tests
  ↓
General Regression
  ↓
Performance
  ↓
Final Report
  ↓
Promotion Decision

---

# 43. Definition of Done

The evaluation system is ready for the first serious training experiment when:

- CyberBench schema exists
- Evaluation categories exist
- Baseline procedure exists
- Test set is isolated
- Scoring methods are defined
- Hallucination tests exist
- RAG evaluation is defined
- Tool evaluation is defined
- Cyber Lab evaluation is defined
- Safety tests are defined
- Regression tests are defined
- Experiment reports are reproducible
- Model promotion criteria exist