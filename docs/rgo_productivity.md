# RGO Productivity

This system penalizes RGO output when market price falls below the good's base price, creating a price-responsive supply curve. Work is split across two pulses: Phase 1 triage runs per country in `monthly_country_pulse` through a load balancer, Phase 2 penalty computation runs once globally in `weather_monthly_pulse`. A full pass also runs at game start, and locations reindex on `on_raw_material_changed`. Execution order is in [technical_summary.md](../technical_summary.md).

**Penalty formula:** `penalty = relative_price * sensitivity * (1 + existing_output_modifiers)`

Where `relative_price` is the vanilla location trigger `relative_raw_material_price` (price relative to base, negative below base) and `sensitivity` = 1.0.

`existing_output_modifiers` = `local_raw_material_output` + owner's `global_raw_material_output` + `local_<good>_output_modifier` + owner's `global_<good>_output_modifier`, **minus the mod's own previously applied penalty**. The subtraction is required because the penalty modifier itself contributes to `local_raw_material_output`; without it the penalty compounds on itself each tick.

The penalty is applied as a permanent scaled location modifier, `dmsd_rgo_price_penalty` (which carries `local_raw_material_output = 1`), replaced in place on each update with the size rounded to 0.01. It is removed entirely, along with its state variables, when price returns to or above base.

## Load Balancer

The full producer set is too large to evaluate in one tick, so the work is spread over countries and over a 12-month cycle. `dmsd_rgo_assign_countries` numbers every country into `dmsd_rgo_country_idx` and records the total in `dmsd_rgo_country_count`. Each country then owns a contiguous slice of the unified location index:

- `slice = ceil(loc_count / country_count)`, the locations one country owns
- `share = ceil(slice / 12)`, how many of those it walks per month
- `phase = months_elapsed % 12`, which twelfth of the slice comes up this month
- the walk runs from `country_idx * slice + phase * share`, for `share` steps, stopping at `min((country_idx + 1) * slice, loc_count)`

`dmsd_months_elapsed` is a global month counter derived from `current_year`/`current_month` against a 1337-04 epoch. It is written with a 25-day expiry so it recomputes itself every month rather than needing incrementing.

Every producing location is therefore triaged once per year, with the cost of a single month's tick bounded by `share` per country.

## Phase 1: Triage

`dmsd_rgo_triage` runs on each location the balancer hands it:

- **Price at or above base:** if a penalty is applied, strip the modifier and its state variables (`dmsd_rgo_applied`, `dmsd_rgo_last_price`). Nothing is queued.
- **Price below base:** round `relative_raw_material_price` to the nearest 0.02. If the rounded value differs from `dmsd_rgo_last_price` (or that variable is missing), store the new value and push the location onto its anchor's `dmsd_rgo_pending` list.

The rounding is the price pre-filter: the modifier math only runs when the rounded price actually moved, so a stable market queues nothing.

## Phase 2: Penalty Computation

`dmsd_rgo_update_pending` iterates the 52 goods. For each, it looks up the good's anchor in `dmsd_rgo_good_anchors`, jumps there, applies the penalty to every location on that anchor's `dmsd_rgo_pending` list, then clears the list. Iterating per good is what makes the `$good$` parameter available for the `local_<good>_output_modifier` reads in the formula.

`dmsd_rgo_apply_penalty` also carries a **delta threshold**: the modifier is only rewritten when the target differs from the applied value by more than 0.007, reducing modifier churn.

## Data Structures

| Name | Scope | Contents |
|------|-------|----------|
| `dmsd_rgo_loc_index` | global map | index number to location, the unified list the balancer walks |
| `dmsd_rgo_loc_count` | global | size of that index; its absence is the "not initialized" signal |
| `dmsd_rgo_good_anchors` | global map | good to its anchor location (the first producer found at init) |
| `dmsd_rgo_vm_<good>` | global map | which locations produce each good, one map per good |
| `dmsd_rgo_country_idx` / `dmsd_rgo_country_count` | country / global | load balancer slice assignment |
| `dmsd_rgo_anchor` | location | reference to this location's good anchor, so triage can route without knowing the good |
| `dmsd_rgo_pending` | location list | on anchors only: this good's locations awaiting Phase 2 |
| `dmsd_rgo_last_price` | location | last rounded relative price, the pre-filter comparand |
| `dmsd_rgo_applied` | location | the penalty size currently on the modifier |

The anchor indirection is what lets Phase 1 stay good-agnostic. Triage reads `dmsd_rgo_anchor` off the location and appends to that anchor's list; only Phase 2 needs to know which good it is handling.

## Init and Maintenance

**Game start and re-enable:** `dmsd_rgo_init_vm` clears and rebuilds the per-good maps, the unified index, and the anchors; `dmsd_rgo_assign_countries` numbers the countries; `dmsd_rgo_initial_pass` then applies penalties to every below-base producer immediately, rather than waiting a year for the balancer to cycle through. The monthly effect detects the uninitialized state by the absence of `dmsd_rgo_loc_count` and runs this same sequence.

**`on_raw_material_changed`:** the location is removed from all 52 per-good maps (brute force, each removal is O(1)), added to the new good's map, and given the new good's anchor. A location with no prior anchor is newly colonized, so it is appended to the unified index and the count is bumped. Its penalty and price state are stripped, then it is queued onto the new anchor's pending list if the new good is below base.

**Rule disable:** `dmsd_rgo_full_cleanup` strips the modifier, all four location variables, and the pending lists from every owned location, then clears the global index, anchors, and count. A `dmsd_rgo_cleaned` sentinel keeps it from running more than once.
