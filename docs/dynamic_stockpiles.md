# Dynamic Stockpiles

Stockpile capacity scales per market from total traded value with sqrt diminishing returns. Capacity is recalculated monthly and at game start; execution order is in [technical_summary.md](../technical_summary.md).

**Formula:** `capacity = 250 * sqrt(traded_value / 2500)`, where `traded_value` = `market.total_goods_value_traded`. The result is called the trade base below.

Two permanent location modifiers on the market center, replaced in place each recalculation:

- `dws_stockpile_scaling` (flat base): this modifier is sized so the location's total flat capacity equals the trade base. The offset works by bookkeeping: the mod stores its own last applied sizes in `dws_last_size` / `dws_last_pct_size`, computes `vanilla_flat = modifier:maximum_stockpile_capacity` minus those stored sizes, then applies `trade_base - vanilla_flat`. This value goes negative when vanilla flat capacity exceeds the formula; that is intended, the modifier pulls total capacity down to the trade base.
- `dws_stockpile_pct_bonus`: this modifier adds `trade_base * maximum_stockpile_capacity_modifier`, letting buildings and development scale capacity as a percentage of the trade-value base instead of vanilla's flat base.

Orphaned locations (no longer market centers) have their modifiers and bookkeeping variables stripped monthly.

**Defines:** vanilla ramps stockpile bleed from 50% fill to a max at 75% fill. The mod ramps linearly from 0% to 100% fill (bleed maxes at 5% of capacity at full), and sets `STOCKPILE_TRADE_IMPACT_ON_SUPPLY_SCALE = 0.25`, so a quarter of the bleed counts toward price-forming supply (max 2.5% at full).
