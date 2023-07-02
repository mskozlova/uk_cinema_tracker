for log in *.log; do tail -n 100000 $log | sponge $log; done

