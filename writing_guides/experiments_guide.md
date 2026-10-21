# Academic Writing Guide: Experimental Evaluation Chapter (IEEE Standard)

## Objective
The Experimental Evaluation chapter empirically proves the claims made in the Introduction and validates the mathematical models in the Methodology.

## Industry Standard Structure
1. **Experimental Setup & Testbed:**
   - Physical room geometries (e.g., Line-of-Sight vs. Non-Line-of-Sight rooms).
   - Hardware platforms (e.g., commodity Intel 5300 NIC / Atheros CSI tools, 802.11n routers).
   - Dataset statistics (e.g., SenseFi benchmark, Widar 3.0, sample counts, train/val/test splits).
2. **Comparative Baselines:**
   - State-of-the-art architectures compared under identical testbed splits (ResNet, CNN-GRU, Vision Transformers, Handcrafted SVM).
3. **Evaluation Metrics:**
   - Classification accuracy, Macro F1-score, Cross-domain transfer degradation, and latency (ms).
4. **Performance Analysis & Key Findings:**
   - Quantitative superiority over baselines.
   - Robustness to transmitter-receiver distance and room geometry variation.
5. **Ablation Studies:**
   - Isolating the individual contribution of each component (e.g. without contrastive pretraining, without Doppler filter).

## Weighting Rules
- Grounded directly in the benchmark protocols of the top-ranked experiment chapters from Phase 2.
