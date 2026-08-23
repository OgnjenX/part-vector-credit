# Apical dendrite and layer-1 mapping

## Architecture-specific map

| Source/model | Top-down source and target | Inhibition | Relation to distal apical dendrite | Relation to NDNF+ cells | Match to Francioni |
|---|---|---|---|---|---|
| pART, [Grossberg 2018](https://doi.org/10.1177/2398212818772179) | Prefrontal, sensory, orbitofrontal, amygdala, hippocampal, and basal-ganglia representations are composed for structural/temporal credit. | Competitive fields and inhibitory interneurons occur at multiple representational stages. | pART is not a compartmental model of the RSC L5 dendrites measured by Francioni. | No explicit NDNF mapping identified. | **Absent** as a direct cellular mapping. |
| SMART, [Grossberg & Versace 2008](https://doi.org/10.1016/j.brainres.2008.04.024) | Higher cortical L6II projects to lower L1 and contacts L5 apical dendrites; another branch reaches specific thalamus. | Cortical folded feedback recruits lower L4 inhibitory competition; thalamic feedback uses TRN. | **SOURCE-DERIVED:** a direct higher-feedback/apical target exists in the model. | SMART does not identify the inhibitory elements as NDNF+ interneurons. Its modeled off-surround is not simply an inhibitory current delivered by the higher axon onto the imaged distal dendrite. | Direct for “higher feedback can reach L1/L5 apical dendrites”; speculative for the exact RSC/NDNF opponent circuit. |
| Canonical laminar circuit, [Grossberg 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8102731/) | Higher L6→lower L1/L5, then L5→L6→L4 folded feedback. | Lower circuit balances a top-down excitatory center with inhibition and suppresses nonmatches. | Supports the plausibility of an apical entry point across cortical systems. | No explicit NDNF cell-type identification. | **Plausible** canonical extrapolation, not an anatomical demonstration. |
| Francioni et al. 2026, [Nature](https://doi.org/10.1038/s41586-026-10190-7) | The experiment measures apical dendritic and somatic calcium in task-participating RSC L5 cells. It does not identify a unique cortical feedback source for the residual. | L1 NDNF+ activation suppresses dendritic measures, task/reward information, and learning; somatic activity is also reduced. | **SOURCE-DERIVED:** the measured compartment and L1 manipulation are causally relevant. | Direct experimental involvement, but the manipulation does not reveal whether endogenous NDNF activity carries center, surround, gain, or another signal. | The empirical target. |
| Generic L1 physiology | L1 receives diverse long-range inputs; local interneurons regulate distal dendrites. | Neurogliaform/NDNF-like cells can inhibit distal apical dendrites and dendritic electrogenesis. [Jiang et al. 2013](https://doi.org/10.1038/nn.3305), [Abs et al. 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6226614/) | Supports a biophysical route from feedback and inhibition to dendritic calcium. | Cell-type plausibility, not Grossberg attribution. | **GENERIC NEUROBIOLOGY.** |

## What is justified

**SOURCE-DERIVED:** SMART contains a learned higher-to-lower feedback pathway terminating in lower layer 1 on L5 apical dendrites. This is a genuine Grossbergian apical bridge, not an invention of EXP003.

**CROSS-SYSTEM EXTRAPOLATION:** the same motif operates in the association-cortical RSC circuit and is driven by the pART causal representation relevant to the BCI.

**NEW HYPOTHESIS:** the opponent inhibitory component seen in the effective SMART on-center/off-surround is implemented at the measured distal compartment by, or depends specifically on, NDNF+ circuitry. The primary SMART circuit places important surround generation downstream in folded cortical and thalamic inhibitory loops. “SMART predicts NDNF” is therefore not warranted.

## Axon and compartment questions that remain open

1. Which higher area supplies task- and context-specific feedback to these RSC L5 apical tufts?
2. Is its projection learned or fixed, and at what cellular resolution?
3. Does that projection directly depolarize P+ relative to P− dendrites, or does local inhibition generate the role sign?
4. Does endogenous NDNF activity carry an opponent signal, regulate gain/plateaus, or only determine whether dendritic events remain measurable?
5. Does the same pathway influence soma strongly enough that soma-conditioned regression removes its optical signature?

## Experimental mapping needed

Use projection-specific axon imaging/manipulation, cell-type-specific NDNF recording, and simultaneous dendritic voltage/calcium or current inference. The key causal design separates:

- higher excitatory feedback suppression;
- NDNF inhibition suppression/activation;
- motor/BCI output preservation;
- sensory feedback and reward preservation.

If suppressing the identified top-down source eliminates cell-role dendritic structure before materially changing sensory error or reward, A1/A5 gain support. If the structure survives complete removal of that source, the proposed Grossbergian bridge is falsified at its anatomical bottleneck.
