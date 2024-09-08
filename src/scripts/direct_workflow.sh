END=100

for i in $(seq 32 $END); do
  python -m src.workflow.direct --index $i
done