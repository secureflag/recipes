# SecureFlag Code Recipes Repository

Welcome to the SecureFlag code recipes repository! 🎉

Here you'll find handy scripts, code snippets, and small demo apps showcasing how to interact with the SecureFlag platform.

Whether you are exploring the API, testing out ideas, or looking for inspiration on how to integrate SecureFlag into your own organization, these examples are here to help you get up and running faster.

## Git Hook: SecureFlag Assignment Completion

Enforce SecureFlag assignment completion requirements before allowing pushes to remote repositories.

This hook verifies that developers have met configurable training requirements before they can push code, ensuring continuous security compliance across your team. The hook provides flexible configuration options to match your organization's security policies.

**What does it do?**
- Verifies that users meet one of three configurable assignment requirements:
  - **Completed initial assignments**: All onboarding or initial training assignments are complete (default)
  - **Completed pending assignments**: All currently pending assignments are complete
  - **No expired assignments**: The user has no assignments that have passed their deadline
- **Blocks pushes** if the user has not met the configured requirement, with clear instructions on what needs to be completed

📖 Read the [Assignment Hook README](/githooks-assignments/README.md) for setup instructions and details.

## Git Hook: SecureFlag Training Based On GHSA Advisory

Automatically enforce SecureFlag's vulnerability training compliance whenever a commit references a GitHub Security Advisory (GHSA).

This hook scans commit messages for GHSA IDs and verifies that the committer has completed the required training for those specific vulnerabilities, creating a direct link between vulnerability remediation and security training.

**What does it do?**
- **Scans the commit message** for any GHSA IDs (e.g., `GHSA-xxxx-xxxx-xxxx`)
- For each GHSA ID found:
  - Checks the corresponding advisory in the current GitHub repository via the GitHub API
  - Verifies, via the SecureFlag API, whether the committer has completed the required training for the referenced vulnerability
- **Blocks the commit** if the committer has not completed the required training, and provides instructions and direct links to the relevant SecureFlag training

📖 Read the [GHSA Hook README](/githooks-ghsa/README.md) for setup instructions and details.

## Users' assignment report

Leverage the power of the SecureFlag APIs with a Python script that retrieves all users in your organization, along with their assigned learning paths and exercises.

This script demonstrates how to collect user details, fetch assignments and activities for each user, and export the combined results to a CSV report; giving you practical examples of API integration.

💻 Read the [`documentation`](/users_assignments_report/) to download and customize the script to create the reports you need!
