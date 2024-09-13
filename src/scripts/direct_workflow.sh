END=50

for i in $(seq 1 $END); do
  python -m src.workflow.direct --index $i
done