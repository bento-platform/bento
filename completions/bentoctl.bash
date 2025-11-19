# Bash completion script for bentoctl
# Place this file in /etc/bash_completion.d/ or ~/.local/share/bash-completion/completions/

_bentoctl_completions() {
    local cur prev words cword
    _init_completion || return

    local commands="init-dirs init-auth init-certs init-docker init-web init-all init-config init-cbioportal pg-dump pg-load convert-pheno conv run start up stop down restart clean work-on dev develop local prebuilt pre-built prod mode state status pull shell sh run-as-shell logs compose-config"

    # All services (for most commands)
    local all_services="all aggregation auth auth-db authz authz-db beacon cbioportal drs drop-box event-relay gateway gohan gohan-api gohan-elasticsearch katsu katsu-db notification public redis reference reference-db service-registry web wes"

    # Services that can be worked on (have repositories)
    local workable_services="aggregation authz beacon drs drop-box event-relay gateway gohan-api katsu notification public reference service-registry web wes"

    if [[ ${cword} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
        return
    fi

    case "${prev}" in
        run|start|up|stop|down|restart|clean|logs|pull|mode|state|status)
            COMPREPLY=($(compgen -W "${all_services}" -- "${cur}"))
            ;;
        work-on|dev|develop|local)
            COMPREPLY=($(compgen -W "${workable_services}" -- "${cur}"))
            ;;
        prebuilt|pre-built|prod)
            COMPREPLY=($(compgen -W "${all_services}" -- "${cur}"))
            ;;
        shell|sh|run-as-shell)
            COMPREPLY=($(compgen -W "${all_services}" -- "${cur}"))
            ;;
        init-web)
            COMPREPLY=($(compgen -W "public private" -- "${cur}"))
            ;;
        init-config)
            COMPREPLY=($(compgen -W "katsu beacon beacon-network" -- "${cur}"))
            ;;
        pg-dump|pg-load)
            _filedir -d
            ;;
        convert-pheno|conv)
            _filedir
            ;;
        -s|--shell)
            COMPREPLY=($(compgen -W "/bin/bash /bin/sh" -- "${cur}"))
            ;;
        *)
            # Handle flags
            case "${words[1]}" in
                run|start|up|restart)
                    COMPREPLY=($(compgen -W "-p --pull" -- "${cur}"))
                    ;;
                logs)
                    COMPREPLY=($(compgen -W "-f --follow" -- "${cur}"))
                    ;;
                init-certs|init-web|init-config)
                    COMPREPLY=($(compgen -W "-f --force" -- "${cur}"))
                    ;;
                shell|sh|run-as-shell)
                    COMPREPLY=($(compgen -W "-s --shell" -- "${cur}"))
                    ;;
                compose-config)
                    COMPREPLY=($(compgen -W "--services" -- "${cur}"))
                    ;;
            esac
            ;;
    esac
}

complete -F _bentoctl_completions bentoctl
