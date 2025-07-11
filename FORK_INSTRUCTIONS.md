# How to Set Up This Repository as a GitHub Fork

This repository extends the original [LLM-IPD-ARXIV](https://github.com/kennethpayne01/LLM-IPD-ARXIV) with significant new features. Here's how to properly set it up as a fork while preserving our extensions.

## Step 1: Fork on GitHub

1. Go to https://github.com/kennethpayne01/LLM-IPD-ARXIV
2. Click the "Fork" button in the top right
3. This creates your own copy under your GitHub account

## Step 2: Update Your Local Repository

```bash
# Add upstream remote (original repository)
git remote add upstream https://github.com/kennethpayne01/LLM-IPD-ARXIV.git

# Change origin to point to your fork
git remote set-url origin https://github.com/YOUR_USERNAME/LLM-IPD-ARXIV.git

# Verify remotes
git remote -v
# Should show:
# origin    https://github.com/YOUR_USERNAME/LLM-IPD-ARXIV.git (fetch)
# origin    https://github.com/YOUR_USERNAME/LLM-IPD-ARXIV.git (push)
# upstream  https://github.com/kennethpayne01/LLM-IPD-ARXIV.git (fetch)
# upstream  https://github.com/kennethpayne01/LLM-IPD-ARXIV.git (push)
```

## Step 3: Create a Branch for Our Extensions

```bash
# Create and switch to extensions branch
git checkout -b extended-framework

# Stage all our new files
git add ipd_suite/
git add run_experiments.py
git add live_monitor.py
git add simple_monitor.py
git add quick_status.py
git add README_EXTENDED.md
git add CHANGELOG.md
git add EXPERIMENTAL_DESIGN_COMPARISON.md
git add .github/

# Commit our extensions
git commit -m "Add temperature variation analysis and adaptive strategies

- Implement systematic temperature testing (0.2, 0.7, 1.2)
- Add Mistral Large support
- Create new behavioral strategies (ForgivingGrimTrigger, Detective, SoftGrudger)
- Implement adaptive learning strategies (Q-Learning, Thompson Sampling, Gradient Meta-Learning)
- Add real-time monitoring system
- Create modular ipd_suite package
- Document methodology and findings"

# Push to your fork
git push -u origin extended-framework
```

## Step 4: Keep Your Fork Updated

```bash
# Fetch updates from upstream
git fetch upstream

# Merge upstream changes into your main branch
git checkout main
git merge upstream/main

# Rebase your extensions on top of updates
git checkout extended-framework
git rebase main
```

## Step 5: Share Your Extensions

1. Go to your fork on GitHub
2. Click "Pull requests" → "New pull request"
3. Set base repository to original and compare to your extended-framework
4. Describe your extensions in the PR description

## Alternative: Standalone Repository

If you prefer to maintain this as a separate project:

```bash
# Remove original remote
git remote remove origin

# Add your new repository
git remote add origin https://github.com/YOUR_USERNAME/LLM-IPD-Extended.git

# Update README to clarify relationship
# Add prominent attribution to original work
```

## File Structure

```
Our Extensions:
├── ipd_suite/              # New modular package
├── run_experiments.py      # Enhanced experiment runner
├── *_monitor.py           # Progress monitoring tools
├── README_EXTENDED.md     # Our documentation
├── CHANGELOG.md           # Change tracking
└── .github/workflows/     # CI/CD

Original Files (modified):
├── evolutionary_PD_expanded.py
└── requirements.txt

Original Files (unchanged):
├── LICENSE
└── [other original files]
```

## Attribution

Always maintain clear attribution to the original work:
- Keep original LICENSE file
- Reference original paper and repository in README
- Use clear commit messages indicating extensions vs modifications