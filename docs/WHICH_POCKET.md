# Two products. Not two modes.

Stop thinking of these as faces of one app. They are separate.

| | **POCKET Owner** | **POCKET for Users** |
|--|------------------|----------------------|
| Who | You, this PC | Customers |
| Port | **8787** | **8788** |
| URL | `http://127.0.0.1:8787/desk` | `http://127.0.0.1:8788/desk` |
| Shortcut | **POCKET Owner** | **POCKET for Users** |
| Electron | `POCKET_CLIENT_ROLE=operator` | `POCKET_CLIENT_ROLE=user` |
| Profile | `%APPDATA%\POCKET-Owner` | `%APPDATA%\POCKET-User` |
| Files | This machine | `~/.pocket/tenants/<user>/` |
| Chrome | Gold · OWNER | Green · USERS |

They do **not** share a window, a port, or a login.

Do not tunnel `:8787` to the customer hostname. That is still your laptop.

## Launch

```powershell
# Yours
.\scripts\Open-POCKET-Owner.cmd

# What users get (starts :8788 if needed)
.\scripts\Open-POCKET-User.cmd
```
