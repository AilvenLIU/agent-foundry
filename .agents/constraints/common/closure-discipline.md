# Closure Discipline

> Completion standard for every session, task, commit, and roadmap phase.
> Effort is proportional: the feature comes first, verification serves it.

## 1. Proportionality

Most effort, and most of the diff, belongs to the feature itself: design,
implementation, and edge cases. Testing, validation, documentation, and process
exist to serve it, and are sized by the real complexity and risk of the change,
never by a wish to be procedurally complete.

Before handing off, ask: do the tests, scripts, and docs I added outweigh the
feature, or does something exist that nobody asked for? If so, cut it.

## 2. Done means it works

A task is done when the feature works end to end and the parts that can really
break are tested. It is not done when every path is covered.

- Run the changed feature once, for real, and run the tests that cover it.
- Fix what that shows. One review of your own diff is enough for ordinary work.
- Do not loop on review rounds, re-prove what the code already shows, or add
  validation layers around work that is already verified.

## 3. Rigor rises with concrete risk

Go deeper only where something specific can go wrong: security boundaries,
money or data loss, migrations, public APIs, concurrency, and GPU numerics.
Use the extra tool that fits (property tests, sanitizers, a rollback plan) and
say which risk justifies it. "High-risk by category" is not a reason by itself.

## 4. Roadmap phases

A phase is closed when its "done when" criterion holds: run the thing and
observe it. Record the state in a few lines in the handoff. Do not advance to
the next phase while in-scope work is unfinished, and do not create phases or
tasks whose only output is tests, validation, hardening, or documentation.

## 5. Reporting

State plainly what changed, what ran, and what did not. Do not claim success
that was not observed, and do not pad the report.
