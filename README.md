# Jira Release Helper

A tool that uses a `git` repo's commit history to determine which Jira issues are being deployed and consequently comment and/or close them.

## Usage

```
jira_release <COMMAND> <jira prefix> <environment> <remote commit hash> <local commit hash> <local git repo path>
```

The `COMMAND` can be either:

- `comment_and_close_issues_to_deploy`: for each detected Jira issue, this command will ask the user if he allows a commment to be posted, THEN asks if the program should close and resolve the issue.
- `comment_after_deploy`: for each detected Jira issue, this command will ask the user if he allows a commment to be posted.

**Example**

```
jira_release comment_after_deploy SWING- staging 8278cf99cf270332d113f6a3de7ea526c9a126db 5be893162f4bc698acdd6c969388117f0e25c931 /code
```