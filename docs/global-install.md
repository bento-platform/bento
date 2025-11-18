# Global Installation of bentoctl

This guide explains how to install `bentoctl` so it can be run from any directory with shell autocompletions.

## Prerequisites

- Python 3.7+
- A Bento installation at `/path/to/bento`
- Virtual environment with dependencies installed

## Installation Steps

### 1. Install Python Dependencies

```bash
cd /path/to/bento
source env/bin/activate
pip install -r requirements.txt
```

### 2. Create Global Symlink

Choose one of the following locations:

**User-local (recommended, no sudo required):**
```bash
mkdir -p ~/.local/bin
ln -sf /path/to/bento/bin/bentoctl ~/.local/bin/bentoctl
```

**System-wide:**
```bash
sudo ln -sf /path/to/bento/bin/bentoctl /usr/local/bin/bentoctl
```

### 3. Ensure PATH is Set

Add to your shell configuration file (`~/.zshrc` or `~/.bashrc`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 4. Set Up Shell Completions

#### Zsh (with argcomplete - recommended)

Add to `~/.zshrc`:

```zsh
# bentoctl completions
autoload -U bashcompinit && bashcompinit
eval "$(register-python-argcomplete bentoctl)"
```

#### Zsh (with static completions - alternative)

Add to `~/.zshrc`:

```zsh
# Add completions directory to fpath
fpath=(/path/to/bento/completions $fpath)
autoload -Uz compinit && compinit
```

#### Bash

Add to `~/.bashrc`:

```bash
eval "$(register-python-argcomplete bentoctl)"
```

### 5. Reload Shell

```bash
source ~/.zshrc  # or ~/.bashrc
```

## Usage

Once installed, you can run `bentoctl` from any directory:

```bash
# Run from anywhere
bentoctl run all
bentoctl logs katsu -f
bentoctl mode

# Tab completion works for commands and services
bentoctl <TAB>        # Shows all commands
bentoctl run <TAB>    # Shows all services
bentoctl logs -<TAB>  # Shows flags
```

## Multiple Installations

If you have multiple Bento installations (e.g., dev and staging), you can set `BENTO_HOME` to switch between them:

```bash
# Use a specific installation
BENTO_HOME=/path/to/staging bentoctl run all

# Or create aliases
alias bentoctl-dev='BENTO_HOME=/path/to/dev bentoctl'
alias bentoctl-staging='BENTO_HOME=/path/to/staging bentoctl'
```

## Troubleshooting

### Command not found

Ensure `~/.local/bin` is in your PATH:
```bash
echo $PATH | grep -q ".local/bin" && echo "OK" || echo "Add ~/.local/bin to PATH"
```

### Completions not working

1. Verify argcomplete is installed:
   ```bash
   pip show argcomplete
   ```

2. For zsh, ensure bashcompinit is loaded before the eval command.

3. Try regenerating completions:
   ```bash
   source ~/.zshrc
   ```

### Wrong Bento directory

The wrapper script auto-detects `BENTO_HOME` from the symlink location. To override:
```bash
export BENTO_HOME=/path/to/your/bento
```
