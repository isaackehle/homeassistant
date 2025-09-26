# SFTP Configuration

## 🔐 Step 1: Generate an Ed25519 SSH Key Pair

Run this command in your terminal:

```shell
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519
```

- -t ed25519: Specifies the key type (Ed25519 is modern and secure).
- -C: Adds a comment (usually your email). This could also be your hostname if you are using more than one computer.
- -f: Specifies the filename/location for the key.

You'll be prompted to:

1. Enter a passphrase (recommended for security).
2. Confirm the passphrase.

This creates two files:

- `~/.ssh/id_ed25519` (private key)
- `~/.ssh/id_ed25519.pub` (public key)

## 📌 Step 2: Add SSH Key to SSH Agent (Optional but Recommended)

Start the SSH agent and add your key:

```shell
eval "$(ssh-agent -s)" 
ssh-add ~/.ssh/id_ed25519
```

This avoids typing your passphrase every time.

## 🚀 Step 3: Add an SSH Alias

You can create an alias to simplify connecting to a server.

### Option A: SSH Config Alias

Edit your SSH config file:

```shell
nano ~/.ssh/config
```

Add something like:

```shell
Host ha
    HostName homeassistant.local
    User root
    IdentityFile ~/.ssh/id_ed25519
    Port 22
```

Now you can connect using:

```shell
ssh ha
```

This is an SSH "alias" via config — clean and powerful.

### Option B: Shell Alias (Bash/Zsh)

Add a shell alias to your shell profile.

Edit your shell config:

```shell
nano ~/.bashrc    # or ~/.zshrc if using zsh
```

Add:

```shell
alias ssh-myserver='ssh -i ~/.ssh/id_ed25519 yourusername@example.com'
```

Reload the shell:

```shell
source ~/.bashrc   # or source ~/.zshrc
```

Now use:

```shell
ssh-myserver
```

## 🗄️ Step 4: Configure SSH Server

```json
{
    "name": "Home assistant",
    "host": "homeassistant.local",
    "protocol": "sftp",
    "port": 1022,
    "username": "root",
    "uploadOnSave": true,
    "useTempFile": true,
    "openSsh": true
}
```