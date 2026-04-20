SHELL := /bin/bash

ARCHIVE_DIR ?= .repo-archive

.PHONY: archive-repo clean-archives

archive-repo:
	@set -euo pipefail; \
	ts="$$(date +"%Y%m%d-%H%M%S")"; \
	out_dir="$(ARCHIVE_DIR)/snapshot-$$ts"; \
	mkdir -p "$$out_dir"; \
	echo "Creating repository snapshot in $$out_dir"; \
	{ \
		echo "Snapshot timestamp: $$ts"; \
		echo "Repository: $$(basename "$$PWD")"; \
		echo "Absolute path: $$PWD"; \
		echo "Head commit: $$(git rev-parse HEAD 2>/dev/null || echo 'n/a')"; \
		echo "Current branch: $$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'n/a')"; \
	} > "$$out_dir/summary.txt"; \
	git remote -v > "$$out_dir/git_remote.txt" || true; \
	git status --short --branch > "$$out_dir/git_status.txt" || true; \
	git branch -vv > "$$out_dir/git_branches.txt" || true; \
	git log --decorate --oneline -n 50 > "$$out_dir/git_log_last_50.txt" || true; \
	git show --stat --oneline --no-patch HEAD > "$$out_dir/git_head.txt" || true; \
	git ls-files > "$$out_dir/tracked_files.txt" || true; \
	git ls-files --others --exclude-standard > "$$out_dir/untracked_files.txt" || true; \
	find . -type f -not -path './.git/*' -not -path './$(ARCHIVE_DIR)/*' | sort > "$$out_dir/worktree_files.txt"; \
	git diff > "$$out_dir/diff_unstaged.patch" || true; \
	git diff --staged > "$$out_dir/diff_staged.patch" || true; \
	git diff HEAD > "$$out_dir/diff_vs_head.patch" || true; \
	git bundle create "$$out_dir/repo.bundle" --all > /dev/null 2> "$$out_dir/repo_bundle.stderr" || true; \
		COPYFILE_DISABLE=1 tar -czf "$$out_dir/worktree.tar.gz" \
			--exclude='./.git' \
			--exclude='./$(ARCHIVE_DIR)' \
			--exclude='./.repo-archive' \
			--exclude='./._*' \
			--exclude='./.DS_Store' \
			--exclude='./.AppleDouble' \
			--exclude='._*' \
			--exclude='.DS_Store' \
			--exclude='.AppleDouble' \
			. ; \
		COPYFILE_DISABLE=1 tar -czf "$$out_dir.tar.gz" \
			--exclude='._*' \
			--exclude='.DS_Store' \
			--exclude='.AppleDouble' \
			--exclude='.repo-archive' \
			-C "$(ARCHIVE_DIR)" "snapshot-$$ts"; \
	echo "Done."; \
	echo "Folder snapshot: $$out_dir"; \
	echo "Portable archive: $$out_dir.tar.gz"

clean-archives:
	rm -rf "$(ARCHIVE_DIR)"
