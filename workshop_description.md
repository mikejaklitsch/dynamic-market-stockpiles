[h1]Dynamic Market Stockpiles and Demand[/h1]

Every market in EU5 gets the same stockpile capacity, so Cahokia and Constantinople hold the same amount of goods. When those stockpiles add supply, prices in small markets crash while large ones have enough demand to absorb it.

This mod scales stockpile capacity to market size, and goes further: government spending now generates goods demand, adding pressure on the other side of the equation.

[h2]Dynamic Stockpiles[/h2]

Stockpile capacity scales with actual market size. Larger markets have higher demand, so the extra supply from stockpiles has less impact on prices. Markets trading above 2,500 total value gain extra capacity; markets below that threshold lose capacity, down to a floor of 5%. As economies grow throughout the game, stockpile capacity grows with them, keeping the system balanced from 1337 to the end date.

[h2]Slider Demand[/h2]

The gold you spend on court, diplomacy, stability, and culture now becomes demand for goods at your proximity sources. Higher spending means more demand, with diminishing returns at larger amounts. Court spending splits between a subcontinental goods basket and a religious one based on your faith; the other three sliders use subcontinental baskets only.

The goods demanded at each proximity source depend on that location's subcontinent. A proximity source in Western Europe generates demand for furniture, fine cloth, glass, marble, and pearls. One in South Asia generates demand for silk, cotton, and incense. If your proximity sources span multiple subcontinents, different goods are demanded at each. Court religious baskets vary the same way: Christian ceremonies pull wine, wheat, beeswax, and olives, while Muslim courts pull coffee, sugar, pepper, and porcelain.

[h2]Game Rules[/h2]

Both systems are fully controllable via game rules and can be toggled mid-game. Disabling a system cleanly removes all its effects.

[list]
[*] Dynamic Stockpiles: on/off (default on)
[*] Slider Demand: on/off (default on)
[*] Burgher Trading: on/off (default on). Disabling removes all burgher trade capacity.
[/list]

The stockpile supply defines which were disabled in 1.3.2 have been tweaked and re-added(0-100% linear ramp instead of vanilla's 50-75% range) and are always active and cannot be disabled(I tried).

[h2]Compatibility[/h2]

No vanilla files are overwritten except the market destruction action (removes a temporary-demand check that would block it). This should be compatible with almost any mod unless it modifies the way slider values are calculated, how markets work at a fundamental level, or overrides the destroy market action. In other words, it really won't conflict with anything that currently exists.

---

[h3]Update Comment[/h3]

The original mod scaled stockpile capacity to fix the 1.3 price crashes from stockpile generated supply. With 1.3.2 zeroing out that define, the mod needed a new purpose.

The core problem was never that stockpiles affecting prices is wrong; it's that there was no demand-side counter-pressure. This update re-enables stockpile supply with a smoother 0-100% ramp(vs 1.3.0s 50-75% fill) and adds a new dynamic demand system: court, diplomatic, stability, and cultural spending now generate demand for regional goods baskets distributed across your proximity source markets. Religious and subcontinental variety means different parts of the world demand different goods.

Tooltips now show detailed breakdowns per slider, per source market, and per good. Both systems are game-rule controlled and can be toggled mid-game cleanly.

Balance feedback is welcome, especially on which goods belong in which regional or religious baskets.
