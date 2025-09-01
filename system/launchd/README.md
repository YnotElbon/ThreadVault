# Launchd Autostart (macOS)

- Bridge agent: `system/launchd/com.threadvault.bridge.plist`
- Daily maintenance: `system/launchd/com.threadvault.maintenance.plist`

Install commands (from your user shell):

```
mkdir -p ~/Library/LaunchAgents
cp system/launchd/com.threadvault.*.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.threadvault.bridge.plist 2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.threadvault.maintenance.plist 2>/dev/null || true
launchctl load -w ~/Library/LaunchAgents/com.threadvault.bridge.plist
launchctl load -w ~/Library/LaunchAgents/com.threadvault.maintenance.plist
```

- Logs: `ThreadVault/system/*_launchd.*.log`
- Token: `ThreadVault/system/bridge_token.txt` (rotate by editing file and restarting agent)

To stop:
```
launchctl unload ~/Library/LaunchAgents/com.threadvault.bridge.plist
launchctl unload ~/Library/LaunchAgents/com.threadvault.maintenance.plist
```
