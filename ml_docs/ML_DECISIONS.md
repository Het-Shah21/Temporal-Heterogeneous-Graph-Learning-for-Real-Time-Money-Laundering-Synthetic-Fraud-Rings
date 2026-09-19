# ML Decision Log

*This document tracks all decisions made during the development of the ML portion.*

### Decision 001: Dataset Selection Strategy
- **What:** Decided to pivot from a purely custom naive simulator to adopting structures and data from the IBM AML (Anti-Money Laundering) Dataset.
- **Why:** Purely synthetic data fails to capture the realistic noise and hidden topological structures (cycles, layering, smurfing) present in actual financial crimes. The IBM AML dataset uses a multi-agent simulation that closely mimics real-world banking logic.
- **Where:** ml/data/ module.
- **When:** Week 1, Phase 1 (Project Initiation).

### Decision 002: Deterministic Heterogeneous Augmentation
- **What:** Decided to computationally augment the homogeneous IBM AML dataset using deterministic SHA-256 hashing based on Account_ID to generate static Device_IDs and IP_Addresses. Overwritten for fraud rings to share identical hardware.
- **Why:** Real banking logs hide IPs/Devices for privacy. Pure synthetic data lacks structure. This hybrid approach guarantees we have a strictly heterogeneous graph schema without losing the realistic transactional flow of the IBM dataset.
- **Where:** ml/data/hetero_builder.py
- **When:** Week 1, Phase 1 (Data Acquisition).
