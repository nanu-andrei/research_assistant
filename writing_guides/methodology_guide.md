# Academic Writing Guide: Methodology Chapter (IEEE Standard)

## Objective
The Methodology chapter defines the mathematical foundation, system model, signal processing pipeline, and algorithmic steps of the proposed system. It must be sufficiently detailed for reproducibility.

## Industry Standard Structure
1. **System Overview & Formal Preliminaries:**
   - Define physical parameters: Transmit/Receive antennas ($N_{tx}, N_{rx}$), OFDM subcarriers ($S$), and time packets ($T$).
   - Mathematical formulation of Channel State Information (CSI) matrix $\mathbf{H} \in \mathbb{C}^{N_{tx} \times N_{rx} \times S \times T}$.
   - Channel Impulse Response (CIR): $h(\tau) = \sum_{l=1}^L \alpha_l e^{j\phi_l} \delta(\tau - \tau_l)$.
2. **Phase Sanitization & Signal Denoising Pipeline:**
   - Phase unwrapping and linear regression calibration to eliminate carrier frequency offset (CFO) and sampling frequency offset (SFO).
   - High-pass Doppler filtering to separate static environmental multipath from dynamic human movement reflections.
3. **Core Architectural Engine:**
   - Feature extractor backbone (e.g. Temporal Convolutional Networks, Self-Attention / Transformer, or BiLSTM).
   - Loss function definition with explicit equations: $\mathcal{L}_{total} = \mathcal{L}_{task} + \lambda \mathcal{L}_{contrastive}$.
4. **Algorithmic Specification:**
   - Formal pseudocode or structured pipeline walkthrough.

## Weighting Rules
- Directly build upon the physical signal formulation of the #1 ranked methodology from Phase 2 (e.g. `SenseFi`'s CSI modeling).
- Formal LaTeX equations (`\begin{equation} ... \end{equation}`) must be utilized.
