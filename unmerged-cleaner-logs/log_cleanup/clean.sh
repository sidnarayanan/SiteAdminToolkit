for m in $(seq 1 12); do
        for d in $(seq 1 31); do 
                echo $m $d 
                eos rm -r store/unmerged/logs/prod/2017/$m/$d
        done
        eos rm -r store/unmerged/logs/prod/2017/$m
done
eos rm -r store/unmerged/logs/prod/2017
