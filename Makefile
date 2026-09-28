.PHONY: build clean default test

SHELL:=/bin/bash

ifdef VERBOSE
  Q :=
else
  Q := @
endif


clean:
	$(Q)rm -rf ./build ./dist ./python/bikkuri.egg-info
	$(Q)find . -name __pycache__ -exec rm -rf {} \;
	@echo "--- Deleted __pycache__ and build and dist dirs"



changelog.latest.md:
	$(Q)( \
		declare TAGS=(`git tag`); \
		for ((i=$${#TAGS[@]};i>=0;i--)); do \
			if [ $$i -eq 0 ]; then \
				echo -e "Version $${TAGS[$$i]}" >> changelog.latest.md; \
				git log $${TAGS[$$i]} --no-merges --format="  * %h %s"  >> changelog.latest.md; \
			elif [ $$i -eq $${#TAGS[@]} ] && [ $$(git log $${TAGS[$$i-1]}..HEAD --oneline | wc -l) -ne 0 ]; then \
				echo -e "Version $${TAGS[$$i-1]}-$$(git log -n 1 --format='%h')" >> changelog.latest.md; \
				git log $${TAGS[$$i-1]}..HEAD --no-merges --format="  * %h %s"  >> changelog.latest.md; \
			elif [ $$i -lt $${#TAGS[@]} ]; then \
				echo -e "Version $${TAGS[$$i]}" >> changelog.latest.md; \
				git log $${TAGS[$$i-1]}..$${TAGS[$$i]} --no-merges --format="  * %h %s"  >> changelog.latest.md; \
				break; \
			fi; \
		done \
	)

test:
	$(Q)python -m unittest tests/*.py
