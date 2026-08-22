# Parameter log

## Development version 0 (pre-run)

Chosen before any EXP002 seed was run:

- neurons 10; balanced random hidden roles;
- hypotheses 48; maximum ART categories 28; vigilance 0.88;
- action frames 8; seven visual bins; five distractors;
- causal strength initially 0.34; transition noise 0.018; soma noise 0.045;
- exploration 0.32 linearly to 0.06 within each learning epoch;
- scalar value learning rate 0.22; eligibility decay 0.82; WM persistence 0.94;
- motor scale 0.27; initial top-down scale 0.04; outstar rate 0.075;
- 220/40 episodes before remap and 220/40 after remap;
- development seeds 20-27; untouched confirmatory seeds 2000-2029.

Rationale: parameters were selected for numerically stable bounded activity, multiple state
transitions per episode, nontrivial random-basis selection, and a top-down time constant slower
than one trial. They are not claimed as biological fits. Development failures and every change
will be appended below; no confirmatory parameter changes are allowed after freezing.

## Development revision 1 — task scale only

Development v0 showed 0% binary success for every non-vector condition despite mean visual-state
improvement of about 0.28 for the bandit/primary versus 0.11 frozen. The vector control was 100%.
Thus the original scale made the binary endpoint non-discriminating. A declared development sweep
tested causal strengths 0.55, 0.75, 0.95, 1.20, and 1.50 without changing the learning rules.
Strength 1.50 was selected because it was the first tested value at which scalar selection crossed
substantial success (development bandit 0.603 pre-remap and 0.384 post-remap) while frozen/random
remained 0.156-0.191. The final causal strength is 1.50. The strong-support behavior floor was
lowered from the uncalibrated draft 0.55 to 0.35 before protocol freeze; the paired-control and
all cellular criteria remain unchanged.

## Development revision 2 — positive-control measurement only

The explicit vector control's motor policy learned `c`, but its dendritic variable did not contain
the explicit teaching event; its residual therefore could not validate the analysis. A fixed gain
of 3.0 now expresses `error_improvement * c` after sensory feedback in that control only. The gain
was chosen before rerunning development to make the deliberately supplied vector measurable over
apical noise; it is excluded from every Grossberg/generic-routing condition.
