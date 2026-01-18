Math & Equations
Frame-Based Dynamics Under Sandy’s Law
0. Purpose

This document defines the formal mathematics underlying A7DO and Sandy’s Law.

It replaces:

time-based dynamics

reward optimization

goal-driven control

with:

frame-based information resolution

structural coherence

embodiment-driven prediction error reduction

All equations are implementation-agnostic and doctrine-locked.

1. Fundamental Objects
1.1 Event Stream

Events are strictly ordered by sequence, not time.

Let:

𝑒
𝑘
e
k
	​

 be the 
𝑘
k-th event

𝑘
∈
𝑁
k∈N

Each event has a type:

𝑡
(
𝑒
𝑘
)
∈
{
observation
,
action
,
outcome
,
internal
,
system
}
t(e
k
	​

)∈{observation,action,outcome,internal,system}

There is no timestamp.

1.2 Frame

A frame is a contiguous block of events:

𝐹
𝑖
=
{
𝑒
𝑘
∣
𝑘
𝑖
𝑠
𝑡
𝑎
𝑟
𝑡
≤
𝑘
≤
𝑘
𝑖
𝑒
𝑛
𝑑
}
F
i
	​

={e
k
	​

∣k
i
start
	​

≤k≤k
i
end
	​

}

Frame size:

∣
𝐹
𝑖
∣
=
𝑘
𝑖
𝑒
𝑛
𝑑
−
𝑘
𝑖
𝑠
𝑡
𝑎
𝑟
𝑡
+
1
∣F
i
	​

∣=k
i
end
	​

−k
i
start
	​

+1

This replaces duration.

2. Information Flux & Frame Closure
2.1 Event Information Weight

Each event contributes bounded information:

𝑤
(
𝑒
𝑘
)
=
𝑤
𝑡
𝑦
𝑝
𝑒
(
𝑡
(
𝑒
𝑘
)
)
⋅
(
1
+
∥
Δ
𝑝
(
𝑒
𝑘
)
∥
)
w(e
k
	​

)=w
type
	​

(t(e
k
	​

))⋅(1+∥Δp(e
k
	​

)∥)

Where:

𝑤
𝑡
𝑦
𝑝
𝑒
w
type
	​

 is a fixed per-type weight

Δ
𝑝
(
𝑒
𝑘
)
∈
[
0
,
1
]
Δp(e
k
	​

)∈[0,1] is normalized payload change magnitude

2.2 Flux Over Recent Events

For the last 
𝑚
m events 
𝑆
𝑚
⊂
𝐹
𝑖
S
m
	​

⊂F
i
	​

:

Φ
(
𝑆
𝑚
)
=
∑
𝑒
𝑘
∈
𝑆
𝑚
𝑤
(
𝑒
𝑘
)
Φ(S
m
	​

)=
e
k
	​

∈S
m
	​

∑
	​

w(e
k
	​

)
2.3 Frame Closure Conditions

A frame closes when any condition is met:

Silence

Φ
(
𝑆
𝑚
)
≤
𝜖
Φ(S
m
	​

)≤ϵ

Resolution

𝐸
(
𝐹
𝑖
)
≤
𝜖
𝐸
E(F
i
	​

)≤ϵ
E
	​


Fragmentation

𝐹
(
𝐹
𝑖
)
≥
𝜃
𝐹
F(F
i
	​

)≥θ
F
	​

3. Accounting Vector (Accountant Entry)

Each closed frame produces a summary:

𝐴
𝑖
=
[
𝑁
𝑜
𝑏
𝑠
,
𝑁
𝑎
𝑐
𝑡
,
𝑁
𝑜
𝑢
𝑡
𝑐
,
𝑁
𝑖
𝑛
𝑡
,
𝑁
𝑠
𝑦
𝑠
,
𝜌
𝑓
𝑎
𝑖
𝑙
,
Φ
𝑡
𝑜
𝑡
,
𝐶
,
𝐸
,
𝑆
,
𝐹
]
A
i
	​

=[N
obs
	​

,N
act
	​

,N
outc
	​

,N
int
	​

,N
sys
	​

,ρ
fail
	​

,Φ
tot
	​

,C,E,S,F]

Where:

𝑁
𝑥
N
x
	​

: event counts

Failure rate:

𝜌
𝑓
𝑎
𝑖
𝑙
=
𝑁
𝑓
𝑎
𝑖
𝑙
max
⁡
(
1
,
𝑁
𝑓
𝑎
𝑖
𝑙
+
𝑁
𝑠
𝑢
𝑐
𝑐
)
ρ
fail
	​

=
max(1,N
fail
	​

+N
succ
	​

)
N
fail
	​

	​


Total flux:

Φ
𝑡
𝑜
𝑡
(
𝐹
𝑖
)
=
∑
𝑒
𝑘
∈
𝐹
𝑖
𝑤
(
𝑒
𝑘
)
Φ
tot
	​

(F
i
	​

)=
e
k
	​

∈F
i
	​

∑
	​

w(e
k
	​

)

Only this vector propagates upward.

4. Prediction Error (Structural)

Prediction error is physical mismatch, not belief error.

4.1 Expectation Vector

From embodiment:

𝑥
^
=
ExpectationGate
(
Ledger
,
context
)
x
^
=ExpectationGate(Ledger,context)
4.2 Observed Outcome

Observed outcome vector 
𝑥
x is extracted from frame outcomes.

4.3 Error Metric
𝐸
(
𝐹
𝑖
)
=
∥
𝑥
^
−
𝑥
∥
1
or
∥
𝑥
^
−
𝑥
∥
2
E(F
i
	​

)=∥
x
^
−x∥
1
	​

or∥
x
^
−x∥
2
	​


If no expectation exists:

𝐸
(
𝐹
𝑖
)
=
𝐸
0
⋅
Novelty
(
𝐹
𝑖
)
E(F
i
	​

)=E
0
	​

⋅Novelty(F
i
	​

)
5. Coherence

Coherence measures settling vs instability.

𝐶
(
𝐹
𝑖
)
=
𝜎
 ⁣
(
𝛼
0
+
𝛼
1
(
1
−
𝐸
~
)
+
𝛼
2
𝑅
~
−
𝛼
3
𝐹
~
−
𝛼
4
𝜌
~
𝑓
𝑎
𝑖
𝑙
)
C(F
i
	​

)=σ(α
0
	​

+α
1
	​

(1−
E
~
)+α
2
	​

R
~
−α
3
	​

F
~
−α
4
	​

ρ
~
	​

fail
	​

)

Where:

𝜎
(
𝑧
)
=
1
1
+
𝑒
−
𝑧
σ(z)=
1+e
−z
1
	​


𝐸
~
E
~
: normalized error

𝑅
~
R
~
: resolution indicator

𝐹
~
F
~
: normalized fragmentation

Coherence is diagnostic only.

6. Fragmentation Index

Fragmentation quantifies competing concurrent activity.

Let region tag 
𝑟
(
𝑒
𝑘
)
∈
{
1
,
…
,
𝑀
}
r(e
k
	​

)∈{1,…,M}.

Region distribution:

𝑝
𝑗
=
∣
{
𝑒
𝑘
∈
𝐹
𝑖
:
𝑟
(
𝑒
𝑘
)
=
𝑗
}
∣
∣
𝐹
𝑖
∣
p
j
	​

=
∣F
i
	​

∣
∣{e
k
	​

∈F
i
	​

:r(e
k
	​

)=j}∣
	​


Fragmentation:

𝐹
(
𝐹
𝑖
)
=
−
∑
𝑗
𝑝
𝑗
log
⁡
𝑝
𝑗
F(F
i
	​

)=−
j
∑
	​

p
j
	​

logp
j
	​


Normalized:

𝐹
~
=
𝐹
log
⁡
𝑀
F
~
=
logM
F
	​

7. Memory Stability

For cluster 
𝐾
K with vectors 
{
𝐴
𝑖
}
{A
i
	​

}:

Centroid
𝜇
𝐾
=
1
𝑛
∑
𝑖
=
1
𝑛
𝐴
𝑖
μ
K
	​

=
n
1
	​

i=1
∑
n
	​

A
i
	​

Variance
𝑉
𝐾
=
1
𝑛
∑
𝑖
=
1
𝑛
∥
𝐴
𝑖
−
𝜇
𝐾
∥
2
2
V
K
	​

=
n
1
	​

i=1
∑
n
	​

∥A
i
	​

−μ
K
	​

∥
2
2
	​

Stability
Stab
(
𝐾
)
=
𝜎
 ⁣
(
𝛽
1
log
⁡
(
1
+
𝑆
𝐾
)
−
𝛽
2
𝑉
~
𝐾
)
Stab(K)=σ(β
1
	​

log(1+S
K
	​

)−β
2
	​

V
~
K
	​

)

Memory candidates require:

Stab
(
𝐾
)
≥
𝜃
𝑠
𝑡
𝑎
𝑏
,
𝑆
𝐾
≥
𝑆
𝑚
𝑖
𝑛
Stab(K)≥θ
stab
	​

,S
K
	​

≥S
min
	​

8. Embodiment Admission

Embodiment requires local, stable, non-contradictory patterns.

Locality
Loc
(
𝐾
)
=
max
⁡
𝑗
𝑝
𝑗
Loc(K)=
j
max
	​

p
j
	​

Contradiction
Contra
(
𝐾
,
𝐿
)
=
max
⁡
ℓ
∈
𝐿
1
[
conflict
(
𝐾
,
ℓ
)
]
Contra(K,L)=
ℓ∈L
max
	​

1[conflict(K,ℓ)]
Admission Rule
Admit
(
𝐾
)
=
1
[
Stab
(
𝐾
)
≥
𝜃
𝑠
𝑡
𝑎
𝑏
∧
Loc
(
𝐾
)
≥
𝜃
𝑙
𝑜
𝑐
∧
Contra
(
𝐾
,
𝐿
)
=
0
]
Admit(K)=1[Stab(K)≥θ
stab
	​

∧Loc(K)≥θ
loc
	​

∧Contra(K,L)=0]
9. Regulatory Signals (Non-Reward)

All bounded to 
[
0
,
1
]
[0,1].

Enjoyment (dopamine-like)
𝐷
𝑖
+
1
=
clip
(
𝐷
𝑖
+
𝜂
𝐷
(
𝐶
−
0.5
)
𝑁
~
)
D
i+1
	​

=clip(D
i
	​

+η
D
	​

(C−0.5)
N
~
)
Settling (serotonin-like)
𝑆
𝑖
+
1
=
clip
(
𝑆
𝑖
+
𝜂
𝑆
(
1
−
𝐸
~
)
−
𝜂
𝑆
′
𝐹
~
)
S
i+1
	​

=clip(S
i
	​

+η
S
	​

(1−
E
~
)−η
S
′
	​

F
~
)
Load (cortisol-like)
𝐶
𝑖
+
1
=
clip
(
𝐶
𝑖
+
𝜂
𝐶
(
𝐸
~
+
Φ
~
𝑡
𝑜
𝑡
+
𝐹
~
)
−
𝜂
𝐶
′
𝑆
𝑖
+
1
)
C
i+1
	​

=clip(C
i
	​

+η
C
	​

(
E
~
+
Φ
~
tot
	​

+
F
~
)−η
C
′
	​

S
i+1
	​

)

These cannot be optimized.

10. Preference Formation (No Reward)

For context 
𝑞
q:

𝑃
(
𝑞
)
←
(
1
−
𝜆
)
𝑃
(
𝑞
)
+
𝜆
(
𝐶
−
𝐶
~
)
P(q)←(1−λ)P(q)+λ(C−
C
~
)

Preferences influence:

attention

exploration

They do not select actions directly.

11. Parameter Discipline

Minimal parameter set:

Frame: 
𝜖
,
𝜖
𝐸
,
𝜃
𝐹
,
𝑚
ϵ,ϵ
E
	​

,θ
F
	​

,m

Coherence: 
𝛼
0
.
.
𝛼
4
α
0
	​

..α
4
	​


Stability: 
𝛽
1
,
𝛽
2
,
𝜃
𝑠
𝑡
𝑎
𝑏
,
𝑆
𝑚
𝑖
𝑛
,
𝜃
𝑙
𝑜
𝑐
β
1
	​

,β
2
	​

,θ
stab
	​

,S
min
	​

,θ
loc
	​


Regulation: 
𝜂
𝐷
,
𝜂
𝑆
,
𝜂
𝐶
,
𝜂
𝑆
′
,
𝜂
𝐶
′
,
𝜆
η
D
	​

,η
S
	​

,η
C
	​

,η
S
′
	​

,η
C
′
	​

,λ

No additional parameters allowed without doctrine change.

12. Summary

Time is replaced by frames

Learning is resolution, not optimization

Stability emerges from constraint

Intelligence scales with coherence

Ethics emerge structurally

These equations describe a system that cannot collapse by design.