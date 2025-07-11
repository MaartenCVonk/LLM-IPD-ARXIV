#!/bin/bash
# Script to properly set up this repository as a fork with upstream tracking

echo "Setting up LLM-IPD-ARXIV as a proper fork..."

# Add upstream remote
echo "Adding upstream remote..."
git remote add upstream https://github.com/kennethpayne01/LLM-IPD-ARXIV.git 2>/dev/null || echo "Upstream already exists"

# Rename origin to fork (if you've forked on GitHub)
echo "Current remotes:"
git remote -v

echo ""
echo "To complete the fork setup:"
echo "1. Fork the original repo on GitHub: https://github.com/kennethpayne01/LLM-IPD-ARXIV"
echo "2. Add your fork as origin: git remote set-url origin https://github.com/YOUR_USERNAME/LLM-IPD-ARXIV.git"
echo "3. Push your changes: git push -u origin main"
echo ""
echo "To sync with upstream:"
echo "  git fetch upstream"
echo "  git merge upstream/main"