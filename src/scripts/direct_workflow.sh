END=10

for i in $(seq 1 $END); do
  python -m src.workflow.direct --index $i
done