#!/usr/bin/env bash

set -o nounset
set -o pipefail

export PS4="+${BASH_SOURCE[0]}:${LINENO}: "

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename ${__file} .bash)"
__root="$(cd "$(dirname "${__dir}")" && pwd)"


function __usage ()
{
    cat <<-USAGE_HELP
Usage: ${__base} [flags]
    Options:
        -h|--help: Display this help
        -v|--verbose: Increase verbosity
        -d|--debug: Enable debug mode
USAGE_HELP
}


function __parse_args() {
    _debug=false
    _verbose=0
    while true; do
        case ${1:-""} in
            -h|-\?|--help)
                __usage
                return 1
                ;;
            -d|--debug)
                _debug=true
                ;;
            -v|--verbose)
                _verbose=$((_verbose + 1)) # Each -v argument adds 1 to verbosity.
                ;;
            --)              # End of all options.
                shift
                break
                ;;
            -?*)
                printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
                return 1
                ;;
            *)               # Default case: If no more options then break out of the loop.
                break
        esac

        shift
    done
}


function _activate_common() {
    return
}


function _deactivate_common() {
    unset JAVA_HOME
}


function _active_linux_specific() {
    source "${__dir}/java.sh"
}


function _deactive_linux_specific() {
    return
}


function deactivate () {
    # reset old environment variables

    # ! [ -z ${VAR+_} ] returns true if VAR is declared at all
    if ! [ -z "${_OLD_VIRTUAL_PATH+_}" ] ; then
        export PATH="${_OLD_VIRTUAL_PATH}"
        unset _OLD_VIRTUAL_PATH
    fi

    if ! [ -z "${_OLD_VIRTUAL_LD_LIBRARY_PATH+_}" ] ; then
        export LD_LIBRARY_PATH="${_OLD_VIRTUAL_LD_LIBRARY_PATH}"
        unset _OLD_VIRTUAL_LD_LIBRARY_PATH
    fi

    _deactivate_common
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        _deactive_linux_specific
    fi

    unset VIRTUAL_ENV

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "${BASH-}" ] || [ -n "${ZSH_VERSION-}" ] ; then
        hash -r 2>/dev/null
    fi

    if ! [ -z "${_OLD_VIRTUAL_PS1+_}" ] ; then
        export PS1="${_OLD_VIRTUAL_PS1}"
        unset _OLD_VIRTUAL_PS1
    fi

    if [ ! "${1-}" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate
    fi
}


function activate() {
    export VIRTUAL_ENV="__VIRTUAL_ENV__"

    _OLD_VIRTUAL_PS1="${PS1-}"
    export PS1="($(basename "${VIRTUAL_ENV}")) ${PS1-}"

    _OLD_VIRTUAL_PATH="${PATH:-}"
    _OLD_VIRTUAL_LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}"

    _activate_common
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        _active_linux_specific
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "${BASH-}" ] || [ -n "${ZSH_VERSION-}" ] ; then
        hash -r 2>/dev/null
    fi
}


function __main () {
    __parse_args $@ || return

    if [[ (! -z ${_debug+1}) && "${_debug}" == "true" ]]; then
        set -o xtrace # on
    fi

    # unset irrelevant variables
    deactivate nondestructive

    # activate new environment
    activate

    if [[ "${_debug}" == "true" ]]; then
        set +o xtrace # off
    fi
}

__main $@

set +o nounset
set +o pipefail