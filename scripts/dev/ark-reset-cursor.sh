#!/bin/zsh
echo "🧹 Purge des caches Cursor / Pyright..."
rm -rf ~/.cache/pyright
rm -rf ~/Library/Application\ Support/Code/User/workspaceStorage
rm -rf ~/Library/Application\ Support/Code/User/globalStorage/ms-python.*
echo "✅ Caches supprimés. Relance Cursor."
