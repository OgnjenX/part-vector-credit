# EXP005 theory analysis

Status: **PRE-IMPLEMENTATION / HARD STOP ACTIVE**

## Distinct learning problems

EXP004 tested selection and storage:

```text
fixed population responses
  -> scalar outcome selects a useful response
  -> outstar T stores the selected response
```

EXP005 asks for construction:

```text
initially uninformative H-to-RSC projection A
  -> locally varying neural exploration
  -> scalar outcome
  -> signed coordinate-specific changes in A
```

ART category creation, pART temporal credit, and outstar storage remain genuine
learning, but none of them alone computes the last arrow. Structural credit answers
“which representation owns the outcome?” Cellular topology credit asks “which
coordinates of that representation caused the outcome, and in which direction?”

## Information-theoretic requirement

Let the BCI drive be `u = centered(S) dot c / N`, with hidden random balanced `c`.
If every adaptive coordinate receives only identical variables `(H, R)`, then any
permutation-symmetric initialization and update preserves exchangeability. There is
no information that can correlate coordinate `i` with `c_i`.

Locally distinct activity can break symmetry, but Hebbian storage of `S_i` is not
enough: it must be linked to outcome in a way that separates causal covariance from
irrelevant activity. A perturbation estimator does this because, under small
independent zero-mean perturbations,

`E[(R-b) xi_i]` is proportional to the local reward sensitivity to first order.

That is a valid derivative-free source of neuron-specific information. It is also
the missing new algorithmic assumption.

## Audit of the most favorable Grossberg composition

| Required component | Published support | Sufficiency |
|---|---|---|
| Active causal representation `H` | pART working memory / structural credit | Explicit and sufficient for ownership |
| Exploration | SOVEREIGN/aVITE ERG | Explicit at behavior/vector level; neuron-resolved form is an extrapolation |
| Delayed reinforcement | pART/CogEM/Now Print | Explicit for temporal credit and value |
| Stable distributed storage | outstar/ART expectations | Explicit if a suitable postsynaptic target already exists |
| Local perturbation trace | No matching source equation found | Missing |
| Scalar-outcome × local-trace update | No matching source equation found | Missing and decisive |
| Arbitrary bidirectional cellular sign | VAM has signs only via structured difference vectors | Missing under scalar-only boundary |

The first four components cannot logically substitute for the last three. Calling
their addition “Grossberg-derived” would turn compatibility into attribution.

## Hard-gate consequence

EXP005 is classified **Outcome E** at the theory gate. The scientific deliverable is
the negative source audit plus a separately labeled generic perturbation comparison,
if implemented. There is no Grossberg-primary held-out confirmation to run.

Future discovery of a primary Grossberg equation containing a local exploratory
eligibility, delayed scalar reinforcement, and bidirectional coordinate-specific
update could reopen the gate. It would require a new preregistration, not a silent
reinterpretation of this stage.

