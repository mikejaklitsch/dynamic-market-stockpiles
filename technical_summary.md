# DMSD Technical Summary

The mod contains three independent systems, each with its own game rule toggle and its own document:

| System             | Toggle                        | Document                                                    |
|--------------------|-------------------------------|-------------------------------------------------------------|
| Dynamic Stockpiles | `dmsd_stockpiles_disabled`    | [docs/dynamic_stockpiles.md](docs/dynamic_stockpiles.md)    |
| Slider Demand      | `dmsd_slider_demand_disabled` | [docs/slider_demand.md](docs/slider_demand.md)              |
| RGO Productivity   | `dmsd_rgo_disabled`           | [docs/rgo_productivity.md](docs/rgo_productivity.md)        |

Dynamic Stockpiles scales each market's stockpile capacity with its trade value. Slider Demand converts each country's court, diplomatic, stability, and cultural spending into goods demand on markets. RGO Productivity penalizes raw material output when its price falls below base, creating a price-responsive supply curve.

## Entry Points

All work is driven by on_action hooks defined in `in_game/common/on_action/dmsd_monthly.txt`:

| Hook                      | Scope       | Work performed                                                                        |
|---------------------------|-------------|---------------------------------------------------------------------------------------|
| `on_game_start`           | global      | Stockpile scaling, init check, RGO index build, RGO update                            |
| `monthly_country_pulse`   | per country | Proximity cache rebuild (players), Phase 1 spending events                            |
| `weather_monthly_pulse`   | global      | Stockpile scaling, init check, Phase 2 apply, swap toggle, orphan cleanup, RGO update |
| `yearly_country_pulse`    | per country | Proximity cache rebuild (AI)                                                          |
| `on_capital_moved`        | per country | Proximity cache rebuild                                                               |
| `on_raw_material_changed` | location    | RGO index maintenance                                                                 |

## Monthly Execution Order

1. `monthly_country_pulse` fires first, once per country:
   - The proximity cache rebuilds (players only; AI rebuilds on `yearly_country_pulse`; all countries also rebuild on `on_capital_moved`, and event .1 rebuilds lazily if the cache is missing).
   - Phase 1 events run: .1 court, .2 diplomatic, .3 stability, .5 cultural (.4 was removed; the numbering gap is historical).
2. `weather_monthly_pulse` fires second, globally, after all countries: stockpile scaling, init check, Phase 2 apply, swap toggle, orphan cleanup, RGO update.

Phase 1 computes each country's spending gold and accumulates it into market location maps; Phase 2 reads those maps and applies market demands. The two-pulse split guarantees every country has accumulated before any market applies.

## Init and Rule Toggles

The init check runs at game start and monthly, and it detects three conditions: rule disable, version mismatch, and first run. Disabling a rule mid-game runs cleanup once and sets a sentinel; the system then idles. Re-enabling triggers a full reinit, which rebuilds the demand registries and proximity caches.
