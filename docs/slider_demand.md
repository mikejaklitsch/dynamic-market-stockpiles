# Slider Demand

Each country's court, diplomatic, stability, and cultural spending is converted monthly into temporary goods demand on markets. Phase 1 (per country) computes gold and accumulates it into market location maps; Phase 2 (global) converts the maps into demands. Execution order and rule gating are in [technical_summary.md](../technical_summary.md).

## Shared Machinery

**Economic base:** every formula below uses `country_economical_base`, written as `eco_base`.

**Efficiency divisor:** each slider's cost efficiency modifier divides gold as `max(1 + efficiency, 0.5)`; the engine clamps the divisor at 0.5 (max 2x cost).

**Efficiency decay:** heavy spending generates diminishing demand per slider (spoilage, corruption, inefficiency). Each doubling of raw gold past a baseline of 250 costs a multiplicative 25% efficiency loss: `gold *= (250 / max(gold, 250)) ^ 0.415`, where 0.415 = log(0.75)/log(0.5). The decay is applied after the raw gold formula and before distribution.

**Distribution:** gold splits across the country's cached proximity sources proportionally by weight. Sources are owned locations with `modifier:local_proximity_source > 0`; the weight is that modifier's value. Countries with no sources fall back to their capital with weight 1. Each source's share = `total_gold * (source_weight / total_weight)`.

**Accumulation:** each source's share is added into a per-slider gold map (`dmsd_court_map`, `dmsd_diplo_map`, `dmsd_stab_map`, `dmsd_cult_map`) on the source's market center location, keyed by demand type. All countries routing through the same market accumulate additively into the same map. Phase 2 consumes and clears these maps every month.

**Tooltip subsystem:** the Phase 1 events and accumulators also maintain display-only state (`dmsd_prox_*_dict/gold/scale` maps for the per-source goods breakdowns, `dmsd_disp_court_rel_dict` for the country-level religion basket, `dmsd_cult_raw_gold`). This state feeds GUI tooltips and has no effect on gameplay logic; the per-source scale in those maps is informational, the applied scale is computed in Phase 2 from aggregated gold.

## Court (Event .1)

**Gold formula:** `slider * 0.1 * eco_base / max(1 + court_spending_efficiency, 0.5)`

The `court_maintenance` trigger gives the raw slider position (0-1) but does not account for reduced spending when government power sits at its cap of 100. We infer the effective slider from month-over-month government power deltas.

The delta comes from a snapshot: each monthly run ends by storing current government power in `dmsd_last_gov_power` on the country. The next run reads that stored value as last month's level, so current power minus the snapshot is exactly one month of change; stripping the non-slider contribution from that change leaves what the slider produced.

**Non-slider contribution** depends on government type:

| `uses_government_power` | Modifier read                  |
|----------------------------------------------------------|
| legitimacy              | `monthly_legitimacy`           |
| republican_tradition    | `monthly_republican_tradition` |
| devotion                | `monthly_devotion`             |
| horde_unity             | `monthly_horde_unity`          |
| tribal_cohesion         | `monthly_tribal_cohesion`      |

**Inference cases**, one applies each month:

- **Normal growth** (power below the cap): the delta method applies. `slider_raw = government_power - last_snapshot - non_slider_contribution`, and `dmsd_court_slider = slider_raw / 2`. Since +2/month is the max output a cost of court slider can produce on its own, a `slider_raw` outside 0 to +2 is physically impossible for the slider, so it means outside interference (event-driven spikes/spends); the month is thrown out and `dmsd_court_slider` keeps last month's value.
- **At the cap**: a nation that has maxed out government power spends less, because the slider only needs to maintain equilibrium against drain. To handle that, the effective slider is set to the drain it is offsetting: `dmsd_court_slider = -non_slider_contribution / 2` (negated because drain is a negative contribution). The result is floored at 0 because a nation with no drain spends nothing, and ceilinged at `court_maintenance` because the slider never works harder than its set position; a slider at zero pays nothing no matter the drain.
- **First month** (no snapshot yet): the raw position is used, `dmsd_court_slider = court_maintenance`.

Every month ends by recording the snapshot: `dmsd_last_gov_power = government_power`. The snapshot is written after the delta is consumed, never before, or every delta reads as zero.

**Basket routing:** court is the only slider that splits gold between two baskets. Each proximity source's share goes 50/50 to the source's subcontinent basket and the country's religion-group basket. Every subcontinent is registered (some map to the generic base basket, e.g. southern Africa), so the regional side always exists; when the country's religion group has no registered basket, the subcontinent basket gets 100%.

## Diplomatic (Event .2)

**Gold formula:** `diplomatic_maintenance * cost * (1 + cost) * eco_base / max(1 + diplomatic_upkeep_efficiency, 0.5)`

Where `cost` = `modifier:diplomatic_spending_cost` (base 0.1). Vanilla applies the cost modifier twice: once as the base rate, once as a `(1 + cost)` multiplier. The `diplomatic_maintenance` trigger gives the slider position directly; no inference needed.

## Stability (Event .3)

**Gold formula:** `slider * 0.1 * eco_base / max(1 + stability_cost_efficiency, 0.5)`

The engine exposes no usable stability spending trigger, so the slider is inferred from stability deltas, same snapshot pattern as cost of court: each run ends by storing current stability in `dmsd_last_stability`, and the next run diffs against it.

**Non-slider sources:** these are the `stability_investment` modifier plus natural decay. Decay pulls stability toward zero at `-stability * stability_decay`; at negative stability this contributes positive growth that must still be removed to isolate the slider.

**Inference cases**, one applies each month:

- **Normal growth** (stability below the cap): the delta method applies. `decay = -last_snapshot * stability_decay` (last month's stability, since decay acted on that value), then `slider_raw = stability - last_snapshot - stability_investment - decay`, and `dmsd_stab_slider = slider_raw / 0.5` since +0.5/month is max output. The plausibility window is 0 to `0.5 + stability_investment`; investment is additive, so it raises what a legitimate month can show. A value outside the window means outside interference; the month is thrown out and `dmsd_stab_slider` keeps last month's value.
- **At the cap**: this is the same equilibrium case as court; a nation at max stability only spends enough to hold against drain. Here the drain has two parts, decay plus investment: `drain = stability_investment + (-stability * stability_decay)` using current stability, and `dmsd_stab_slider = -drain / 0.5`, clamped 0-1.
- **First month** (no snapshot yet): unlike court, there is no fallback; `dmsd_stab_slider` stays unset and the event computes zero gold until the second month.

Every month ends by recording the snapshot: `dmsd_last_stability = stability`. Same rule as court: snapshot after the delta, never before.

## Cultural (Event .5)

Cultural spending is fundamentally different: cost comes from artist salaries, not a slider-times-eco_base formula.

**Gold formula:** `0.025 * cultural_maintenance * tax_base * N^2 / 12 * (1 + artist_salary_modifier + avg_char_modifier)`

Where:
- `0.025` = the engine's `ARTIST_SALARY_BASE_FACTOR` define
- `cultural_maintenance` = slider position (0-1)
- `tax_base` = `country_tax_base`
- `N` = number of employed artists; each artist's salary scales with `tax_base * N`, and there are N of them, hence N squared
- `/ 12` converts the annual salary to monthly
- `avg_char_modifier` = sum of per-character `artist_salary_modifier_on_character` across all artists, divided by `max(N, 1)`

The pre-decay gold is stored as `var:dmsd_cult_raw_gold` on the country because the tooltip cannot recompute it (requires `every_artist` iteration).

## Phase 2: Application

After all countries have accumulated, every market center:

1. Removes last month's demands. Each slider keeps a `dmsd_*_applied` variable list of the demand types it actually applied; removal iterates that list, then clears it.
2. For each key in the slider's gold map: `basket_price = sum(weight * market_price)` over the goods in the demand type's weight container, `scale = gold / basket_price`. Entries with gold below 0.01 or basket price of zero are skipped.
3. Applies the demand with unlimited duration: demands persist until explicitly removed, which is what makes the applied-list bookkeeping necessary.
4. Clears the gold map.

**Swap system:** the engine cannot update an existing temporary demand's scale in place, and a same-month remove and re-add of one type does not take. Each demand type therefore has a reg1/reg2 twin (`dmsd_demand_swap` maps 1 to 2), and a global `dmsd_swap` flag toggles monthly: one month applies the reg1 types and removes reg2, the next month reverses. Both twins share the same weight container.

**Orphan cleanup:** market center locations are registered in a global `dmsd_active_locations` list during accumulation and Phase 2. After applying, any listed location that is no longer a market center has its demands and maps stripped, and the list is cleared for next month.

## Demand Types and Baskets

Demand types and their baskets are generated by `tools/gen_dmsd_demands.py`. Each slider has regional variants keyed by subcontinent; every subcontinent is registered, with a base basket as the value for those without a specific variant. Court additionally has religion-group variants.

**Weights are baked at generation time** from a static price table in the generator: `weight = (REF_PRICE / base_price) * importance`, with `REF_PRICE = 3.0`. Expensive goods get lower weights and cheap goods higher, producing roughly equal gold allocation per good within a basket. Runtime market prices enter only through the basket price computation above.

**Weight containers:** each basket's goods weights are stored in a `dmsd_weights` variable map on a location allocated from a pool at init: the first 50 locations returned by `every_location_in_the_world`. `dmsd_demand_dict` maps each demand type to its container location; reg1/reg2 twins share one container.

**Registry maps** (global, built at init):
- `dmsd_court_reg1`, `dmsd_diplo_reg1`, `dmsd_stab_reg1`, `dmsd_cult_reg1`: subcontinent (or religion group, court only) to demand type
- `dmsd_demand_swap`: reg1 demand type to its reg2 counterpart
- `dmsd_demand_dict`: demand type to weight container location
