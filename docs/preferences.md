# Preference Formation (Stage A)

A7DO does not use reward.  
Preference is not "liking". Preference is structural gravity: a bias toward frame-structures that reduce informational resistance.

## Core Doctrine

- No time: only frames.
- A Frame begins when information enters and ends when information settles/collapses.
- Preference is computed only at frame close.
- Preference does not force actions. It only measures structural ease.

## Definitions

A Frame F contains fragments {f_i} with fragment kinds k_i.

### Observed kind distribution (per frame)
Let K be the set of fragment kinds observed.
p_F(k) = (1/n) * sum_i 1[k_i = k]

### Normalized entropy (structure-only)
H(p_F) = - sum_k p_F(k) log(p_F(k) + δ)
H_N = H(p_F) / log(|K|)

### Coherence and Fragmentation
C_F = 1 - H_N
Φ_F = H_N

Coherence increases as a single structure dominates.
Fragmentation increases as structures diversify.

### Expectation model (Identity-owned)
Identity maintains an expectation distribution q(k) (probabilities over kinds).

Update after each frame close:
q_new(k) = (1 - β) q(k) + β p_F(k)

### Prediction error (L1)
ε_F = ||p_F - q||_1 = sum_k |p_F(k) - q(k)|

ε_F is a measure of mismatch between expected structure and observed structure.

## Preference Energy (per context key)

A context key x is a stable address for preference tracking, e.g.:
- region only: "top", "left", ...
- signature only: "sig:contact|contact"
- combined: "top::sig:contact|contact"

We maintain a preference value P(x) ∈ [-1, 1].

### Update components

- Coherence centered to [-1, 1]:
c_term = 2*C_F - 1

- Understanding gain (non-reward)
ΔU_F(x) = max(0, ε_prev(x) - ε_F)

- Embodiment load (optional)
L_F ∈ [0,1] from thermal/pain overload fragments (if present)

### Preference update (bounded, conservative)

ΔP_F(x) =
  α_C * c_term
+ α_U * ΔU_F(x)
- α_E * ε_F
- α_L * L_F

P_new(x) = clip( (1 - λ) P(x) + η ΔP_F(x), -1, 1 )

Notes:
- No reward term exists.
- Preference rises only when structure is coherent and mismatch reduces.
- Preference falls when mismatch remains high or embodiment load grows.

## What Stage A Produces

- A preference table over contexts x
- A trend of ε_F, C_F, Φ_F
- No action selection changes (yet)

## Expected behavior

If the same context repeats:
- ε_F tends to fall
- C_F tends to rise
- P(x) rises gradually

If contexts are mixed:
- ε_F stays moderate/high
- C_F stays low
- P(x) stays near 0
