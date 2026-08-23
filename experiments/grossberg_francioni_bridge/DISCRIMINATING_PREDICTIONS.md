# Discriminating predictions

Priority favors experiments that can falsify a necessary bridge assumption rather than merely reproduce another correlation.

## 1. Projection-specific top-down source perturbation — highest priority

**Manipulation.** Identify task/context-responsive cortical afferents to RSC L1 and image their axons with L5 apical/somatic activity. Suppress the candidate source selectively during (a) pre-action/ongoing control, (b) sensory feedback, or (c) outcome, while preserving the motor decoder, visual task state, and reward delivery as far as possible.

**Grossbergian prediction.** Category-specific role information should be present in the learned feedback before final outcome, and source suppression should reduce the cell-specific apical signal and subsequent learning even when sensory error remains observable.

**Explicit cellular-error prediction.** A teaching vector computed elsewhere may remain during outcome/error despite removal of this expectation source. If the same source carries the error vector, both accounts predict impairment; temporal and content analysis is then essential.

**Distinguishing observation.** Role/context information in the afferent before outcome, followed by loss of residual and learning under phase-specific source suppression, supports A1/A5. An intact role-specific residual and learning after complete source suppression falsifies this bridge.

**Feasibility.** Medium: retrograde tracing, axon imaging, pathway optogenetics, and the existing BCI/dendritic imaging framework.

**Confounds.** The source may also carry sensory state, arousal, or motor intention; broad suppression may change behavior and hence feedback. Use matched sensory playback and expression-versus-learning phases.

## 2. Within-cell context reversal and hidden-role remapping

**Manipulation.** Give the same identified neurons two observable contexts with opposite decoder roles, or reverse roles after stable learning. Track higher-source axons, apical residual, soma, and learning continuously.

**Grossbergian prediction.** Different context categories should select approximately opponent expectations for the same cells. A learned expectation signal may appear during pre-action control; after remap, old T should transiently be maladaptive, then search/new-category selection should precede or accompany new cell-specific plasticity.

**Explicit cellular-error prediction.** Once the new causal derivative can be estimated from feedback, the cellular teaching sign should reverse with error/outcome; it need not wait for a stable category-specific expectation.

**Distinguishing observation.** Category/source activity and pre-outcome apical sign reverse before later soma change, with a search-like transition, favors representation feedback. Immediate post-error sign reversal without corresponding reorganization of higher expectation weakens A1/A2.

**Feasibility.** Medium–high using the existing BCI contingency, but greater behavioral burden.

**Confounds.** Reversal surprise, extinction, context salience, and asymmetric exploration can mimic search. Counterbalance mappings and include stable-context controls.

## 3. Separate excitatory feedback from L1 inhibitory surround

**Manipulation.** Record or infer distal excitatory and inhibitory currents while independently perturbing the higher feedback axons and NDNF+ cells. Preserve average somatic firing with calibrated compensation where possible.

**Grossbergian prediction.** The role-opponent pattern should be decomposable into a learned center and inhibitory competitor/surround component; disrupting the surround should reduce role opposition or match selectivity, while source disruption should remove the patterned center.

**Explicit cellular-error prediction.** A cell-indexed apical error could be carried directly by excitation, inhibition, or both; it does not specifically require an ART-like center/surround geometry.

**Distinguishing observation.** A topographically/category-organized opponent current that depends on both components and predicts local timing/plasticity supports A3. A fully role-specific signal with no candidate surround, or a surround too broad to respect intermingled roles, falsifies that bridge.

**Feasibility.** Low–medium in vivo; voltage indicators, targeted electrophysiology, and cell-type/pathway manipulation are demanding.

**Confounds.** NDNF manipulation changes dendritic integration and soma broadly; compensation can introduce artificial network states.

## 4. Match/resonance versus scalar-reward dissociation

**Manipulation.** Orthogonally manipulate bottom-up/top-down match and reward. Include matched-but-unrewarded, mismatched-but-rewarded, matched-and-rewarded, and neither conditions while measuring timing, ΔW proxies, and later response.

**Grossbergian prediction.** Match should be required for category-specific local timing/plasticity; reward should reinforce/maintain the eligible representation but should not rescue a mismatched local circuit by itself.

**Vector/three-factor predictions.** Explicit cellular error or reward-gated eligibility may drive updates under mismatch if the relevant cell-indexed error or eligibility remains available.

**Distinguishing observation.** Rewarded mismatch failing to produce role-specific plasticity while unrewarded match preserves only transient/gated local change supports the separation between resonance and reinforcement. Reward alone producing the full chain makes SMART-specific match unnecessary.

**Feasibility.** Medium with sensory/task replay or controlled perturbation of expected feedback.

**Confounds.** “Mismatch” must be independently validated physiologically; reward omission changes arousal and motivation.

## 5. Timing-law test within a fixed representation

**Manipulation.** Hold the selected H and its T fixed, then shift top-down arrival relative to feedforward and somatic spikes without changing reward or causal role.

**Grossbergian prediction.** Local ΔW should follow the SMART timing/voltage window; role-correct change should disappear or reverse when timing is moved out of the window.

**Explicit cellular-error prediction.** A robust cell-indexed error can remain informative despite this timing shift, although its biological plasticity implementation may still require coincidence.

**Distinguishing observation.** A preregistered timing curve matching the local SMART rule and mediating future response supports A4. Stable role-correct updates independent of the candidate timing law falsify that local transform.

**Feasibility.** Medium ex vivo; difficult but possible with closed-loop optogenetic timing in vivo.

**Confounds.** Timing perturbation changes excitability and calcium directly; control for spike count and voltage integral.

## 6. Calibrated voltage/current-to-calcium forward model

**Manipulation.** Simultaneously record dendritic voltage/calcium, soma, and identified excitatory/inhibitory inputs; fit the forward model on independent trials and predict the held-out Francioni residual.

**Grossbergian prediction.** If the proposed local state is real, its role information should survive through a calibrated optical model in the same temporal windows.

**Cellular-error prediction.** A genuine dendritic teaching signal should likewise survive; the source/timing/content still discriminate accounts.

**Distinguishing observation.** This does not choose theories alone. It falsifies A6 if the proposed latent Grossbergian signal cannot generate the observed residual, or rescues the measurement arrow if it can.

**Feasibility.** Low in vivo, medium in a staged ex vivo/computational calibration.

**Confounds.** Indicator expression, sampling, event detection, and regression transport across preparations.

## Priority order

1. Projection-specific source perturbation (kills A1/A5 directly).
2. Context reversal/remapping (tests A2 and representational timing).
3. Excitation-versus-NDNF surround dissection (tests A3/A5).
4. Match-by-reward dissociation (tests Grossberg specificity).
5. Fixed-H timing law (tests A4).
6. Measurement calibration (necessary for model–experiment comparison, less theory-specific).
