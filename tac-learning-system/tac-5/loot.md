---
title: "TAC Lesson 5 - Close The Loops"
lesson: 5
level: Intermediate
tactic: "Always Add Feedback Loops"
source: indydevdan/loot/loot.txt
transcript: transcript.txt
video: "Close The Loops"
---

> **Full Transcript**: [[transcript.txt]] | **Source**: IndyDevDan TAC Course

# Close The Loops: More Compute, More Confidence

> Close the loop(s) and let the code write itself. Transform brittle agent workflows into self-correcting systems with strategic feedback loops. Build 'Closed Loop Prompts' that ensure your agents correct their own work so you don't have to.

## Key Concepts

### Your Most Valuable Contribution
Our most valuable contribution is the experience we create for our users. Making sure all engineering stuff does what it's meant to do is one of the most valuable things we can do.

### The Gift of Generative AI
Agentic coding presents us with a massive opportunity to have your agents test on your behalf like you never could at scales you never will achieve. This is the gift of generative AI and the agent architecture.

### The Core Validation Question
Given a unit of valuable work that's production ready, how would you, the engineer, test and validate this work? If you can answer this for every class of work and encode it into commands or tool calls, you will fly while other engineers run.

### Architecture Leverage
Codebase architecture comes into play as a massive critical leverage point. Net new code bases have a massive advantage here when it comes to validation and testing.

---

## Tactic #5: Always Add Feedback Loops

> Your work is useless unless it's tested. Always add feedback loops enables your agents to act, validate, and correct in a continuous cycle until the job is done right. By teaching your agents to test through linters, unit tests, UI tests, and end-to-end validation, you create closed-loop systems where agents self-validate their work.

### Your Work is Useless Unless Tested
Your work, my work, any engineer's work is useless unless it's tested. The ultimate test will always be your users. The next best test used to be you. Now, the next best test is an army of agents validating your entire codebase.

### Army of Agents Validation
An army of agents validating your entire code base with regression tests and most importantly with end-to-end tests. Start handing off this responsibility and teaching your agents to test.

### Closed Loop Feedback Systems
When you do this, you create closed loop feedback systems where your agent can execute, validate, and reflect on the work done in a loop until the job is done right.

---

## Common Validation Steps

Examples of validation:
- Run your linter
- Execute unit tests
- Run UI tests
- CI/CD integration tests
- Build/compile your application
- Check Datadog logs
- Monitor Sentry for errors
- Run custom evaluations
- LLM as judge workflows

### Manual Testing is a Waste of Time
Opening the browser and clicking through your new feature is a waste of time. These are all feedback loops you can now hand off to your agents - work you don't have to do anymore.

---

## In-Loop vs Out-Loop

### Terminology
In-loop agent coding means you sitting here, prompting back and forth with your agent. Out-loop is a high level prompt running through the PITER system that fires off on your isolated device. Closing the loop is letting your agent operate on work, get feedback, and continue until feedback is positive.

### Let the Code Write Itself
When you close the loop, you let the code write itself. You let the agent operate with the right information so well that it closes the loop and continues building until the feedback is positive.

### Stay Out The Loop
As you progress, you wanna be doing less and less in-loop prompting. You wanna stay out the loop, kicking off workflows that run in an agent environment.

---

## Agentic KPIs

### Great Agentic Coding KPIs
Remember, we want attempts down, we want size up, we want streak up, and we want our presence down. How do we accomplish this? With upfront investment into the new agentic layer of our code base.

### End-to-End Agents, Not In-Loop
Remember, we want end-to-end agents, not in-loop agents. We don't want to be babysitting our agents. We want work done agentically.

---

## Key Insights

### Engineers That Test With Agents Win
Now engineers that test with their agents win. Full stop, zero exceptions. This is because the value of tests are multiplied by the number of agent executions that occur in your code base.

### Confidence Through Testing
If your auth tests are passing, you can be more confident your authentication system is working. With every passing set of tests, you free your context window and you stop second guessing so you can focus on what's next for your users.

### Building the System That Builds the System
This is us building the system that builds the system. Keep this idea in mind because this is the differentiating factor between agentic engineers and engineers of the past.

---

## Related Concepts

- [[Closed Loop Systems]]
- [[Feedback Loops]]
- [[Agentic KPIs]]
- [[Validation Commands]]
- [[Test-Driven Agentic Coding]]
