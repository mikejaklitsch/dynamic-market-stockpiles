#!/usr/bin/env python3
"""
DMSD demand generator — produces demand definitions, IO weight containers,
and init code from a single data source.

Weights are set so gold is distributed across goods roughly proportional to
1/price (equal-gold-allocation), then scaled by an importance factor.
The generator normalizes within each basket so total basket cost stays
consistent regardless of the number of goods.

Output files (--write):
  - in_game/common/goods_demand/dmsd_generated_demands.txt
  - in_game/common/international_organizations/dmsd_generated_ios.txt
  - in_game/common/scripted_effects/dmsd_generated_init.txt

Usage:
  python gen_dmsd_demands.py              # Preview
  python gen_dmsd_demands.py --write      # Write output files
"""

import os
import sys
import argparse
from collections import OrderedDict

# =============================================================================
# VANILLA BASE PRICES
# =============================================================================

PRICES = {
    "amber": 4, "beer": 2, "beeswax": 2, "books": 3, "chili": 5,
    "cloth": 3, "cloves": 5, "coal": 2, "cocoa": 4, "coffee": 3,
    "cotton": 3, "dyes": 4, "fine_cloth": 6, "fruit": 1, "fur": 2,
    "furniture": 3, "gems": 4, "glass": 3, "horses": 3, "incense": 2.5,
    "ivory": 4, "jewelry": 5, "lacquerware": 5, "leather": 3,
    "legumes": 1, "liquor": 2.5, "livestock": 1.5, "maize": 1,
    "marble": 5, "medicaments": 1, "olives": 1, "paper": 2,
    "pearls": 4, "pepper": 5, "porcelain": 3, "potato": 1,
    "salt": 4, "silk": 4, "sugar": 3, "tea": 3,
    "tobacco": 3, "tools": 3, "weaponry": 3, "wheat": 1,
    "wild_game": 1, "wine": 2, "wool": 2.5,
}

# Reference price for weight computation: weight = (ref / price) * importance
REF_PRICE = 3.0


def compute_weight(good, importance=1.0):
    """Weight = (ref_price / good_price) * importance, rounded to 4 places."""
    return round((REF_PRICE / PRICES[good]) * importance, 4)


def make_basket(goods_with_importance):
    """Build a basket dict from [(good, importance), ...]."""
    return OrderedDict(
        (good, compute_weight(good, imp))
        for good, imp in goods_with_importance
    )


# =============================================================================
# DEMAND VARIANT DATA
# =============================================================================
# Each good has an importance factor (1.0 = standard, <1 = secondary, >1 = emphasis).
# Actual weight = (ref_price / market_price) * importance.

# --- COURT: regional subcontinent variants ---
# Core goods: furniture, fine_cloth, glass
# Regionals add thematic luxury/craft goods

_court_core = [("furniture", 1.0), ("fine_cloth", 1.0), ("glass", 1.0)]

COURT_REGIONAL = {
    "court_demand": make_basket(_court_core),
    "court_we":  make_basket(_court_core + [("marble", 0.8), ("pearls", 0.4)]),
    "court_ee":  make_basket(_court_core + [("amber", 0.8), ("fur", 0.5)]),
    "court_me":  make_basket(_court_core + [("marble", 0.8), ("incense", 0.7), ("silk", 0.4)]),
    "court_ca":  make_basket(_court_core + [("horses", 0.8), ("fur", 0.5)]),
    "court_sa":  make_basket(_court_core + [("incense", 0.7), ("silk", 0.5), ("cotton", 0.4)]),
    "court_sea": make_basket(_court_core + [("lacquerware", 0.8), ("silk", 0.4)]),
    "court_ea":  make_basket(_court_core + [("porcelain", 0.8), ("lacquerware", 0.7), ("silk", 0.4)]),
    "court_naf": make_basket(_court_core + [("marble", 0.8), ("incense", 0.4)]),
    "court_af":  make_basket(_court_core + [("ivory", 0.8), ("dyes", 0.4)]),
    "court_eaf": make_basket(_court_core + [("ivory", 0.8), ("incense", 0.6)]),
    "court_nam": make_basket(_court_core + [("fur", 0.8), ("cocoa", 0.5)]),
    "court_sam": make_basket(_court_core + [("gems", 0.8), ("cocoa", 0.5)]),
    "court_nas": make_basket(_court_core + [("fur", 0.8), ("horses", 0.6)]),
}

# --- COURT: religion variants ---
# 3-4 goods per basket, thematic to religious traditions

COURT_RELIGION = {
    "rc_christian":             make_basket([("wine", 1.0), ("wheat", 1.0), ("beeswax", 0.8), ("olives", 0.5)]),
    "rc_muslim":                make_basket([("coffee", 1.0), ("sugar", 1.0), ("pepper",0.8), ("porcelain", 0.4)]),
    "rc_buddhist":              make_basket([("tea", 1.0), ("silk", 1.0), ("incense", 0.8), ("wine", 0.5)]),
    "rc_dharmic":               make_basket([("medicaments", 1.0), ("pepper",1.0), ("cotton", 0.8), ("incense", 0.4), ("liquor", 0.5)]),
    "rc_folk_asian":            make_basket([("tea", 1.0), ("porcelain", 1.0), ("pepper",0.8), ("wine", 0.5)]),
    "rc_zoroastrian":           make_basket([("olives", 1.0), ("incense", 1.0), ("pepper",0.8), ("beeswax", 0.5), ("wine", 0.7)]),
    "rc_israelite":             make_basket([("olives", 1.0), ("wheat", 1.0), ("salt", 0.8), ("wine", 0.7)]),
    "rc_mandean":               make_basket([("salt", 1.0), ("incense", 1.0), ("beeswax", 0.8), ("wine", 0.4)]),
    "rc_manichaean":            make_basket([("silk", 1.0), ("incense", 1.0), ("tea", 0.8)]),
    "rc_tonal":                 make_basket([("cocoa", 1.0), ("dyes", 1.0), ("chili", 0.8), ("cotton", 0.4), ("liquor", 0.5)]),
    "rc_folk_north_american":   make_basket([("fur", 1.0), ("wheat", 1.0), ("wild_game", 0.8), ("beer", 0.5)]),
    "rc_folk_central_american": make_basket([("cocoa", 1.0), ("cotton", 1.0), ("maize", 0.8), ("liquor", 0.5)]),
    "rc_folk_caribbean":        make_basket([("sugar", 1.0), ("dyes", 1.0), ("fruit", 0.8), ("liquor", 0.5)]),
    "rc_folk_south_american":   make_basket([("cocoa", 1.0), ("gems", 1.0), ("fruit", 0.8), ("beer", 0.4)]),
    "rc_folk_peruvian":         make_basket([("wool", 1.0), ("wheat", 1.0), ("potato", 0.8), ("beer", 0.5)]),
    "rc_folk_brazilian":        make_basket([("sugar", 1.0), ("dyes", 1.0), ("fruit", 0.8), ("liquor", 0.5)]),
    "rc_folk_argentinian":      make_basket([("livestock", 1.0), ("wheat", 1.0), ("leather", 0.8), ("wine", 0.5)]),
}

# --- DIPLOMATIC: regional subcontinent variants ---
# Core: paper, jewelry, dyes, leather
# + medicaments (diplomatic corps health), horses (envoy travel)

_diplo_core = [("paper", 1.0), ("jewelry", 1.0), ("dyes", 0.8), ("leather", 0.8),
               ("medicaments", 0.4), ("horses", 0.4)]

DIPLO_REGIONAL = {
    "diplomatic_demand": make_basket(_diplo_core),
    "diplo_salt":        make_basket(_diplo_core + [("salt", 0.6)]),
}

# --- STABILITY: regional subcontinent variants ---
# Core: books, cloth, weaponry
# + tools (infrastructure), medicaments (public health), salt (basic commodity)

_stab_core = [("books", 1.0), ("cloth", 1.0), ("weaponry", 1.0),
              ("tools", 0.5), ("medicaments", 0.4)]

STAB_REGIONAL = {
    "stability_demand": make_basket(_stab_core),
    "stab_ca":  make_basket(_stab_core + [("livestock", 0.7), ("wool", 0.6), ("horses", 0.5)]),
    "stab_nas": make_basket(_stab_core + [("wool", 0.6), ("fur", 0.5)]),
}

# --- CULTURAL: regional subcontinent variants ---
# Core goods: paper, dyes, fine_cloth, glass (artist materials)
# Regionals add thematic craft/art goods

_cult_core = [("paper", 1.0), ("dyes", 1.0), ("fine_cloth", 0.6), ("glass", 0.5)]

CULT_REGIONAL = {
    "cultural_demand": make_basket(_cult_core),
    "cult_we":  make_basket(_cult_core + [("marble", 0.5), ("jewelry", 0.5)]),
    "cult_ee":  make_basket(_cult_core + [("beeswax", 0.5), ("amber", 0.5)]),
    "cult_me":  make_basket(_cult_core + [("gems", 0.5), ("silk", 0.5)]),
    "cult_ca":  make_basket(_cult_core + [("silk", 0.5), ("wool", 0.5)]),
    "cult_sa":  make_basket(_cult_core + [("gems", 0.5), ("cotton", 0.5)]),
    "cult_sea": make_basket(_cult_core + [("lacquerware", 0.5), ("silk", 0.5)]),
    "cult_ea":  make_basket(_cult_core + [("porcelain", 0.5), ("lacquerware", 0.5)]),
    "cult_naf": make_basket(_cult_core + [("marble", 0.5), ("leather", 0.5)]),
    "cult_af":  make_basket(_cult_core + [("ivory", 0.5), ("leather", 0.5)]),
    "cult_eaf": make_basket(_cult_core + [("ivory", 0.5), ("leather", 0.5)]),
    "cult_nam": make_basket(_cult_core + [("leather", 0.5), ("fur", 0.5)]),
    "cult_sam": make_basket(_cult_core + [("gems", 0.5), ("cotton", 0.5)]),
    "cult_nas": make_basket(_cult_core + [("ivory", 0.5), ("fur", 0.5)]),
}

# =============================================================================
# COLLECT ALL VARIANTS
# =============================================================================

ALL_VARIANTS = []
for name, goods in COURT_REGIONAL.items():
    ALL_VARIANTS.append((name, goods))
for name, goods in COURT_RELIGION.items():
    ALL_VARIANTS.append((name, goods))
for name, goods in DIPLO_REGIONAL.items():
    ALL_VARIANTS.append((name, goods))
for name, goods in STAB_REGIONAL.items():
    ALL_VARIANTS.append((name, goods))
for name, goods in CULT_REGIONAL.items():
    ALL_VARIANTS.append((name, goods))


# Bump this when generated data changes to trigger save-game rebuild
VERSION = 103


def fmt(v):
    if v == 0:
        return "0"
    r = round(v, 4)
    s = f"{r:.4f}".rstrip("0").rstrip(".")
    return s


# =============================================================================
# GENERATE DEMAND DEFINITIONS
# =============================================================================

def generate_demands():
    lines = ["# Generated by gen_dmsd_demands.py", ""]
    for name, goods in ALL_VARIANTS:
        goods_str = " ".join(f"{g} = {fmt(w)}" for g, w in goods.items())
        lines.append(f"dmsd_{name}1 = {{ {goods_str} category = government_activities }}")
        lines.append(f"dmsd_{name}2 = {{ {goods_str} category = government_activities }}")
    lines.append("")
    return "\n".join(lines)


# =============================================================================
# GENERATE IO DEFINITIONS
# =============================================================================

def generate_ios():
    lines = ["# Generated by gen_dmsd_demands.py",
             "# Hidden IOs as variable map containers for demand weights.", ""]
    for name, _ in ALL_VARIANTS:
        lines.append(f"dmsd_io_{name} = {{")
        lines.append(f"\tunique = yes")
        lines.append(f"\thas_target = no")
        lines.append(f"\tshow_on_diplomatic_map = no")
        lines.append(f"\tcreate_visible_trigger = {{ always = no }}")
        lines.append(f"\tauto_disband_trigger = {{ always = no }}")
        lines.append(f"}}")
        lines.append("")
    return "\n".join(lines)


# =============================================================================
# GENERATE INIT SCRIPTED EFFECT
# =============================================================================

def generate_init():
    lines = ["# Generated by gen_dmsd_demands.py", ""]
    lines.append("dmsd_init_demand_ios = {")

    # Destroy stale IOs
    lines.append("\t# Destroy stale IOs from previous save")
    lines.append("\trandom_country = {")
    lines.append("\t\tlimit = { is_real_country = yes }")
    lines.append("\t\tevery_in_global_list = {")
    lines.append("\t\t\tvariable = dmsd_all_ios")
    lines.append("\t\t\tsave_temporary_scope_as = dmsd_io_destroy")
    lines.append("\t\t\tprev = { destroy_international_organization = { target = scope:dmsd_io_destroy } }")
    lines.append("\t\t}")
    lines.append("\t}")
    lines.append("\tclear_global_variable_list = dmsd_all_ios")
    lines.append("\tclear_global_variable_map = dmsd_demand_io")
    lines.append("")

    # Create IOs and populate weight maps
    lines.append("\t# Create IOs with weight maps")
    lines.append("\trandom_country = {")
    lines.append("\t\tlimit = { is_real_country = yes }")
    lines.append("")

    for name, goods in ALL_VARIANTS:
        io_type = f"dmsd_io_{name}"
        goods_block = " ".join(
            f'dmsd_io_good = {{ good = {g} weight = {fmt(w)} }}'
            for g, w in goods.items()
        )
        lines.append(f"\t\tcreate_international_organization = {{ type = international_organization_type:{io_type} {goods_block} }}")
        lines.append(f"\t\tadd_to_global_variable_map = {{ name = dmsd_demand_io key = demand:dmsd_{name}1 value = international_organization:{io_type} }}")
        lines.append(f"\t\tadd_to_global_variable_map = {{ name = dmsd_demand_io key = demand:dmsd_{name}2 value = international_organization:{io_type} }}")
        lines.append(f"\t\tadd_to_global_variable_list = {{ name = dmsd_all_ios target = international_organization:{io_type} }}")
        lines.append("")

    lines.append("\t}")  # close random_country
    lines.append("")

    # Display goods maps (dmsd_tt_*_goods) are populated dynamically per-player
    # by dmsd_update_player_display, not at init time. This ensures the GUI
    # shows only the goods for the player's active regional/religion variant.

    lines.append("}")  # close effect
    lines.append("")

    # Helper effect for IO creation
    lines.append("dmsd_io_good = {")
    lines.append("\tadd_to_variable_map = {")
    lines.append("\t\tname = dmsd_weights")
    lines.append("\t\tkey = goods:$good$")
    lines.append("\t\tvalue = $weight$")
    lines.append("\t}")
    lines.append("}")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# GENERATE IO LOCALIZATION
# =============================================================================

def generate_io_loc():
    lines = ["l_english:", " # Generated by gen_dmsd_demands.py"]
    for name, _ in ALL_VARIANTS:
        io = f"dmsd_io_{name}"
        lines.append(f' {io}: ""')
        lines.append(f' {io}_desc: ""')
        lines.append(f' diplomatic_status_{io}_name: ""')
        lines.append(f' diplomatic_status_{io}_tooltip: ""')
        lines.append(f' {io}_list_who_tt: ""')
        lines.append(f' io_opinion_{io}: ""')
    lines.append("")
    return "\n".join(lines)


# =============================================================================
# GENERATE IO BIASES
# =============================================================================

def generate_io_biases():
    """Each IO type requires an opinion bias entry (engine requirement, value 0)."""
    lines = ["# Generated by gen_dmsd_demands.py",
             "# Opinion biases for hidden IOs (required by engine, value 0).", ""]
    for name, _ in ALL_VARIANTS:
        lines.append(f"io_opinion_dmsd_io_{name} = {{")
        lines.append(f"\tvalue = 0")
        lines.append(f"}}")
        lines.append("")
    return "\n".join(lines)


# =============================================================================
# GENERATE VERSION SCRIPT VALUE
# =============================================================================

def generate_version():
    lines = [
        "# Generated by gen_dmsd_demands.py",
        f"dmsd_version_value = {VERSION}",
        "",
    ]
    return "\n".join(lines)


# =============================================================================
# SUMMARY
# =============================================================================

def print_summary():
    print(f"{'=' * 70}")
    print(f"  DMSD DEMAND GENERATOR — PRICE-WEIGHTED")
    print(f"{'=' * 70}")
    print(f"  Reference price: {REF_PRICE}")
    print(f"  Variants: {len(ALL_VARIANTS)}")
    print(f"  Demand types: {len(ALL_VARIANTS) * 2} (swap pairs)")
    print(f"  IOs: {len(ALL_VARIANTS)}")
    print()

    for name, goods in ALL_VARIANTS:
        basket_cost = sum(w * PRICES.get(g, 3) for g, w in goods.items())
        goods_str = ", ".join(f"{g}={fmt(w)}(@{PRICES.get(g, '?')})" for g, w in goods.items())
        print(f"  {name} (cost={basket_cost:.1f}):")
        print(f"    {goods_str}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate DMSD demand variants")
    parser.add_argument("--write", action="store_true", help="Write output files")
    args = parser.parse_args()

    print_summary()

    outputs = {
        "demands": generate_demands(),
        "ios": generate_ios(),
        "init": generate_init(),
        "io_loc": generate_io_loc(),
        "io_biases": generate_io_biases(),
        "version": generate_version(),
    }

    if args.write:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mod_dir = os.path.dirname(script_dir)

        paths = {
            "demands": os.path.join(mod_dir, "in_game", "common", "goods_demand", "dmsd_generated_demands.txt"),
            "ios": os.path.join(mod_dir, "in_game", "common", "international_organizations", "dmsd_generated_ios.txt"),
            "init": os.path.join(mod_dir, "in_game", "common", "scripted_effects", "dmsd_generated_init.txt"),
            "io_loc": os.path.join(mod_dir, "main_menu", "localization", "english", "dmsd_generated_ios_l_english.yml"),
            "io_biases": os.path.join(mod_dir, "in_game", "common", "biases", "dmsd_generated_biases.txt"),
            "version": os.path.join(mod_dir, "main_menu", "common", "script_values", "dmsd_version.txt"),
        }

        for key, path in paths.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write(outputs[key])
            print(f"Wrote {path}")
    else:
        print("Use --write to generate files")


if __name__ == "__main__":
    main()
