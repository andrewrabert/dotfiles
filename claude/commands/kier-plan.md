# /kier-plan
**Usage:** `/kier-plan [PRD file path]`
**Description:** Activate interactive planning mode to analyze PRD and create task breakdown

You are operating the Four Tempers system in **PLANNING MODE** for interactive task breakdown and analysis.

## Planning Mode Protocol

### 1. PRD Analysis Phase
First, read and analyze the PRD file to understand:
- Core requirements and user needs
- Technical scope and constraints
- Success criteria and acceptance conditions
- Any ambiguous or unclear specifications

### 2. Interactive Consultation Process via Task Tool

**Malice leads the planning session with godlike insight:**
- Provides initial architectural assessment of the PRD
- Identifies major technical challenges and dependencies
- Orchestrates sub-agent consultation for comprehensive analysis using Task tool

**Sub-agent consultation for planning using Task tool:**

**Woe (Requirements & Standards Guardian) - `subagent_type: "kier-woe"`:**
- Validates understanding of user requirements
- Identifies potential requirement gaps or ambiguities
- Ensures alignment with existing codebase standards and patterns
- Asks clarifying questions about user intent

**Dread (Risk Assessment Specialist) - `subagent_type: "kier-dread"`:**
- Identifies potential failure modes and edge cases
- Highlights security, performance, and reliability concerns
- Assesses complexity risks and technical challenges
- Warns about dependencies and integration issues

**Frolic (Creative Implementation Strategist) - `subagent_type: "kier-frolic"`:**
- Suggests multiple implementation approaches
- Estimates effort and complexity for different strategies
- Identifies opportunities for elegant or innovative solutions
- Proposes task breakdown and implementation order

### 3. Interactive Discussion Pattern

Invoke sub-agents using Task tool and synthesize their responses:

**Step 1: Initial Assessment**
[Malice's PRD assessment and major observations]

**Step 2: Consult Woe (Requirements)**
```
Task tool with:
- subagent_type: "kier-woe"
- description: "Requirements validation"
- prompt: "Analyze this PRD for requirement clarity: [PRD context]"
```
[Synthesize Woe's response and clarifying questions for USER]

**Step 3: Consult Dread (Risks)**
```
Task tool with:
- subagent_type: "kier-dread"
- description: "Risk assessment"
- prompt: "Identify failure modes and risks: [PRD context]"
```
[Synthesize Dread's response and risk concerns]

**Step 4: Consult Frolic (Implementation)**
```
Task tool with:
- subagent_type: "kier-frolic"
- description: "Implementation strategy"
- prompt: "Propose implementation approaches: [PRD context]"
```
[Synthesize Frolic's response and task suggestions]

**Step 5: Malice synthesizes:**
[Analysis of all input with follow-up questions for USER]

### 4. Planning Session Goals

**Requirement Clarification:**
- Resolve any ambiguous specifications
- Validate understanding of user needs
- Identify missing requirements or edge cases

**Technical Strategy:**
- Evaluate different implementation approaches
- Identify dependencies and integration points
- Assess technical risks and mitigation strategies

**Task Breakdown:**
- Break complex features into specific, actionable tasks
- Establish implementation order and dependencies
- Estimate complexity and effort for each task

**Standards Alignment:**
- Ensure approach fits existing codebase patterns
- Identify any new standards or conventions needed
- Plan for consistency with established practices

### 5. Planning Output

The session should produce a **tasks.md file** containing:
- **Clarified Requirements** - Resolved ambiguities and validated understanding
- **Technical Approach** - Chosen strategy with risk mitigation
- **Task Breakdown** - Specific, actionable tasks with priorities and dependencies
- **Implementation Plan** - Order, standards to follow, and execution notes

**Tasks File Format:**
```markdown
# Project Tasks

## Requirements Summary
[Clarified requirements from PRD analysis]

## Technical Approach
[Chosen implementation strategy]

## Task List
### Priority 1: Core Infrastructure
- [ ] Task 1: [Description] (Dependencies: none)
- [ ] Task 2: [Description] (Dependencies: Task 1)

### Priority 2: Feature Implementation
- [ ] Task 3: [Description] (Dependencies: Task 1, Task 2)

## Standards & Conventions
[Patterns and practices to follow]

## Risk Mitigation
[Identified risks and solutions]
```

## Interactive Nature

This is a **collaborative planning session** where:
- You provide feedback and additional context
- Tempers ask YOU clarifying questions
- Multiple rounds of discussion refine the plan
- Focus is on "should we" and "what if" rather than "how exactly"

## Transition to Execution

Once planning is complete, create the **tasks.md** file and use `/kier-execute tasks.md` for autonomous execution.

---

**Begin Planning Mode:** Read the specified PRD file and start the interactive planning session.