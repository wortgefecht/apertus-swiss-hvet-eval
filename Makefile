.PHONY: run smoke api-smoke

run:
	$(MAKE) -C track_1b run

smoke:
	$(MAKE) -C track_1b smoke

api-smoke:
	$(MAKE) -C track_1b api-smoke
