# EXP003b results

## Development checkpoint (not confirmatory)

Canonical development output is `results/exp003b/development_v2`; the invalid
evaluation-learning run remains in `development_v1`.

Across four development seeds, the primary model exceeded frozen/random behavior
and learned top-down alignment (`T` alignment 0.340 before remap and 0.410 after).
The old expectation was poorly aligned to the remapped role (0.069), and the new
one reorganized. The learned top-down pathway had a real local effect: it created
spikes on 0.96% of cell-frames and advanced comparable first-spike latency by
6.29 ms; lower weights changed by norm 0.263.

Nevertheless, the primary within-hypothesis longitudinal chain failed:
pre-remap `D→W=0.020`, `D→S=0.020`; post-remap `D→W=-0.056`, `D→S=0.025`.
All intervals crossed zero. Context opposition was 0.167, below the 0.25 floor.
The explicit vector-credit control passed behavior and all longitudinal endpoints,
showing that the task and analysis can detect the intended chain.

No change was made in response. The frozen held-out result will be appended below
after the single confirmation run.

## Held-out confirmation

Pending at protocol-freeze commit.
