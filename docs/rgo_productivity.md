# RGO Productivity

This system penalizes RGO output when market price falls below the good's base price, creating a price-responsive supply curve. It runs monthly in `weather_monthly_pulse` and at game start, and it reindexes on `on_raw_material_changed`; execution order is in [technical_summary.md](../technical_summary.md).

**Penalty formula:** `penalty = relative_price * sensitivity * (1 + existing_output_modifiers)`

Where `relative_price` is the vanilla location trigger `relative_raw_material_price` (price relative to base, negative below base) and `sensitivity` = 1.0.

`existing_output_modifiers` = `local_raw_material_output + owner's global_raw_material_output + local_<good>_output_modifier + owner's global_<good>_output_modifier`, **minus the mod's own previously applied penalty**. The subtraction is required because the penalty modifier itself contributes to `local_raw_material_output`; without it the penalty compounds on itself each tick.

The penalty is applied as a permanent scaled location modifier, `dmsd_rgo_price_penalty` (which carries `local_raw_material_output = 1`), replaced in place on each update with the size rounded to 0.01. It is removed entirely, along with its state variables, when price returns to or above base.

**Optimizations:**
- Per-good global variable maps (`dmsd_rgo_vm_<good>`) index which locations produce each good, avoiding a full world scan. The maps are built at game start; `on_raw_material_changed` moves the location between maps and strips its penalty and state.
- Price pre-filter: relative price is rounded to the nearest 0.02 and compared against the last evaluation; the modifier math only runs when the rounded price changed.
- Delta threshold: the modifier is only rewritten when the target differs from the applied value by more than 0.007, reducing modifier churn.
