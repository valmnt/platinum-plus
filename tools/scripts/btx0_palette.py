#!/usr/bin/env python3
"""Read and write palettes inside a NITRO BTX0 texture container.

BTX0 holds 3D model textures. tools/nitrogfx does not handle it, hence this
script.

    btx0_palette.py dump FILE
    btx0_palette.py add-palette FILE --name NAME --copy-from NAME
                                     [--replace '#RRGGBB=#RRGGBB' ...]
"""

import argparse
import struct
import sys
from dataclasses import dataclass, field
from typing import List

NAME_LEN = 16
PLTT_ENTRY_SIZE = 4


class Btx0Error(Exception):
    pass


@dataclass
class Palette:
    name: str
    offset: int
    colors: List[int] = field(default_factory=list)


def rgb555_to_hex(value):
    r, g, b = value & 0x1F, (value >> 5) & 0x1F, (value >> 10) & 0x1F
    return "#{:02X}{:02X}{:02X}".format(r * 255 // 31, g * 255 // 31, b * 255 // 31)


def hex_to_rgb555(text):
    digits = text.lstrip("#")
    if len(digits) != 6:
        raise Btx0Error("expected #RRGGBB, got {!r}".format(text))
    try:
        r, g, b = (int(digits[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise Btx0Error("expected #RRGGBB, got {!r}".format(text))
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def _find_tex0(data):
    if len(data) < 0x14 or data[:4] != b"BTX0":
        raise Btx0Error("not a BTX0 container")
    (num_sections,) = struct.unpack_from("<H", data, 0x0E)
    for i in range(num_sections):
        (offset,) = struct.unpack_from("<I", data, 0x10 + i * 4)
        if data[offset : offset + 4] == b"TEX0":
            return offset
    raise Btx0Error("no TEX0 section in container")


def parse_palettes(data):
    tex0 = _find_tex0(data)

    (pltt_size,) = struct.unpack_from("<I", data, tex0 + 0x30)
    pltt_size <<= 3
    (info_offset,) = struct.unpack_from("<I", data, tex0 + 0x34)
    (data_offset,) = struct.unpack_from("<I", data, tex0 + 0x38)

    return _parse_dictionary(data, tex0 + info_offset, tex0 + data_offset, pltt_size)


def _parse_dictionary(data, dict_offset, data_base, pltt_size):
    num_objs = data[dict_offset + 1]
    (section_size,) = struct.unpack_from("<H", data, dict_offset + 2)

    names_offset = dict_offset + section_size - num_objs * NAME_LEN
    entries_offset = names_offset - num_objs * PLTT_ENTRY_SIZE

    (size_unit,) = struct.unpack_from("<H", data, entries_offset - 4)
    if size_unit != PLTT_ENTRY_SIZE:
        raise Btx0Error(
            "unexpected PLTT entry size {} (expected {})".format(
                size_unit, PLTT_ENTRY_SIZE
            )
        )

    starts = []
    for i in range(num_objs):
        (raw,) = struct.unpack_from("<H", data, entries_offset + i * PLTT_ENTRY_SIZE)
        starts.append(raw << 3)

    palettes = []
    for i in range(num_objs):
        raw_name = data[names_offset + i * NAME_LEN : names_offset + (i + 1) * NAME_LEN]
        name = raw_name.split(b"\0")[0].decode("ascii")

        later = [s for s in starts if s > starts[i]]
        end = min(later) if later else pltt_size
        count = (end - starts[i]) // 2
        absolute = data_base + starts[i]
        colors = list(struct.unpack_from("<{}H".format(count), data, absolute))
        palettes.append(Palette(name=name, offset=absolute, colors=colors))

    return palettes


def replace_colors(colors, replacements):
    swapped = 0
    result = []

    for value in colors:
        if value in replacements:
            result.append(replacements[value])
            swapped += 1
        else:
            result.append(value)

    return result, swapped


def _build_dictionary(num_entries, entries, names):
    node_bytes = (num_entries + 1) * 4
    ofs_entry = 8 + node_bytes
    ofs_name = 4 + num_entries * PLTT_ENTRY_SIZE
    size_dict_blk = ofs_entry + ofs_name + num_entries * NAME_LEN

    nodes = bytearray(b"\x7f\x01\x00\x00")
    for i in range(num_entries):
        nodes += bytes((0x46 + i, 0x00, i + 1, i))

    return (
        struct.pack("<BBHHH", 0, num_entries, size_dict_blk, 8, ofs_entry)
        + bytes(nodes[:node_bytes])
        + struct.pack("<HH", PLTT_ENTRY_SIZE, ofs_name)
        + entries
        + names
    )


def add_palette(data, name, colors):
    if len(name.encode("ascii")) > NAME_LEN - 1:
        raise Btx0Error("palette name {!r} exceeds {} bytes".format(name, NAME_LEN - 1))

    tex0 = _find_tex0(data)
    (pltt_size,) = struct.unpack_from("<I", data, tex0 + 0x30)
    pltt_size <<= 3
    (info_rel,) = struct.unpack_from("<I", data, tex0 + 0x34)
    (data_rel,) = struct.unpack_from("<I", data, tex0 + 0x38)

    dict_offset = tex0 + info_rel
    num_objs = data[dict_offset + 1]
    (old_dict_size,) = struct.unpack_from("<H", data, dict_offset + 2)

    existing = _parse_dictionary(data, dict_offset, tex0 + data_rel, pltt_size)
    if any(p.name == name for p in existing):
        raise Btx0Error("palette {!r} already exists".format(name))

    old_names_offset = dict_offset + old_dict_size - num_objs * NAME_LEN
    old_entries_offset = old_names_offset - num_objs * PLTT_ENTRY_SIZE
    old_entries = data[
        old_entries_offset : old_entries_offset + num_objs * PLTT_ENTRY_SIZE
    ]
    old_names = data[old_names_offset : old_names_offset + num_objs * NAME_LEN]

    new_dict = _build_dictionary(
        num_objs + 1,
        bytes(old_entries) + struct.pack("<HH", pltt_size >> 3, 0),
        bytes(old_names) + name.encode("ascii").ljust(NAME_LEN, b"\0"),
    )
    delta = len(new_dict) - old_dict_size

    new_colors = struct.pack("<{}H".format(len(colors)), *colors)
    pltt_abs = tex0 + data_rel

    rebuilt = bytearray(
        data[:dict_offset]
        + new_dict
        + data[dict_offset + old_dict_size : pltt_abs]
        + data[pltt_abs : pltt_abs + pltt_size]
        + new_colors
    )

    for field_offset in (0x14, 0x24, 0x28, 0x38):
        (value,) = struct.unpack_from("<I", rebuilt, tex0 + field_offset)
        if value > info_rel:
            struct.pack_into("<I", rebuilt, tex0 + field_offset, value + delta)

    struct.pack_into("<I", rebuilt, tex0 + 0x30, (pltt_size + len(new_colors)) >> 3)

    (section_size,) = struct.unpack_from("<I", rebuilt, tex0 + 0x04)
    struct.pack_into("<I", rebuilt, tex0 + 0x04, section_size + delta + len(new_colors))
    struct.pack_into("<I", rebuilt, 0x08, len(rebuilt))

    return bytes(rebuilt)


def _parse_replacement(text):
    source_text, separator, target_text = text.partition("=")
    if not separator:
        raise Btx0Error("expected #RRGGBB=#RRGGBB, got {!r}".format(text))
    return hex_to_rgb555(source_text), hex_to_rgb555(target_text)


def cmd_dump(args):
    with open(args.file, "rb") as handle:
        data = handle.read()

    for i, palette in enumerate(parse_palettes(data)):
        print(
            "palette {}: {} ({} colours @ 0x{:X})".format(
                i, palette.name, len(palette.colors), palette.offset
            )
        )
        for index, value in enumerate(palette.colors):
            print("  {:3}  0x{:04X}  {}".format(index, value, rgb555_to_hex(value)))
    return 0


def cmd_add_palette(args):
    with open(args.file, "rb") as handle:
        data = handle.read()

    source = [p for p in parse_palettes(data) if p.name == args.copy_from]
    if not source:
        raise Btx0Error("no palette named {!r} to copy from".format(args.copy_from))
    colors = list(source[0].colors)

    replacements = dict(_parse_replacement(item) for item in args.replace or [])
    swapped = 0
    if replacements:
        colors, swapped = replace_colors(colors, replacements)
        if swapped == 0:
            raise Btx0Error(
                "no colour matched any --replace source in palette {!r}".format(
                    args.copy_from
                )
            )

    rebuilt = add_palette(data, args.name, colors)
    with open(args.file, "wb") as handle:
        handle.write(rebuilt)

    print(
        "added palette {!r} ({} colours, {} replaced), file {} -> {} bytes".format(
            args.name, len(colors), swapped, len(data), len(rebuilt)
        )
    )
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    dump = subparsers.add_parser("dump", help="list the palettes in a BTX0 file")
    dump.add_argument("file")
    dump.set_defaults(func=cmd_dump)

    add = subparsers.add_parser(
        "add-palette", help="append a palette, copied from an existing one"
    )
    add.add_argument("file")
    add.add_argument("--name", required=True)
    add.add_argument("--copy-from", required=True)
    add.add_argument(
        "--replace",
        action="append",
        metavar="#RRGGBB=#RRGGBB",
        help="swap every entry matching a colour, wherever it sits; repeatable",
    )
    add.set_defaults(func=cmd_add_palette)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Btx0Error as error:
        print("error: {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
