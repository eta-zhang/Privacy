bash src/scripts/privacy_workflow.sh
bash src/scripts/direct_workflow.sh
python -m src.evaluate --mode privacy
python -m src.evaluate --mode direct