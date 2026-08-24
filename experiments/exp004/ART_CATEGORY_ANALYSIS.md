# EXP004 ART category analysis

## What remains plastic

The clean primary model has a fixed motor bank but is not a lookup table. At every action frame it:

1. complement-codes the visible context, normalized action phase, and current BCI state;
2. ranks existing prototypes by fuzzy-ART choice;
3. rejects prototypes below vigilance;
4. recruits an uncommitted category if search exhausts the committed set;
5. modifies a resonant prototype by fuzzy intersection;
6. selects h from the category-specific value row;
7. assigns delayed outcome to the maintained category–hypothesis trace;
8. updates the category–hypothesis T toward the experienced soma target.

The prototype update is

\[
P_k^+=P_k+\beta[\min(I,P_k)-P_k],\qquad\beta=0.15.
\]

The motor pattern remains exactly \(B_h\). New category creation allocates a representational memory slot; it does not allocate a new action vector.

## Recorded trajectories

Every category event archives episode, action frame, event type, category ID, reset count, prototype before/after, and change norm. These records independently recover:

- recruitment time and proliferation;
- reset/search frequency;
- prototype trajectories;
- observations grouped by each category;
- context/category normalized mutual information;
- the hypotheses selected in each category;
- the soma targets and T updates owned by every category–h pair.

## Prespecified category conditions

| Condition | Recruitment | Prototype modification | Initial structure | Scientific question |
|---|---:|---:|---|---|
| Full primary ART/outstar | Yes | Yes | Uncommitted | Do search, recruitment, and prototype learning help discover/use topology? |
| Fixed categories | No | No | Complete context×phase×state-bin grid | Is a fixed contextual partition sufficient? |
| No new category | No after initialization | Yes | Two context-start prototypes | Can broad, plastic categories share structural credit better than fragmented search? |
| No category modification | Yes | No | Uncommitted | Does recruitment alone suffice? |
| Contextual bandit | No ART | No ART | Explicit discrete context×phase×state table | Does ART add anything beyond scalar Q(state,h)? |

The no-new-category condition is not “no learning”: its two prototypes can change, its values and T memories learn, and it can select different h across closed-loop frames. It specifically removes uncommitted-category proliferation.

## Development observation retained before freeze

At controlled medium coverage, full ART recruited about 10 categories and changed prototypes hundreds of times. A two-category no-recruitment ablation performed better than full ART on all four development mappings. This suggests full state fragmentation may divide outcome evidence among too many \(V_{k,h}\) slots. No parameter was changed to remove this result.

The held-out question is therefore two-sided: category construction could reduce interference, but excessive recruitment could make structural credit harder. “More ART” is not assumed beneficial.

## Category-dependent T criterion

For every h selected in more than one category, EXP004 measures the normalized distance among the corresponding T vectors. R3 requires both:

- a category-dependent T distance of at least 0.10; and
- a held-out behavioral advantage of at least 0.10 over the contextual-bandit/fixed-category comparison with a seed-bootstrap interval above zero.

Different memory slots alone do not establish factorization if they store the same selected motor response.
