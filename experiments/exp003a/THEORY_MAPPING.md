# EXP003a theory mapping

## Scope and claim boundary

EXP003a tests one local mechanism from Grossberg and Versace (2008): whether a
supplied top-down match can alter a lower cell's state and spike timing, thereby
altering the local SMART weight rule and the cell's response to a later identical
feedforward input. It does not implement pART, reward learning, learned top-down
expectancies, a BCI, or the full SMART circuit.

The implementation is therefore called **SMART-derived reduced STDP**, not SMART.
Outcome A means that this reduced motif reproduces the preregistered qualitative
mechanism. It does not validate the complete SMART model or show that the brain
uses this mechanism.

Primary source: Grossberg, S. & Versace, M. (2008), “Spikes, synchrony, and
attentive learning by laminar thalamocortical circuits,” *Brain Research* 1218,
278–312. [Official manuscript](https://sites.bu.edu/steveg/files/2016/06/GroVer2008BR.pdf),
[DOI](https://doi.org/10.1016/j.brainres.2008.04.024).

## Exact source equations used

SMART Equation 5, using the paper's notation, is

\[
\frac{dw_{jk}}{dt}
=
\lambda f_G(V_k,\bar g_{jk})
\left[
\bar g_{jk} f_N(V_k)(\hat w-\check w)+w_0-w_{jk}
\right].
\]

Here \(\check w\) and \(\hat w\) are the lower and upper bounds and \(w_0\) is
the baseline. The implementation preserves this bounded differential equation.

SMART Equation 6 defines \(f_N\) after a postsynaptic spike at time \(s\):

\[
f_N(t)=
\begin{cases}
-10(t-s)+D+1,&s<t<s+0.1\ \mathrm{ms},\\
-\dfrac{D}{25}(t-s-0.1\ \mathrm{ms})+D,
&s+0.1\le t<s+25.1\ \mathrm{ms},\\
0,&\text{otherwise},
\end{cases}
\]

with \(f_N(s)=D+1\) and

\[
D=\frac{\check w-w_0}{\check w-\hat w}.
\]

`equation6_post_signal` implements those intervals in milliseconds. The source
also specifies \(f_G(V_k,\bar g_{jk})=V_k^2\) for the plastic lower synapses used
in SMART.

## Mapping table

| Source mechanism | Theoretical role | Code implementation | Status and known simplification |
|---|---|---|---|
| SMART Eq. 3 dual-exponential conductance | Converts presynaptic spikes to a local conductance trace | `normalized_presynaptic_conductance`; the Brian2 feedforward synapse uses the same rise/fall trace | Grossberg-derived form; normalized to unit peak and scaled by a dimensionless gain rather than SMART's biophysical conductance units |
| SMART Eq. 5 | Local bounded synaptic learning | `equation5_update` | The bracketed law and bounds are retained; explicit Euler is applied between Brian2 presentations |
| SMART Eq. 6 | Makes plasticity depend on postsynaptic spike timing | `equation6_post_signal` and `local_post_signal` | Piecewise timing function retained in milliseconds |
| SMART \(f_G=V_k^2\) | Postsynaptic local gate on learning | Reduced to `f_G = f_N**2` | **Major reduction.** Eq. 6's normalized post-spike state is used as a voltage/activity proxy; raw Brian2 membrane voltage is not inserted into Eq. 5 |
| Top-down ART match | Modulatorily primes the matched lower population | A supplied top-down spike raises `g_td` in one lower cell four milliseconds before equivalent feedforward input | Grossberg-derived principle; supplied, not learned, and reduced to one spike source |
| Top-down on-center/off-surround | Selects the matched population and suppresses competitors | Direct excitatory center projection plus a spiking surround interneuron inhibiting the other cell | Reduced explicit motif, not SMART's full laminar/thalamic circuit |
| Mismatch/reset | Breaks resonant timing and suppresses attentive learning | A mismatch spike recruits a spiking reset interneuron that inhibits both lower cells | Qualitative reduced analogue; mismatch detection and beta reset dynamics are not modeled |
| Spike-timing-dependent lower learning | Match causes suitable timing; competitors and mismatches do not | The same local Eq. 5/6 function receives only each synapse's pre/post spikes and current weight | Mechanism under test; there is no condition label or top-down value in the update API |
| Learned lower weight affects later conductance | Closes the learning-to-future-response loop | Brian2 synaptic conductance is multiplied by the updated `w`, then probed with learning and top-down input off | Directly represented |

## What is not imported from Grossberg

- The two-cell conductance-based LIF equations are an engineering reduction of
  SMART's multi-compartment Hodgkin–Huxley neurons.
- Parameter calibration is specific to this motif and is not a fit to the
  original SMART simulations.
- Brian2 evolves the circuit at 0.05 ms; the Eq. 5 update is integrated outside
  Brian2 at 0.01 ms after each 80 ms presentation. This operator splitting is an
  engineering convenience.
- The mismatch source is supplied by the experiment. The motif does not discover
  mismatch or generate SMART's gamma-to-beta transition.
- EXP003a supplies which lower cell is expected. It does not learn an expectancy
  or identify a hidden causal population.

## Information-flow audit

The local plasticity function accepts only:

\[
(w,\;t_{pre},\;t_{post},\;t_{start},\;t_{stop},\;\theta_{local}).
\]

It has no top-down, match, mismatch, reward, error, target, cell-label, or hidden
causal-role argument. Top-down input can affect a weight only by changing the
Brian2 lower neuron's voltage trajectory and postsynaptic spike times. Identical
local spike histories yield identical updates. No statement such as
`if mismatch: learning_rate = 0` exists.
