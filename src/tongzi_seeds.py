"""
童子 v0.5 · seed vectors & labels
===================================
60 fixed seed vectors spanning 12 polarity pairs.
Pre-labeled with cluster assignments.
"""
from tongzi_core import BitStore

SEEDS = [
    # ── heaven/earth (8) ──
    ("h_sky",     0xFFFF),   # all-1
    ("e_ground",  0x0000),   # all-0
    ("h_vault",   0xFFFE),
    ("e_deep",    0x0001),
    ("h_clear",   0xFFF0),
    ("e_turbid",  0x000F),
    ("h_high",    0x7FFF),
    ("e_low",     0x8000),

    # ── motion/stillness (6) ──
    ("m_rise",    0xAAAA),
    ("s_stop",    0x5555),
    ("m_fast",    0xCCCC),
    ("s_slow",    0x3333),
    ("m_flow",    0xA5A5),
    ("s_hide",    0x5A5A),

    # ── solid/void (6) ──
    ("so_full",   0xFF00),
    ("v_empty",   0x00FF),
    ("so_hard",   0xF0F0),
    ("v_soft",    0x0F0F),
    ("so_fixed",  0xFC00),
    ("v_haze",    0x03FF),

    # ── bright/dark (4) ──
    ("b_light",   0xFF55),
    ("d_night",   0x00AA),
    ("b_shine",   0xF0F0),
    ("d_abyss",   0x0F0F),

    # ── warm/cold (4) ──
    ("w_spring",  0x7F7F),
    ("c_winter",  0x8080),
    ("w_sun",     0x7FFE),
    ("c_frost",   0x8001),

    # ── rigid/fluid (4) ──
    ("r_stone",   0xFFF8),
    ("f_water",   0x0007),
    ("r_iron",    0xFFC0),
    ("f_silk",    0x003F),

    # ── straight/crooked (4) ──
    ("st_upright", 0xF00F),
    ("cr_bent",    0x0FF0),
    ("st_direct",  0xC3C3),
    ("cr_winding", 0x3C3C),

    # ── union/separation (6) ──
    ("u_join",    0xFFFF),
    ("sp_split",  0x0000),
    ("u_accord",  0xFF0F),
    ("sp_apart",  0x00F0),
    ("u_merge",   0xF00F),
    ("sp_part",   0x0FF0),

    # ── joy/anger/sorrow/delight (8) ──
    ("joy_lift",  0x7F80),
    ("ang_rage",  0x807F),
    ("sor_grief", 0x1F1F),
    ("del_cheer", 0xE0E0),
    ("joy_light", 0x7FF0),
    ("ang_heat",  0x800F),
    ("sor_gloom", 0x1F00),
    ("del_bright", 0xE0FF),

    # ── near/far (4) ──
    ("n_close",   0xFF0F),
    ("f_remote",  0x00F0),
    ("n_touch",   0xF00F),
    ("f_beyond",  0x0FF0),

    # ── day/night cycle (6) ──
    ("day_dawn",  0x7FFF),
    ("night_dusk", 0x8000),
    ("day_noon",  0xFFFF),
    ("night_mid", 0x0000),
    ("day_sunset",0x3FFF),
    ("night_moon",0xC000),
]

SEED_LABELS = {
    "h_sky": "heaven",    "h_vault": "heaven",
    "h_clear": "heaven",  "h_high": "heaven",
    "e_ground": "earth",  "e_deep": "earth",
    "e_turbid": "earth",  "e_low": "earth",
    "m_rise": "motion",   "m_fast": "motion",
    "m_flow": "motion",
    "s_stop": "still",    "s_slow": "still",
    "s_hide": "still",
    "so_full": "solid",   "so_hard": "solid",
    "so_fixed": "solid",
    "v_empty": "void",    "v_soft": "void",
    "v_haze": "void",
    "b_light": "bright",  "b_shine": "bright",
    "d_night": "dark",    "d_abyss": "dark",
    "w_spring": "warm",   "w_sun": "warm",
    "c_winter": "cold",   "c_frost": "cold",
    "r_stone": "rigid",   "r_iron": "rigid",
    "f_water": "fluid",   "f_silk": "fluid",
    "st_upright": "straight", "st_direct": "straight",
    "cr_bent": "crooked", "cr_winding": "crooked",
    "u_join": "union",    "u_accord": "union",
    "u_merge": "union",
    "sp_split": "split",  "sp_apart": "split",
    "sp_part": "split",
    "joy_lift": "joy",    "joy_light": "joy",
    "ang_rage": "anger",  "ang_heat": "anger",
    "sor_grief": "sorrow","sor_gloom": "sorrow",
    "del_cheer": "delight","del_bright": "delight",
    "n_close": "near",    "n_touch": "near",
    "f_remote": "far",    "f_beyond": "far",
    "day_dawn": "day",    "day_noon": "day",
    "day_sunset": "day",
    "night_dusk": "night","night_mid": "night",
    "night_moon": "night",
}

def inject_seeds(store: BitStore):
    """Inject all 60 seeds into the store."""
    for tag, vec in SEEDS:
        store.data[tag] = vec
        store.active[tag] = store.tick
        store.hits[tag] = 0
        store.potency[tag] = 0
    return len(SEEDS)
