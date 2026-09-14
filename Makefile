.PHONY: demo-replay site

demo-replay:
	@PYTHONPATH=src python3 -m nightbasis.desk_replay --all \
		--transcript-dir reports/replay-transcripts \
		--reason-matrix reports/reason-matrix.md

site:
	@cd web && npm install && npm run dev
