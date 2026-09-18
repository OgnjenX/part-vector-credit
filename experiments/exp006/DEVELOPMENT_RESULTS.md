# EXP006 development result before confirmation

Status: **DEVELOPMENT ONLY; NOT THE HELD-OUT RESULT**

The final primary development run used seeds 601--608. Values below are means and
are used only to set conservative confirmation rules.

| Model | Acquisition success | Remap success | Acquisition topology | Remap topology | Acquisition residual | Remap residual |
|---|---:|---:|---:|---:|---:|---:|
| Vector oracle | 1.000 | 1.000 | 1.000 | 1.000 | 0.154 | 0.153 |
| ART repertoire | 0.774 | 0.668 | 0.650 | 0.750 | 0.026 | 0.043 |
| Local eligibility | 1.000 | 0.500 | 0.955 | 0.347 | 0.003 | 0.001 |
| ART plus eligibility | 1.000 | 0.656 | 0.878 | 0.599 | -0.020 | -0.011 |
| Random no learning | 0.000 | 0.000 | -0.104 | 0.093 | 0.000 | approximately 0.000 |

The controls behaved in the expected direction. Outcome shuffling reduced ART late
success to approximately zero and eligibility late success to 0.110 in acquisition
and 0.016 after remapping. Removing either exploration or the temporal trace reduced
eligibility success to zero. With eligibility plasticity disabled, the hybrid
returned to fixed-repertoire behavior.

The development result already argues against a simple equivalence claim. ART
selection found useful pre-existing population patterns and generated a
role-structured internal signal, but its final topology never exceeded the best
pattern in its fixed repertoire. Local eligibility created a new acquisition
topology from scalar feedback, but its within-trial dendritic proxy was weak and it
did not fully reverse the learned topology during the equally long remap phase. The
hybrid improved acquisition speed and topology, yet its combined dendritic proxy
did not reproduce the target sign structure. Only the privileged vector oracle met
every development signature.

These observations are provisional. They define the held-out test and do not count
as confirmatory evidence.
