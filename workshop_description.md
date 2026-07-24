[h1]Dynamic Market Stockpiles and Demand[/h1]

Every market in EU5 gets the same stockpile capacity, so Cahokia and Constantinople hold the same amount of goods. When those stockpiles add supply relative to stockpile size, prices in small markets crash while large ones have enough demand to absorb it. And when prices do crash, RGOs keep pumping out goods at full output regardless.

This mod scales stockpile capacity to market size, adds goods demand from government spending, reduces RGO output when prices fall below base value, and optionally allows you to disable burgher trading.

[h2]Dynamic Stockpiles[/h2]

Stockpile capacity scales with actual market size. Larger markets have higher demand, so the extra supply from stockpiles has less impact on prices. Markets trading above 2,500 total value gain extra capacity; markets below that threshold lose capacity, down to a floor of 5%. As economies grow throughout the game, stockpile capacity grows with them, keeping the system balanced the entire time.

[h2]RGO Price Response[/h2]

When a good's market price falls below its base price, RGO output for that good drops proportionally. A good trading at 20% below base loses exactly 20% of its output. The penalty accounts for existing local and global output modifiers so the reduction is a true percentage of actual production, not a flat cut. When price returns to base or above, any remaining penalty is removed entirely.

This creates a natural supply correction: oversupplied goods see reduced production, which relieves price pressure and helps markets find equilibrium instead of spiraling into permanent gluts.

[h2]Slider Demand[/h2]

The gold you spend on court, diplomacy, stability, and culture now becomes demand for goods at your proximity sources. Higher spending means more demand, with diminishing returns at larger amounts. Court spending splits between a subcontinental goods basket and a religious one based on your faith; the other three sliders use subcontinental baskets only.

The goods demanded at each proximity source depend on that location's subcontinent. A proximity source in Western Europe generates demand for furniture, fine cloth, glass, marble, and pearls. One in South Asia generates demand for silk, cotton, and incense. If your proximity sources span multiple subcontinents, different goods are demanded at each. Court religious baskets vary the same way: Christian court ceremonies demand wine, wheat, beeswax, and olives, while Muslim courts demand coffee, sugar, pepper, and porcelain.

[h2]Game Rules[/h2]

All systems are fully controllable via game rules and can be toggled mid-game. Disabling a system cleanly removes all its effects on the next month tick. This should be done before removing the mod to make sure nothing lingers after it's removed.

[list]
[*] Dynamic Stockpiles: on/off (default on)
[*] Slider Demand: on/off (default on)
[*] RGO Price Response: on/off (default on)
[*] Burgher Trading: on/off (default on). Disabling removes all burgher trade capacity.
[/list]

The stockpile supply defines which were disabled in 1.3.2 have been tweaked and re-added (0-100% linear ramp instead of vanilla's 50-75% range, 2.5% of stockpile as supply instead of 5%) and are always active and cannot be disabled (I tried to add the option but it's not supported).

[h2]Compatibility[/h2]

Only compatible with 1.3+. Modifiers the system relies on don't exist in 1.2.5 or exist differently.

No vanilla files are overwritten except the market destruction action (removes a temporary-demand check that would block it). This should be compatible with almost any mod unless it modifies the way slider values are calculated, how markets work at a fundamental level, or overrides the destroy market action. In other words, it really won't conflict with anything that currently exists. The new RGO output reduction mechanic will not have any effect for mods which remove RGOs(Prosper or Perish/MEIOU and Taxes/etc.) because it scales RGO output, not the output of the specific good. If those mods repurpose that modifier, I can't predict how the system will behave so I suggest disabling it in the game rules.

[h2]Feedback[/h2]

If you decide to unsubscribe for whatever reason, and can be constructive about it please leave a quick comment. I will be actively maintaining this and adding features in response to feedback and the goal is to make it an enjoyable mod to use and I can only do that with feedback.
