# SecureFlag Code Recipes Repository

Welcome to the SecureFlag code recipes repository! 🎉

Here you'll find handy scripts, code snippets, and small demo apps showcasing how to interact with the SecureFlag platform.

Whether you are exploring the API, testing out ideas, or looking for inspiration on how to integrate SecureFlag into your own organization, these examples are here to help you get up and running faster.

## Git Hooks

Bring SecureFlag training and guidance to your local workflow with Git hooks!

### Assignment Completion Hook

Enforce SecureFlag assignment completion requirements before allowing commits.

This hook verifies that developers have completed their SecureFlag training assignments before they can commit code, ensuring continuous security compliance across your team.

**Key features:**
- Blocks commits if required assignments are incomplete
- Configurable requirements (initial assignments, pending assignments, or expired assignments)
- Clear feedback with direct links to incomplete training
- Easy setup with environment variables

📖 Read the [Assignment Hook README](/githooks-assignments/README.md) for setup instructions and details.

### GHSA Advisory Training Hook

Automatically enforce SecureFlag's vulnerability training compliance whenever a commit references a GitHub Security Advisory (GHSA).

This hook scans commit messages for GHSA IDs and verifies that the committer has completed the required training for those specific vulnerabilities.

**Key features:**
- Automatically detects GHSA IDs in commit messages
- Verifies training completion via SecureFlag API
- Provides direct links to required training modules
- Integrates seamlessly with GitHub's security advisory system

📖 Read the [GHSA Hook README](/githooks-ghsa/README.md) for setup instructions and details.

## Users' assignment report

Leverage the power of the SecureFlag APIs with a Python script that retrieves all users in your organization, along with their assigned learning paths and exercises.

This script demonstrates how to collect user details, fetch assignments and activities for each user, and export the combined results to a CSV report; giving you practical examples of API integration.

💻 Read the [`documentation`](/users_assignments_report/) to download and customize the script to create the reports you need!
