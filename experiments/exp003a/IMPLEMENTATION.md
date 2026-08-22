# EXP003a implementation

## Reduced spiking architecture

The motif contains two exchangeable lower excitatory cells, two equivalent
feedforward spike inputs, one supplied top-down expectation input, one surround
interneuron, and one reset interneuron.

```text
feedforward 0 ── W0 (plastic) ──> lower cell 0
feedforward 1 ── W1 (plastic) ──> lower cell 1

                                ┌── excitatory on-center ──> selected cell
top-down expectation ───────────┤
                                └── surround interneuron ─> competitor

mismatch source ───────────────────> reset interneuron ───> both lower cells
```

Both feedforward neurons spike at 20 ms in every 80 ms presentation. In the
matched condition, top-down input arrives at 16 ms and selects cell 0. Top-down
input alone remains subthreshold. Its combination with the later feedforward
conductance causes the selected cell to spike; the explicit surround circuit
suppresses the competitor. The shuffled condition selects cell 1. The ablated
condition omits top-down spikes. In mismatch, an input at 17 ms recruits broad
inhibition before feedforward arrival.

## Brian2 lower-cell dynamics

Each lower cell is a conductance-based leaky integrate-and-fire neuron:

\[
\tau_m\dot V=
E_L-V+g_{ff}(E_E-V)+g_{td}(E_E-V)+g_I(E_I-V).
\]

The feedforward trace is

\[
g_{ff}(t)=G_{ff}w
\frac{e^{-t/\tau_{fall}}-e^{-t/\tau_{rise}}}{\text{peak normalization}},
\]

with \(\tau_{rise}=0.5\) ms and \(\tau_{fall}=30\) ms. This is the same normalized
trace passed to the reduced Eq. 5 integrator. Top-down and inhibitory conductances
decay exponentially with 8 ms constants. The circuit uses explicit Euler at
0.05 ms.

The interneurons are spiking LIF units rather than numerical labels. Top-down
input recruits the surround interneuron, and mismatch input recruits the reset
interneuron. Their spikes, not a condition branch inside the plasticity function,
produce inhibition.

## SMART-derived reduced Eq. 5/6

The full equations and source mapping are in [THEORY_MAPPING.md](THEORY_MAPPING.md).
For each presentation and each plastic feedforward synapse:

1. Brian2 produces membrane trajectories and pre/post spike times.
2. The local dual-exponential presynaptic trace \(\bar g\) and exact Eq. 6
   post-spike signal \(f_N\) are reconstructed at 0.01 ms.
3. The reduced postsynaptic gate is \(f_G=f_N^2\).
4. Eq. 5 is integrated by explicit Euler and clipped only to its stated
   \([\check w,\hat w]\) bounds.
5. The resulting weight is written into the Brian2 feedforward synapse before
   the next presentation.

This is operator splitting, not an event-driven Brian2 STDP rule. It was chosen
so the source equation and all intermediate terms remain inspectable. It also
makes the scientific limitation explicit: `f_G` is a normalized post-spike proxy,
not SMART's raw compartment voltage.

## Future-response probe

Before and after 24 plasticity presentations, the code creates a fresh network
and presents eight identical feedforward-only inputs. Top-down input and learning
are off. The only difference is the measured feedforward weight. Spike count and
first-spike latency therefore test the chain

\[
\Delta W\rightarrow\Delta g_{ff}\rightarrow\Delta S_{future}.
\]

## Default parameters

| Parameter | Value | Unit / meaning |
|---|---:|---|
| Lower cells | 2 | neurons |
| Training presentations | 24 | 80 ms cycles |
| Feedforward time | 20 | ms in cycle |
| Top-down time | 16 | ms in cycle |
| Mismatch time | 17 | ms in cycle |
| Brian2 step | 0.05 | ms |
| Eq. 5 integration step | 0.01 | ms |
| Membrane time constant | 10 | ms |
| Feedforward rise / fall | 0.5 / 30 | ms |
| Top-down / inhibition decay | 8 / 8 | ms |
| Rest / reset / threshold | -65 / -65 / -50 | mV |
| Excitatory / inhibitory reversal | 0 / -80 | mV |
| Initial / baseline weight | 0.60 / 0.50 | dimensionless |
| Minimum / maximum weight | 0.05 / 1.00 | dimensionless |
| Eq. 5 learning rate | 0.02 | ms\(^{-1}\) |
| Feedforward / top-down gain | 0.60 / 0.42 | dimensionless |
| Surround / reset gain | 1.35 / 2.50 | dimensionless |
| Feedforward-only probe | 8 | presentations |

The complete machine-readable parameter set is stored in every `summary.json`.

## Code map

- `src/part_credit/exp003a/motif.py`: Brian2 motif, operator splitting, and
  learning-off future probe.
- `src/part_credit/exp003a/plasticity.py`: Eq. 3 conductance, Eq. 6 timing signal,
  reduced Eq. 5 integration, and pair-timing curve.
- `src/part_credit/exp003a/experiment.py`: conditions, metrics, figures, and
  A/B/C decision gates.
- `src/part_credit/exp003a/cli.py`: append-only output directory guard and CLI.
- `tests/test_exp003a_smart_motif.py`: mechanistic and information-boundary tests.
