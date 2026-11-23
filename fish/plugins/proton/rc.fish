if command -q proton
    function proton
        set -l cd_prefix
        set -l prefix default
        set -l args
        while set -q argv[1]
            switch $argv[1]
                case --cd
                    set cd_prefix 1
                    set -e argv[1]
                case -p --prefix
                    set -a args $argv[1]
                    set -e argv[1]
                    set prefix $argv[1]
                    set -a args $prefix
                    set -e argv[1]
                case --
                    set -a args $argv
                    set argv
                case '*'
                    set -a args $argv[1]
                    set -e argv[1]
            end
        end
        if test -n "$cd_prefix"
            cd "$(command proton --prefix $prefix)/pfx/drive_c"
        end
        command proton $args
    end
end
