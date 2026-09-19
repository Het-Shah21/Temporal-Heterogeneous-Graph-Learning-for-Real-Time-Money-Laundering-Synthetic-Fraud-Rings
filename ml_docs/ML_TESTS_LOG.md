# ML Tests & Validation Log

*This document tracks the self-validation, architectural scanning, and unit testing performed after every technical implementation or design choice. It ensures the system remains scalable, flawless, and free of underlying loopholes.*

*(Entries will be added here immediately after implementing a system and running our validation checks. Below is the strict template we will follow.)*

---
### [Template] Component / Design Name

**1. What was Tested?**
*The specific code, architecture, or technical choice being evaluated.*

**2. Test Methodology & Execution**
*How the test was run (e.g., memory profiling, scalability load test, logical unit test, architectural dry-run).*

**3. Verdict**
*[PASS / FAIL / NEEDS OPTIMIZATION]*

**4. Issues / Loopholes Found**
*Any open-end connections, scalability bottlenecks, or code errors detected during the test.*

**5. Resolution & Final Solution**
*Exactly how the error or loophole was resolved, and what the final implemented solution looks like.*

### System 1: Data Acquisition & Heterogeneous Graph Builder

**1. What was Tested?**
The hetero_builder.py script responsible for reading IBM AML CSVs, generating heterogeneous entities (Devices/IPs) deterministically, and mapping the correct fraud logic (shared device infrastructure for Is_Laundering=1 transactions).

**2. Test Methodology & Execution**
- Wrote a PyTest/Unittest suite (	est_hetero_builder.py).
- Simulated a 1000-row DataFrame containing a known fraud cycle (A2 -> A3).
- Validated that 
odes_account.csv and edges_uses.csv were correctly constructed.
- Ran architectural checks to ensure the deterministic hash function scales without OOM errors.

**3. Verdict**
PASS

**4. Issues / Loopholes Found**
No logical loopholes. However, ensuring it scales to 5 Million rows required ensuring Pandas operations are fully vectorized (iterating via .iterrows() on large subsets can be slow). 

**5. Resolution & Final Solution**
The current .iterrows() is only bounded to Is_Laundering=1 rows (which is typically <1% of the dataset), thus making it scalable without memory leaks. Final solution approved.
