# This tree is INTERNAL (founder)

You use this folder every day. It is NOT the public product face.

- This repo: your running POCKET. Git remote = internal (local bare only).
- Public GitHub: ItsNotAILABS/pocket - marketing + customer releases. NOT a remote here.
- Your desk: http://127.0.0.1:8787/desk
- Customer host: https://pocket.medinatechlabs.net - only if you run the tunnel.

## Git

    git add -A
    git commit -m '...'
    git push internal main

Never re-add origin to github.com/ItsNotAILABS/pocket from this tree.

## Ship to public (deliberate)

1. Stabilize here.
2. Promote a clean copy/branch to public GitHub only when users should see it.
3. Do not auto-connect public remotes on this machine.

See FOUNDER.md
