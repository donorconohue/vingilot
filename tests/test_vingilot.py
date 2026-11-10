import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARSHIP = ROOT / ".toolchain/starship"
GENERATED = ROOT / "starship/generated/vingilot.toml"


def run(args, tmp_path, **kwargs):
    locale = "en_US.UTF-8" if sys.platform == "darwin" else "C.UTF-8"
    env = {
        "PATH": os.defpath,
        "HOME": str(tmp_path),
        "ZDOTDIR": str(tmp_path),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "STARSHIP_CACHE": str(tmp_path / "cache"),
        "TERM": "xterm-256color",
        "LANG": locale,
        "LC_ALL": locale,
    }
    with subprocess.Popen(
        args,
        cwd=tmp_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
        **kwargs,
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise
        result = subprocess.CompletedProcess(args, process.returncode, stdout, stderr)
        result.check_returncode()
        return result


def python_tool(name, *args):
    return [sys.executable, str(ROOT / "tools" / name), *map(str, args)]


def test_pinned_upstream_preset_and_generated_bytes(tmp_path):
    pin = json.loads((ROOT / "toolchain.json").read_text())["starship"]
    assert run([STARSHIP, "--version"], tmp_path).stdout.splitlines()[0] == (
        f"starship {pin['version']}"
    )
    preset = tmp_path / "preset.toml"
    run([STARSHIP, "preset", "nerd-font-symbols", "-o", preset], tmp_path)
    assert hashlib.sha256(preset.read_bytes()).hexdigest() == pin["preset_sha256"]
    assert preset.read_bytes() == (ROOT / "starship/presets/nerd-font-symbols.toml").read_bytes()
    output = tmp_path / "generated.toml"
    run(python_tool("build-starship-config", "--output", output), tmp_path)
    assert output.read_bytes() == GENERATED.read_bytes()


def test_installation_writes_only_expected_user_files(tmp_path):
    run(["zsh", "-f", "-n", ROOT / "install.zsh"], tmp_path)
    run(["zsh", "-f", "-n", ROOT / "zsh/prompt_vingilot_setup"], tmp_path)
    run(["zsh", "-f", ROOT / "install.zsh", "--user"], tmp_path)
    data = tmp_path / "data"
    assert (data / "zsh/site-functions/prompt_vingilot_setup").read_bytes() == (
        ROOT / "zsh/prompt_vingilot_setup"
    ).read_bytes()
    assert (data / "vingilot/starship.toml").read_bytes() == GENERATED.read_bytes()
    assert not (tmp_path / ".zshrc").exists()


def test_native_prompt_uses_literal_directory_text_and_cleans_hooks(tmp_path):
    directory = tmp_path / "price$HOME%mark"
    directory.mkdir()
    binary = tmp_path / "starship"
    shutil.copy2(STARSHIP, binary)
    source = r"""
        setopt errexit
        fpath=("$1/zsh" $fpath)
        export STARSHIP_CONFIG="$1/starship/generated/vingilot.toml"
        VINGILOT_STARSHIP="$2"
        VINGILOT_CWD_MAX=80
        autoload -Uz promptinit
        promptinit
        prompt vingilot
        cd -- "$3"
        prompt_vingilot_precmd
        print -P -- "$RPROMPT"
        (( ${precmd_functions[(Ie)prompt_vingilot_precmd]} ))
        prompt off
        (( ! ${precmd_functions[(Ie)prompt_vingilot_precmd]:-0} ))
        [[ "$STARSHIP_CONFIG" == "$1/starship/generated/vingilot.toml" ]]
    """
    result = run(["zsh", "-f", "-c", source, "vingilot-test", ROOT, binary, directory], tmp_path)
    assert "price$HOME%mark" in result.stdout


def test_release_archive_is_reproducible(tmp_path):
    one, two = tmp_path / "one", tmp_path / "two"
    run(python_tool("build-release", "--output", one), tmp_path)
    run(python_tool("build-release", "--output", two), tmp_path)
    checksums = (one / "SHA256SUMS").read_text()
    assert checksums == (two / "SHA256SUMS").read_text()
    digest, name = checksums.split()
    artifact = (one / name).read_bytes()
    assert artifact == (two / name).read_bytes()
    assert hashlib.sha256(artifact).hexdigest() == digest
