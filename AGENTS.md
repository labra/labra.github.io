# Instructions for contributors and AI agents

These rules apply to all contributors. They also apply to AI coding agents, for example Claude Code, Codex, Copilot and Cursor. If you use an agent, make sure that the agent obeys these rules.

## 1. Commit attribution

- Attribute each commit only to the human author.
- Do not add attribution lines for an AI agent or a tool. For example, do not add `Co-Authored-By: Claude …`, `Generated with …` or a session link.
- Use the same rule for pull request descriptions.

## 2. Simplified Technical English

- Write all text in Simplified Technical English (ASD-STE100).
- This rule applies to documentation, code comments, error messages, commit messages, pull request descriptions and RDF labels and comments.
- Use these STE rules:
  - Use short sentences. Write a maximum of 20 words in an instruction and 25 words in a description.
  - Write one instruction in each sentence. Use the imperative form, for example "Push the change".
  - Use the active voice.
  - Use one word for one meaning. Use the same term for the same thing.
  - Use simple verb tenses: the present, the simple past and the future.
  - Do not use contractions.
  - Use "NOTE:", "CAUTION:" and "WARNING:" to show special information.
- Before you commit, read the changed text again. Make sure that it obeys these rules.

## 3. TDD Test-driven development

- Use a TDD approach
