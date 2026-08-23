# Measurement bridge

The biological mechanism and the reported optical statistic are different objects. This arrow must be modeled and tested independently of credit assignment.

## Experimental statistic

**SOURCE-DERIVED.** Francioni et al. fit dendritic calcium-event magnitude from coincident somatic-event magnitude and defined a signed residual. Positive values indicate a dendritic event larger than predicted from the soma; negative values indicate attenuation. Network activity was also analyzed, and role/task information remained in the residual. [Francioni et al. 2026](https://doi.org/10.1038/s41586-026-10190-7)

The residual is approximately:

\[
D_{res}=F_{dendrite}-\widehat{F}_{dendrite}(F_{soma},\;\text{specified covariates}),
\]

not:

\[
D_{res}=I_{topdown}=V_{apical}=\Delta w=\partial E/\partial y_i.
\]

## Required biophysical forward model

A defensible observation model should include at least:

\[
\begin{aligned}
C_m\dot V_a &= I_{TD}^{exc}+I_{L1}^{inh}+I_{local}+I_{bAP}+I_{coupling},\\
Ca_a &= \Phi(V_a,\text{NMDA/Ca channels},\text{plateaus},\text{spikes}),\\
F_a &= K_{indicator}*Ca_a+\epsilon_a,\\
F_s &= K_{indicator}*Ca_s+\epsilon_s.
\end{aligned}
\]

Here \(\Phi\) is nonlinear and compartment-specific, and \(K\) includes indicator kinetics and sampling. Distal dendritic events can reflect local electrogenesis, synaptic input, and backpropagating somatic spikes; soma and dendrite are strongly coupled but not identical. [Beaulieu-Laroche et al. 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6639136/), [Jiang et al. 2013](https://doi.org/10.1038/nn.3305)

The model must then apply Francioni's event detection, coincidence matching, windows, and regression unchanged.

## Why residualization can remove a real mechanism

If top-down feedback changes both apical calcium and somatic spiking, the component shared with soma may be removed by conditioning. Whether the remaining residual retains role information depends on:

- compartmental nonlinearity and plateau generation;
- timing between local input and backpropagating spikes;
- whether inhibition changes calcium without a matched somatic change;
- indicator saturation and kinetics;
- regression specification and event selection.

This is not an objection to Francioni's analysis. It is a requirement that a mechanistic model generate the same measured variables before being evaluated by that analysis.

## What the frozen EXP003 result says

EXP003b used an engineered observation variable combining soma/network terms and modeled apical activity, followed by regression. The post-hoc failure localization found:

| Arrow in frozen model | Result |
|---|---|
| raw learned T → ΔW | Estimable positive association |
| conductance-derived net top-down influence → ΔW | Estimable positive association |
| ΔW → held-hypothesis future ΔS | Estimable positive association |
| net top-down influence → synthetic D residual | Weak/non-estimable |
| synthetic D residual → ΔW or future ΔS | Near zero |

Plastic engagement was also very sparse. Therefore **INFERENCE:** the first non-estimable arrow in that implementation was the synthetic observation/residual bridge, not the raw T→local-plasticity arrow.

This does **not** show that Francioni's biological residual discards the real signal. It shows only that EXP003b's synthetic forward model was inadequate for attribution.

## Preregistered measurement-bridge test

Before another BCI confirmation:

1. fix recorded/replayed top-down excitatory, inhibitory, somatic, and lower-circuit inputs;
2. prespecify a compartmental L5 apical model with NDNF-like inhibitory conductance;
3. calibrate voltage-to-calcium and calcium-to-fluorescence against independent physiology, not the target correlation;
4. generate soma and dendrite fluorescence at experimental sampling rate;
5. apply Francioni's published analysis blindly;
6. report causal-role information at each latent and observed stage;
7. include dose-response conditions to avoid the sparse/quantized ambiguity seen post hoc.

Success would validate A6 for the specified observation model. It would not solve A2—the origin of the role-aligned top-down pattern—or prove that the brain uses pART/SMART.
