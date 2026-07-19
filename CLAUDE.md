# CLAUDE.md

Guidance for Claude when working in this repository. 
This is a personal fork of the [pret/pokeplatinum](https://github.com/pret/pokeplatinum) decompilation of Pokémon Platinum (US).

## Project: Pokémon Platinum+

**Pokémon Platinum+** is a Pokémon Platinum romhack that keeps growing without ever moving past Platinum:

> **New content. Same era. Indefinitely.**

The project expands the original Pokémon Platinum experience while preserving its identity, atmosphere, and Nintendo DS-era constraints.

The goal is not to create a sequel, remake, or modern Pokémon game. 
The goal is to keep building on Platinum as if the game itself could continue receiving new content forever.

This may include:

* New Pokémon and forms
* New moves, abilities, items, and mechanics
* New trainers and encounters
* New areas, maps, and events
* New story content
* New graphics, animations, and visual assets
* Quality-of-life improvements
* New systems and gameplay features

The project should remain coherent with the original game's world and technical foundation.

## Project priorities

When making decisions, prioritize:

1. **The identity of Pokémon Platinum+** — additions should feel like they belong to the project.
2. **A working, observable result** — prefer changes that can be built and tested in-game.
3. **Simplicity and maintainability** — implement the smallest clear solution that solves the problem.
4. **Understanding the underlying game and hardware** — the project is also an opportunity to understand the Nintendo DS, the original game, and the decompilation.

The project is **not** intended to be an upstream contribution to **pret**, and preserving a byte-perfect matching build is not a goal once the game is intentionally modified.

## Communication style

* Be concise when explaining general programming concepts such as C syntax, pointers, control flow, or common tooling.
* Be pedagogical when explaining Nintendo DS- or decompilation-specific concepts.
* When a new NDS concept is relevant to a task, briefly explain it before using it in the implementation.

Examples of concepts that may need explanation:

* ARM9 / ARM7 and ARM / Thumb code
* The Nintendo DS memory map
* VRAM banks
* Background layers and OAM
* Overlays
* NARC archives
* The matching build
* Symbols, data layout, and addresses in the ROM
* The relationship between source code, resources, and the final ROM

Do not over-explain concepts that are already understood.

## Think before coding

Do not silently make assumptions.

Before implementing a non-trivial change:

* Identify important assumptions.
* If multiple interpretations are possible, mention them briefly.
* If something is unclear and would materially affect the implementation, ask before coding.
* If a simpler solution exists, prefer it.
* Push back when an approach is unnecessarily complex or would create long-term maintenance problems.

For simple and obvious tasks, use judgment and avoid unnecessary ceremony.

## Simplicity first

Prefer the minimum code and complexity necessary to solve the problem.

* Do not add features that were not requested.
* Do not create abstractions for single-use code.
* Do not add speculative configuration or flexibility.
* Do not introduce unnecessary error handling.
* Prefer existing project conventions and helpers.
* Do not create a parallel architecture when the existing game architecture can be extended cleanly.

The goal is not merely to make the code work, but to make the project remain understandable as Platinum+ grows.

## Make surgical changes

When modifying existing code:

* Touch only what is necessary for the requested change.
* Match the existing code style.
* Do not refactor unrelated code.
* Do not "clean up" adjacent code, comments, or formatting unless requested.
* Do not remove pre-existing dead code unless explicitly asked.

Every changed line should have a clear connection to the requested task.

If your changes create unused imports, variables, functions, or other artifacts, clean up those artifacts. 
Do not use the opportunity to clean up unrelated pre-existing code.

## Goal-driven execution

For non-trivial tasks, define a short plan and concrete success criteria before making changes.

For example:

1. Identify the relevant code or data → verify the correct subsystem is being modified.
2. Make the smallest necessary change → verify the project builds.
3. Run or inspect the result → verify the intended behavior is observable in-game.

Success criteria should be concrete whenever possible.

Examples:

* "Add a new Pokémon" → the relevant data is modified, the ROM builds, and the Pokémon appears correctly in-game.
* "Change a text string" → the correct text resource is modified and the result is visible in-game.
* "Fix a bug" → understand or reproduce the failure, implement the fix, and verify the affected behavior.
* "Modify rendering" → build and inspect the result in an emulator.

Do not claim that a change works without verifying it when verification is possible.

## Build and test workflow

This repository is based on a **matching decompilation**. 
The default build can verify that the generated ROM is byte-for-byte identical to the retail ROM.

That verification is useful for validating the decompilation, but it is fundamentally incompatible with intentional modifications to Pokémon Platinum+.

### Main commands

```bash
make rom
```

Builds the ROM for normal development and modding.

Output:

```text
build/pokeplatinum.us.nds
```

**Use this for Platinum+ development.**

---

```bash
make check
```

Builds the project and verifies that the resulting ROM matches the retail ROM byte-for-byte.

Once Platinum+ intentionally changes the game, this is expected to fail. 
A failing `make check` after an intentional gameplay, code, or data change is **not automatically a bug**.

---

```bash
make debug
```

Builds with logging and GDB debugging enabled.

See:

```text
docs/logging.md
```

### Observing changes

After modifying the game:

1. Build with `make rom`.
2. Run `build/pokeplatinum.us.nds` in a Nintendo DS emulator such as melonDS or DeSmuME.
3. Verify the intended behavior in-game.

When useful, use logging, debugging, or targeted tests to verify behavior before testing the full game.

## Repository map

* `src/` — C source code for the game. Much of it remains obfuscated or auto-named.
* `include/` — C headers.
* `res/` — source assets and data tables compiled into the ROM. Most data-level modifications begin here.
* `asm/` — remaining assembly code.
* `lib/` — separate libraries linked into the ROM.
* `generated/` — enum and constant listings generated from the sources; do not edit by hand.
* `platinum.us/` — ROM packaging metadata: filesystem layout, linker script, ROM header and checksums.
* `tools/` — build and modding tooling.
* `subprojects/` — vendored dependencies, including the NitroSDK.
* `meson/` — Meson cross/native build configuration files.
* `docs/` — project documentation.
* `build/` — generated build output. The final ROM is placed here.
* `INSTALL.md` — setup instructions.
* `CONTRIBUTING.md` — upstream contribution guidelines.

The build is driven by Meson (`meson.build`); the top-level `Makefile` is a thin wrapper around it.

## Git Workflow

Git history is managed manually by the developer.

> **Never commit automatically.**

When asked for a commit message:

* Follow the repository's existing commit conventions.
* Keep the message short, precise, and focused on the actual change.
* Inspect recent commits if the convention is unclear.
* Provide the message without creating the commit.

## General rules

* Search the repository before assuming where functionality is implemented.
* Understand the existing code and data flow before modifying it.
* Prefer extending existing systems over creating parallel implementations.
* Prefer existing project conventions and helpers over inventing new ones.
* Keep changes focused and easy to review.
* Do not optimize prematurely.
* Do not introduce large architectural changes for small problems.
* When implementing a new feature, consider how it fits into the long-term growth of Platinum+.
* Preserve the project's identity: new content should expand Pokémon Platinum, not turn it into a different generation or a modern remake.

The primary goal is to build a Pokémon Platinum experience that can **keep growing indefinitely while remaining Pokémon Platinum**.
