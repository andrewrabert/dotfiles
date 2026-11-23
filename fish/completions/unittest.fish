function __unittest_tests
    set -l cur (commandline -ct)
    set -l results
    if test -n "$cur"
        set results (unittest-findtests --prefix $cur 2>/dev/null)
        if test (count $results) -eq 1
            set results (unittest-findtests --prefix $results[1] 2>/dev/null)
        end
    else
        set results (unittest-findtests 2>/dev/null)
    end
    printf '%s\n' $results
end

complete -c unittest -f

complete -c unittest -s h -l help -d 'show help message and exit'
complete -c unittest -s v -l verbose -d 'verbose output'
complete -c unittest -s q -l quiet -d 'quiet output'
complete -c unittest -l locals -d 'show local variables in tracebacks'
complete -c unittest -l durations -x -d 'show N slowest test cases'
complete -c unittest -s f -l failfast -d 'stop on first fail or error'
complete -c unittest -s c -l catch -d 'catch Ctrl-C and display results so far'
complete -c unittest -s b -l buffer -d 'buffer stdout and stderr during tests'
complete -c unittest -s k -x -d 'only run tests matching substring'

set -l discover '__fish_seen_subcommand_from discover'
complete -c unittest -n $discover -s s -l start-directory -x -a '(__fish_complete_directories)' -d 'directory to start discovery'
complete -c unittest -n $discover -s p -l pattern -x -d 'pattern to match tests'
complete -c unittest -n $discover -s t -l top-level-directory -x -a '(__fish_complete_directories)' -d 'top level directory of project'

complete -c unittest -n __fish_use_subcommand -a discover -d 'test discovery mode'
complete -c unittest -n "not $discover" -a '(__unittest_tests)'
