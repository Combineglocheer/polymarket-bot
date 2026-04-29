# Security Policy

## Reporting a vulnerability

If you discover a security issue in Polymarket Bot, please **do not** file a public issue or pull request. Instead:

- Email the maintainers privately, OR
- Use GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/repository-security-advisories/privately-reporting-a-security-vulnerability).

We will acknowledge your report within **72 hours** and aim to publish a fix within **14 days** depending on severity.

## What counts as a vulnerability

- Anything that could leak a user's private key or API credentials
- Anything that could let an attacker place orders on a user's behalf
- Remote code execution in any code path the user is expected to run
- Bypasses of the risk manager that lead to uncapped losses

## What does NOT count

- Losing money because of a bad strategy (this is a research tool, not a guarantee)
- Polymarket-side outages
- Issues in upstream dependencies (please report those upstream)

## Responsible disclosure

We follow a coordinated disclosure model. Please give us a reasonable window to ship a fix before publishing.

Thank you for keeping the community safe.
