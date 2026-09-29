# SCHABLONE

*by Sebastian Schulz*

*A stencil, not a judge. It is laid over a claim and makes the shape
visible; it decides nothing.*

**A measuring instrument for claims. It does not check whether a
statement is true. It compares the fields a statement is justified in,
and reports where those fields do not fit together.**

```
10 fields per sheet · 9 comparison rules · 7 strands at the gate · 4 stages
```

The result may not live in any field. It arises *between* two of them —
which is why nobody can write it in, not even the person filling out
the form.

```bash
python3 -m schablone bogen              # the built-in attacks
python3 -m schablone erkennung          # 108 detection tests
python3 -m schablone bogen my.json      # your own sheet
```

No dependencies. Python 3 only.

---

## The problem this was built for

A claim shows up with two sources. Both say the same thing. Neither one
measured anything — the second copied the first. Counted as evidence,
that is two confirmations. Counted as failure points, it is one.

This gets worse when machines generate the claims, because a language
model will happily produce a second paragraph that agrees with the
first, and agreement reads like corroboration.

FRAME-NETWORK does not try to detect lies. It makes the shape of a
justification explicit enough that this particular class of mistake
becomes a set comparison instead of a judgment call.

---

## The idea the whole thing rests on

Every successful attack on early versions of this system went through a
**settable field**. None went through a table. If a person filling out
a form can write `verified = true`, they will, and the system learns
nothing.

So: the form asks questions. The rules compare pairs of answers. What
comes out of that comparison is *computed*, and therefore cannot be
written in.

Twenty independent fields catch nothing — they are twenty chances to
assert the same thing once. Ten fields where pairs of them must agree
catch something.

---

## Four axes

Everything the program finds lies on one of four axes. Before using it
on a case, ask: is the suspected error on one of these?

| Axis | Question | Rules |
|---|---|---|
| **Provenance** | Does the chain of grounds end at a measurement or a named author — or at nothing? | P1, P1b |
| **Independence** | Are two pieces of evidence really two, or do they fall together? | P2, P3, P6 |
| **Scope** | Does the claim hold further than its grounds carry? | P4 |
| **Time** | Do the grounds cover the period claimed? Was the falsification criterion fixed before the data? | P5, P7, P8 |

If the suspected error is a wrong *number*, this is the wrong tool.
See "What it cannot do".

---

## The one rule underneath all the others

The same non-equation, at five different layers:

```
unknown                       ≠  false
not assessed                  ≠  unobjectionable
no criterion given            ≠  an independent failure point
not answered                  ≠  stands on its own
examined and not refuted      ≠  refuted
```

An empty field is never a finding. It is a statement about what could
not be checked, and it is printed as such.

---

## The stage ladder — and why the first stage blocks nothing

A claim is not judged by its content but by its **consequences**:

```
S0   stays in conversation           blocks nothing
S1   internally quotable             form + content
S2   goes to third parties           + arithmetic, scope, time
S3   triggers action with money      + a human, second hand
```

**S0 blocking nothing is deliberate and load-bearing.** A system that
makes you prove everything before you may say it does not produce
rigour, it produces silence. Wild, unfounded, half-formed ideas are how
work starts. They only need grounding when they leave the room.

This was built in from the first version, because the author's first
objection to his own design was: *"my own system would block me."*

---

## What it measures

Reproducible with `python3 -m schablone erkennung`:

| Measurement | Value | What it does not say |
|---|---|---|
| Defects inside the ruleset, detected | **44 / 44** | whether these are the right defect classes |
| Defects outside the ruleset, detected | **0 / 24** | as expected — it is not built for those |
| False alarms on clean cases | **0 / 40** | all 40 hang on a single field |
| Probes | **47 / 47** | — |

Two rates, never one number. There is no overall score and no grade,
because a system that fires on everything would score 1.0 on the first
line.

### The counter-measurements, which belong in the same table

- The 40 clean cases all sit at **distance 1**: one empty field would
  make all forty fire. Forty cases that fail identically are one case.
- The 108 test cases are **constructed, not sampled**. No rate for a
  running system can be derived from them.
- On six real, model-filled sheets, rule P2 hit the copied figure in
  **2 of 6** cases — and fired on two genuinely separate meters in the
  other **4 of 6**. On real material the false alarm was more common
  than the hit.
- Everything measured so far comes from **one language, one domain, one
  model family**.

---

## What it cannot do

Stated plainly, because these limits are measured, not suspected.

1. **It does not check arithmetic.** The `zahlen` field is never
   populated by `nach_netz()`, so the arithmetic strand reports "no
   derived number" on every sheet. Digit transpositions, wrong units and
   sign errors pass through — measured: 0 of 24.

2. **It does not check truth.** Two fields that fit each other and are
   both wrong pass. Two invented falsification criteria pass.

3. **One hand fills every sheet.** It shifts effort; it does not build
   a wall. How far it shifts it is measured (`mindestluege`): one to two
   well-chosen changes on the built-in attacks, not twenty.

4. **It is not a defence against an adversary.** It is for honest work
   with blind spots.

---

## What this project is deliberately not

The author's constraints, not the implementer's.

- **Not a truth machine.** It reports structure. A human decides.
- **Not a score.** No single number, ever. Every metric gets its own
  denominator, and the false-alarm rate is printed next to the
  detection rate or neither is printed.
- **Not a model leaderboard.** When run against language models it
  measures how much externally given structure a model carries — not
  which model is "better".
- **Not a rubber stamp.** `FREIGABE auf S2` means "the fields are
  mutually consistent", not "the claim is correct". One reviewer called
  that line the most dangerous part of the output. He was right, and it
  is being narrowed rather than defended.
- **Not a straitjacket.** See S0 above.
- **Not for medicine, law, or safety.** There is no measurement for
  those domains, and a wrong clearance there has consequences no test
  corpus covers.
- **Not measured by attention.** View counts, stars and engagement are
  not evidence about anything this project claims. The useful signal is
  refutation, and refutation needs a name attached to it.

---

## How the project handles being wrong

This is the part that matters more than the code.

**Errors are numbered and kept.** 53 so far. They are not squashed out
of the history; the reasoning that produced each one stays in the source
as a comment, because a fixed bug with its cause deleted teaches nothing.

**Measurements are pre-registered.** What will be counted, and what
would refute the prediction, is written down and dated *before* the run.
See `VORAB_52_53.md` for the most recent one.

**Discarded measurements are documented, not hidden.** One experimental
run read the pre-registration before starting, reported this itself, and
was thrown out and repeated. That is recorded in `versuch/BEFUND_E.md`
along with the admission that contamination cannot be ruled out for the
other runs.

**The instrument is applied to its own figures.** `selbstmass.py` enters
the project's own quality numbers as sheets. Rule P4 fires on them — the
author quoted "0 false alarms out of 40" a dozen times without stating
its scope, and his own rule caught him.

### Where the last five bugs came from

Errors 49 through 53 were not found by the builders. They were found by
runs that *used* the tool for a real task and were asked what they
thought of it. Among them: a strand that reported "checked, fine" when
there was nothing to check, and a rule that fell silent when an
**unsupported** document was added to the sheet.

That is currently the best-measured source of defects in this program,
and it is the reason for the contribution request below.

---

## Contributing

The single most useful contribution is stated first in
`OFFENE_PUNKTE.md`:

> **A case from an outside hand.**

All 108 test cases and every application case so far were built by two
people. Until that changes, "0 false alarms out of 40" measures the
imagination of the people who wrote the 40.

`pruefpaket/` contains everything needed: a real case, a task, and the
sheet format. Nothing else — deliberately. Do not open `versuch/` until
after your own run; it contains the traps and the previous answers, and
reading it first is what invalidated one run already.

Other open work, in order of expected yield:

1. Numbers in the sheet format, so the arithmetic strand stops being
   structurally blind
2. Whether a stated backing actually backs anything, or is
   self-serving (P1b cannot currently tell)
3. Two independent coders and a reported kappa for the four fields that
   are not machine-comparable

---

## Honest notes for anyone reading this repository

**The source is in German.** Field names, rule names, comments, reports.
This is a real barrier to contribution and there is no translation layer
yet. Issues and discussion in English are welcome.

**The name.** A *Schablone* is a stencil: a sheet you lay over
something so its shape becomes visible. It does not draw and it does not
judge. That is the constraint the whole system is built around, and it
is also the name of the module that does the work.

**How this was built.** The framework — the fields, the rules, the stage
ladder, the non-equations — was designed by **Sebastian Schulz**. Large
parts of the implementation, the test corpus and the measurements were
produced in collaboration with a language model, working under a
standing instruction from him to attack every result rather than confirm
it. Given that this project is about provenance, saying so seemed
obligatory.

Every numbered error in this repository, every discarded measurement and
every counter-measurement in the tables above exists because that
instruction was standing. That is the working method, and it is part of
what is being published here.

**A warning about the measurements.** They are direction, not rate.
n is small almost everywhere, the corpus is constructed, and the same
hands built the defects and the rules that catch them. Every number in
this README is reproducible, and none of them generalises yet.

---

## Copyright and rights

**© 2026 Sebastian Schulz. All rights reserved.**

Sebastian Schulz is the author of SCHABLONE and holds the copyright
in this work, including the framework design — the field set, the
comparison rules, the stage ladder and the non-equations — and the
source code implementing it.

**A license does not give away copyright.** Publishing this repository
under an open-source license grants other people permission to use, copy
and modify the code. It does not transfer ownership, and it does not
stop the author from licensing the work differently to someone else.
Sebastian Schulz remains the rights holder in every case.

Two things follow that anyone reading this should know:

- **Attribution is required.** Every common open-source license,
  including the most permissive ones, requires that this copyright
  notice be kept in copies and substantial portions of the work.
- **Until a `LICENSE` file is added, this is not open source.** A public
  repository with no license file is "all rights reserved" by default:
  you may look at it, and you may not copy, modify, redistribute or
  build on it. If you want to use this, wait for the license file or
  ask.

*(This section is a plain-language description of how copyright and
licensing normally work, not legal advice. For anything that matters,
ask a lawyer.)*

---

## Where things are

```
schablone/           25 modules, 8,550 lines
  schablone.py       the pre-stage: 10 fields, 9 comparison rules
  tor.py             7 strands, 4 stages, the certificate
  kern.py            sources, network, entries
  erkennung.py       the test corpus, 108 cases
  aufnahme.py        when a rule may become a paragraph
  selbstmass.py      the project's own quality figures, as sheets
  verdacht.py        a third output type: requests work instead of blocking
  trigger.py         hallucination triggers, paired and ablated

pruefpaket/          material for running it yourself — clean
versuch/             pre-registrations, traps, answers — do not read first
boegen/              six real, model-filled sheets

ZIEL.md              what the instrument was built for
OFFENE_PUNKTE.md     what is missing, ordered by yield
ZEITANKER.md         how the program knows what day it is
LIESMICH.md          the German readme
```
