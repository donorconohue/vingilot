#!/usr/bin/env zsh

emulate -L zsh
setopt errexit nounset pipefail

usage() {
    cat <<'HELP'
Usage:
  ./install.zsh [--user | --system]

Options:
  --user      Install for the current user.
              This is the default.

  --system    Install under /usr/local.
              Requires sufficient privileges.

  -h, --help  Show this help.
HELP
}

mode=user

while (( $# )); do
    case "$1" in
        --user)
            mode=user
            ;;
        --system)
            mode=system
            ;;
        -h|--help)
            usage
            return 0
            ;;
        *)
            print -u2 -- "vingilot: unknown option: $1"
            usage >&2
            return 2
            ;;
    esac
    shift
done

root=${0:A:h}

prompt_source="$root/zsh/prompt_vingilot_setup"
starship_source="$root/starship/generated/vingilot.toml"

if [[ ! -r "$prompt_source" ]]; then
    print -u2 -- "vingilot: missing prompt theme: $prompt_source"
    return 1
fi

if [[ ! -r "$starship_source" ]]; then
    print -u2 -- "vingilot: missing generated Starship config"
    print -u2 -- "vingilot: run 'make check' first"
    return 1
fi

case "$mode" in
    user)
        data_home=${XDG_DATA_HOME:-$HOME/.local/share}
        zsh_dir="$data_home/zsh/site-functions"
        vingilot_dir="$data_home/vingilot"
        ;;

    system)
        zsh_dir="/usr/local/share/zsh/site-functions"
        vingilot_dir="/usr/local/share/vingilot"
        ;;
esac

mkdir -p "$zsh_dir" "$vingilot_dir"

install -m 0644 \
    "$prompt_source" \
    "$zsh_dir/prompt_vingilot_setup"

install -m 0644 \
    "$starship_source" \
    "$vingilot_dir/starship.toml"

print -- "Vingilot installed:"
print -- "  prompt:   $zsh_dir/prompt_vingilot_setup"
print -- "  starship: $vingilot_dir/starship.toml"
print
print -- "Activate from zsh with:"
print

if [[ "$mode" == user ]]; then
    print -- '  fpath=("${XDG_DATA_HOME:-$HOME/.local/share}/zsh/site-functions" $fpath)'
fi

print -- "  autoload -Uz promptinit"
print -- "  promptinit"
print -- "  prompt vingilot"
