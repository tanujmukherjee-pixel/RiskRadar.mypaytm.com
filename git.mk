# Git sync targets
.PHONY: check-remotes fetch-all sync-bitbucket-to-github sync-github-to-bitbucket sync-all show-branches stash-changes unstash-changes

# Git sync variables
GITHUB_REMOTE := github
BITBUCKET_REMOTE := bitbucket
DRY_RUN ?= false
STASH_NAME := "git-sync-temp-stash-$(shell date +%s)"

check-remotes:
	@echo "Checking remotes..."
	@if ! git remote | grep -q "$(BITBUCKET_REMOTE)"; then \
		echo "Error: '$(BITBUCKET_REMOTE)' remote not found"; \
		exit 1; \
	fi
	@if ! git remote | grep -q "$(GITHUB_REMOTE)"; then \
		echo "Error: '$(GITHUB_REMOTE)' remote not found"; \
		exit 1; \
	fi

stash-changes:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Stashing uncommitted changes..."; \
		if git stash push -m $(STASH_NAME); then \
			echo "Changes stashed successfully."; \
		else \
			echo "Error: Failed to stash changes."; \
			exit 1; \
		fi \
	fi

unstash-changes:
	@if git stash list | grep -q $(STASH_NAME); then \
		echo "Restoring stashed changes..."; \
		stash_ref=$$(git stash list | grep $(STASH_NAME) | cut -d: -f1); \
		if git stash pop "$$stash_ref" > /dev/null 2>&1; then \
			echo "Changes restored successfully."; \
		else \
			echo "Warning: Failed to restore changes automatically."; \
			echo "Your changes are still in the stash. To restore manually, run:"; \
			echo "  git stash list   # find your stash with message $(STASH_NAME)"; \
			echo "  git stash pop    # apply and remove the stash"; \
		fi \
	fi

fetch-all: check-remotes
	@echo "Fetching all branches..."
	@git fetch --all --progress
	@echo "Done fetching."

sync-bitbucket-to-github: check-remotes stash-changes
	@echo "Syncing Bitbucket branches to GitHub..."
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	branches=$$(git branch -r | grep "^[[:space:]]*$(BITBUCKET_REMOTE)/" | grep -v "$(BITBUCKET_REMOTE)/HEAD" | sed "s|[[:space:]]*$(BITBUCKET_REMOTE)/||"); \
	total_branches=$$(echo "$$branches" | wc -l | tr -d ' '); \
	current=0; \
	for branch in $$branches; do \
		current=$$((current + 1)); \
		echo "[$$current/$$total_branches] Processing $$branch..."; \
		if [ "$(DRY_RUN)" = "true" ]; then \
			echo "  Would sync $$branch to $(GITHUB_REMOTE)"; \
		else \
			if git checkout -B "$$branch" "$(BITBUCKET_REMOTE)/$$branch" 2>/dev/null; then \
				git push $(GITHUB_REMOTE) "$$branch" || echo "Warning: Failed to push $$branch"; \
			else \
				echo "Warning: Failed to checkout $$branch"; \
			fi; \
		fi; \
	done; \
	if [ "$(DRY_RUN)" = "false" ]; then \
		git checkout "$$current_branch" 2>/dev/null || echo "Warning: Failed to restore original branch"; \
	fi
	@echo "Sync complete."
	@$(MAKE) -f git.mk unstash-changes

sync-github-to-bitbucket: check-remotes stash-changes
	@echo "Syncing GitHub branches to Bitbucket..."
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	branches=$$(git branch -r | grep "^[[:space:]]*$(GITHUB_REMOTE)/" | grep -v "$(GITHUB_REMOTE)/HEAD" | sed "s|[[:space:]]*$(GITHUB_REMOTE)/||"); \
	total_branches=$$(echo "$$branches" | wc -l | tr -d ' '); \
	current=0; \
	for branch in $$branches; do \
		current=$$((current + 1)); \
		echo "[$$current/$$total_branches] Processing $$branch..."; \
		if [ "$(DRY_RUN)" = "true" ]; then \
			echo "  Would sync $$branch to $(BITBUCKET_REMOTE)"; \
		else \
			if git checkout -B "$$branch" "$(GITHUB_REMOTE)/$$branch" 2>/dev/null; then \
				git push $(BITBUCKET_REMOTE) "$$branch" || echo "Warning: Failed to push $$branch"; \
			else \
				echo "Warning: Failed to checkout $$branch"; \
			fi; \
		fi; \
	done; \
	if [ "$(DRY_RUN)" = "false" ]; then \
		git checkout "$$current_branch" 2>/dev/null || echo "Warning: Failed to restore original branch"; \
	fi
	@echo "Sync complete."
	@$(MAKE) -f git.mk unstash-changes

sync-all: fetch-all sync-bitbucket-to-github sync-github-to-bitbucket
	@echo "All branches from Bitbucket and GitHub are now synchronized."

show-branches: check-remotes
	@echo "Showing remote branches..."
	@echo "\nRemote repositories:"
	@git remote -v | cat
	@echo "\nBitbucket branches:"
	@git branch -r | grep "$(BITBUCKET_REMOTE)/" | sed "s|[[:space:]]*$(BITBUCKET_REMOTE)/||" | cat
	@echo "\nGitHub branches:"
	@git branch -r | grep "$(GITHUB_REMOTE)/" | sed "s|[[:space:]]*$(GITHUB_REMOTE)/||" | cat

# Git sync help
git-help:
	@echo "Git Sync Commands:"
	@echo "  make -f git.mk fetch-all         - Fetch all branches from both remotes"
	@echo "  make -f git.mk sync-bitbucket-to-github  - Sync Bitbucket branches to GitHub"
	@echo "  make -f git.mk sync-github-to-bitbucket  - Sync GitHub branches to Bitbucket"
	@echo "  make -f git.mk sync-all          - Sync all branches between remotes"
	@echo "  make -f git.mk show-branches     - Show all remote branches"
	@echo ""
	@echo "Options:"
	@echo "  DRY_RUN=true          - Show what would be done without doing it"
	@echo ""
	@echo "Note: Uncommitted changes will be automatically stashed and restored during sync operations." 