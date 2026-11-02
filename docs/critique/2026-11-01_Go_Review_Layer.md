# Critique Ledger: Go Review-Layer Model Allocation

- Goal: choose the claim-critic and referee models in the `go` profile to maximize review quality without exceeding any monthly OpenCode Go allowance
- Started: 2026-11-01
- Branch: main
- Lens set: cost, correctness, reliability, product

## Findings

- C-20261101-01 | 2026-11-01 | correctness | high | high | addressed | A's 107% breach rests on 1/14 claim-critic sessions hold 4.68M of 7.21M cached; without it A is 79% of $15 | `sqlite3 ... 'claim-critic%'` gives ds 4.68M, ds+glm 2.53M
  - rebuttal | addressed | 4.678M is one row, next is 0.514M; 1 of 14 sessions can blow the cap, which argues against A | outlier confirmed, not an aggregate
- C-20261101-02 | 2026-11-01 | cost | high | high | addressed | At 2x last month's burn the glm-5.3 leg hits $13.93, 92.8% of $15, leaving 0.7% slack | `2x: 13.93/15; worst-7d 5.55/7.50; worst-5h 2.72/3.00`
  - rebuttal | addressed | operator decision, see addressed record | operator decision 2026-11-01: accept 2x at 92.8%; ship C bundled with the blocking usage gate
  - rebuttal | escalated | recomputed 1x $6.96, 1.5x $10.45, 2x $13.93 (92.8%); 5h at 2x is 91%, not the pack's 60% | risk is real and larger than first stated
- C-20261101-03 | 2026-11-01 | cost | high | high | addressed | C's slack against a flailing flash critic is 59x monthly but 2.15x once critic retries drive referee rounds on one $15 pool | `breach 2.15x monthly, 2.21x on the $3/5h cap`
  - rebuttal | addressed | asymmetry stands: 58.9x flash slack versus 2.15x on the shared pool | coupling is the binding constraint
- C-20261101-04 | 2026-11-01 | correctness | high | high | addressed | C contradicts the profile's own text, which scopes flash to low-turn capability seats and pins glm-5.3 to both review seats | `models.yaml:127-134` vs `models.yaml:161`
  - rebuttal | addressed | text confirmed at `models.yaml:132-134`; ledger line pointer was off, doctrine conflict is real | doctrine text must change with the choice
- C-20261101-05 | 2026-11-01 | product | high | medium | rejected | Alternative E keeps the flagship on the critic and referee on flash: $9.02/mo (60%) plus $0.78/mo, legal at 1x | `E 1x 60% of pool; 2x $18.05 = 120%`
  - rebuttal | rejected | E is legal at 1x but breaches at 2x ($18.05, 120%) and at 5h ($4.12, 137%) | fails the never-exceed goal
- C-20261101-06 | 2026-11-01 | reliability | high | high | rejected | A drained pool has no detection rule: the chief re-tasks a blocked referee once then absorbs the gate silently | `grep -rn "drained pool"` hits only `models.yaml:146-147`
  - rebuttal | rejected | a fallback rule does exist at `models.yaml:146-147`; the detection gap is real and carried by C-07 | fallback documented, detection missing
- C-20261101-07 | 2026-11-01 | reliability | high | high | addressed | No usage or allowance check runs in the repo gate; drain shows only when requests are refused | `scripts/check.sh:14-37`; `scripts/cost-report.py` manual only
  - rebuttal | addressed | operator decision, see addressed record | operator decision 2026-11-01: blocking from day one via `scripts/check_usage.py` in `scripts/check.sh:24`
  - rebuttal | escalated | six gate checks confirmed, none touches usage | needs a human decision to add one
- C-20261101-08 | 2026-11-01 | cost | medium | high | addressed | Headroom is burst-concentrated: the worst 7-day window holds 87% of sample referee cost, so one sprint uses 37% of the weekly cap | `worst 7d $2.77 = 86%; 2.77/7.50 = 37%`
  - rebuttal | addressed | ledger's 92.8% weekly figure was wrong; 37% at 1x and 74% at 2x | corrected, still binding under stress
- C-20261101-09 | 2026-11-01 | cost | medium | medium | rejected | Peak billing is untested for GLM seats and could push the pool to 139% of $15 | `pack.md:20` applies peak doubling to deepseek only
  - rebuttal | rejected | no GLM peak rate is documented; the doubling is a DeepSeek-only structure | inapplicable
- C-20261101-10 | 2026-11-01 | correctness | medium | high | addressed | The rulebook says GLM 5.3 holds claim-critic and wordsmith, but go maps wordsmith to flash; C widens the gap | `docs/rulebook/model-profiles.md:8` vs `models.yaml:160`
  - rebuttal | addressed | wordsmith already on flash in go, so the contradiction pre-exists and C widens it | fix with the doctrine text
- C-20261101-11 | 2026-11-01 | correctness | medium | medium | addressed | The claim-critic contract pins reasoningEffort max, which argues against a flash tier for that seat | `agents/generated/claim-critic-go.md:7,17,28`
  - rebuttal | addressed | operator decision, see addressed record | operator decision 2026-11-01: keep the flash critic; revisit against its measured miss rate
  - rebuttal | escalated | contract confirmed: max effort and subtle-defect hunting | capability trade needs a human call
- C-20261101-12 | 2026-11-01 | correctness | medium | medium | addressed | Both review seats sit on one Z.ai family, so a shared GLM failure mode passes both gates | `models.yaml:158-159`; independence scoped to DeepSeek at `:95-97`
  - rebuttal | addressed | confirmed; independence is only vendor-level versus DeepSeek | accepted pre-existing limit
- C-20261101-13 | 2026-11-01 | reliability | medium | high | addressed | cost-report groups by agent with no model column and no sliding window, so per-pool burn is invisible | `scripts/cost-report.py:12-24`
  - rebuttal | addressed | operator decision, see addressed record | operator decision 2026-11-01: model column and `--window` folded into the same diff
  - rebuttal | escalated | confirmed: GROUP BY agent only, `--since` is a day filter | needs a human decision
- C-20261101-14 | 2026-11-01 | correctness | low | high | addressed | Pack count drift: redteamer showed 162 in the pack but the DB held 166 at the same moment | `sqlite3 ... COUNT(*)` returns 166; sessions landed between 10:52 and 10:58
  - rebuttal | addressed | both snapshots were correct when written; no suffix was dropped | measurement drift, not error
- C-20261101-15 | 2026-11-01 | product | low | medium | addressed | The review-share argument uses an unreproducible denominator: chief $65.53 of $72 over 988 sessions | measured chief $7.11 over 130 sessions; `models.yaml:120-124`
  - rebuttal | addressed | comment denominator is foreign to this dataset and must be corrected | text fix
