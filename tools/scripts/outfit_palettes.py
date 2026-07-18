#!/usr/bin/env python3
"""Add the player's alternate outfit palettes to the mmodel files.

The avatar is one model per state (walking, cycling, surfing...), twice over,
hero/heroine: 18 files. Run against pristine files, then `make rom`.

    outfit_palettes.py [--gender male|female|both] [--dry-run]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import btx0_palette
from btx0_palette import Btx0Error, hex_to_rgb555, parse_palettes

MMODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "..",
    "res",
    "prebuilt",
    "data",
    "mmodel",
    "mmodel",
)

VARIANT_NAMES = [
    "outfit_red",
    "outfit_green",
    "outfit_purple",
    "outfit_orange",
    "outfit_grey",
]

MALE_OUTFIT_COLORS = [
    "#BD394A",
    "#DE6A7B",
    "#7B4141",
    "#39628B",
    "#6273BD",
    "#5A83E6",
]

TARGET_COLORS = {
    "outfit_red": ["#C52020", "#F66262", "#832020", "#A40000", "#FF0000", "#FF0083"],
    "outfit_green": ["#20A420", "#62F662", "#186A18", "#00A400", "#00FF00", "#83FF00"],
    "outfit_purple": ["#8320C5", "#C562F6", "#521083", "#6200A4", "#A400FF", "#C562FF"],
    "outfit_orange": ["#E67300", "#FFB441", "#944100", "#A45200", "#FF8300", "#FFC541"],
    "outfit_grey": ["#414141", "#838383", "#202020", "#313131", "#737373", "#A4A4A4"],
}

FEMALE_OUTFIT_COLORS = [
    "#39628B",
    "#7B4141",
    "#C56A9C",
    "#C53939",
    "#F66A4A",
    "#EE94C5",
]

MALE_MODELS = {
    90: 6,  # pl_boy01c
    92: 6,  # pl_cyclehero
    155: 6,  # pl_sphero
    157: 5,  # pl_whelo      lacks #6273BD
    159: 6,  # pl_swimhiro
    166: 6,  # pl_fishhero
    363: 6,  # pl_pokehero
    365: 5,  # pl_savehero   lacks #39628B
    415: 6,  # pl_bshero
}

FEMALE_MODELS = {
    91: 6,  # pl_girl01c
    93: 6,  # pl_cycheroine
    156: 6,  # pl_spheroine
    158: 5,  # pl_wheroine   lacks #EE94C5
    160: 6,  # pl_swimhiroine
    167: 6,  # pl_fheroine
    364: 6,  # pl_pkheroine
    366: 6,  # pl_saveheroine
    416: 6,  # pl_bsheroine
}


def luminance(rgb555):
    r, g, b = rgb555 & 0x1F, (rgb555 >> 5) & 0x1F, (rgb555 >> 10) & 0x1F
    return 0.299 * r + 0.587 * g + 0.114 * b


def model_path(index):
    return os.path.join(MMODEL_DIR, "mmodel_{:08d}.bin".format(index))


def male_replacements(variant):
    return {
        hex_to_rgb555(src): hex_to_rgb555(dst)
        for src, dst in zip(MALE_OUTFIT_COLORS, TARGET_COLORS[variant])
    }


def female_replacements(variant):
    sources = sorted((hex_to_rgb555(c) for c in FEMALE_OUTFIT_COLORS), key=luminance)
    targets = sorted((hex_to_rgb555(c) for c in TARGET_COLORS[variant]), key=luminance)
    return dict(zip(sources, targets))


def apply_to_model(index, expected_swaps, build_replacements, dry_run):
    with open(model_path(index), "rb") as handle:
        palettes = parse_palettes(handle.read())

    base_name = palettes[0].name
    clashes = [n for n in VARIANT_NAMES if n in {p.name for p in palettes}]
    if clashes:
        raise Btx0Error(
            "model {} already has palette(s) {} - nothing written".format(
                index, ", ".join(clashes)
            )
        )

    for variant in VARIANT_NAMES:
        with open(model_path(index), "rb") as handle:
            data = handle.read()

        source = [p for p in parse_palettes(data) if p.name == base_name][0]
        colors, swapped = btx0_palette.replace_colors(
            source.colors, build_replacements(variant)
        )

        if swapped != expected_swaps:
            raise Btx0Error(
                "model {} ({}): {} replaced for {}, expected {}".format(
                    index, base_name, swapped, variant, expected_swaps
                )
            )

        if not dry_run:
            with open(model_path(index), "wb") as handle:
                handle.write(btx0_palette.add_palette(data, variant, colors))

    print(
        "{} mmodel_{:08d} ({}): {} palettes, {} colours each".format(
            "would patch" if dry_run else "patched",
            index,
            base_name,
            len(VARIANT_NAMES),
            expected_swaps,
        )
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gender", choices=["male", "female", "both"], default="both")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="check every file would swap the expected colours, write nothing",
    )
    args = parser.parse_args(argv)

    groups = []
    if args.gender in ("male", "both"):
        groups.append(("male", MALE_MODELS, male_replacements))
    if args.gender in ("female", "both"):
        groups.append(("female", FEMALE_MODELS, female_replacements))

    try:
        for label, models, build in groups:
            print("== {} ==".format(label))
            for index, expected in models.items():
                apply_to_model(index, expected, build, args.dry_run)
            print()
    except Btx0Error as error:
        print("error: {}".format(error), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
