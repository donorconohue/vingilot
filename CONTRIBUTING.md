# Contributing

Keep changes focused on native zsh layout, Starship context and reproducible configuration. Include the shell/Starship versions and terminal/font in rendering bug reports. Use a disposable home directory when testing installs or theme activation.

1. Run `uv sync --locked` and `uv run --locked python tools/prepare-starship`.
2. Change `zsh/prompt_vingilot_setup` or the ASCII TOML template, as appropriate.
3. Regenerate with `make build` and run `make check`. Commit the generated TOML alongside its source changes.

To update the upstream preset, review the new Starship release, pin its platform archive hashes in `toolchain.json`, then regenerate the preset with the verified binary's `preset nerd-font-symbols` command. Record its digest and preserve the applicable upstream notice. Review the generated config and test before accepting a version change. The artifact hashes verify selected bytes; they do not replace upstream provenance review.

## Release

Use the version in `pyproject.toml`, update `CHANGELOG.md`, and merge the reviewed source after CI. Create the corresponding `v<version>` tag on that exact `main` commit when ready to publish. The tag workflow checks the version and ancestry, repeats validation, packages the files, attests their build and attaches the archive/checksums to a draft before publishing. Enable immutable releases before the first public release. Avoid replacing a published tag or archive; issue a new version for corrections.

`make release` builds local review artifacts without touching GitHub. Normal PR validation has no publish credentials. The release workflow uses its scoped GitHub token and workload identity, with no stored PAT or signing key.
