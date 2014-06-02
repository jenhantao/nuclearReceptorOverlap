#bash run.sh $actualDir ~/test_actual_0/ true true true 2>~/test_actual_0/log.txt
path=$1
thresholds=( 0 25 50 75 90 95 99 )
for i in "${thresholds[@]}"
do
	echo "bash run.sh $actualDir ~/test_actual_${i} false false true $i 2>~/test_actual_${i}/error.txt >test_actual_${i}/log.txt"
	bash run.sh $actualDir ~/test_actual_${i} false false true $i 2>~/test_actual_${i}/error.txt > ~/test_actual_${i}/log.txt
done
