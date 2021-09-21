import os
import re
import subprocess
import sys

import fire


def get_issues_in_deployment(jira_prefix, remote_version, to_deploy_version, git_path):
    """
    Returns a list of Jira issues that are found in the commit messages to deploy.
    This list is determined by matching a pattern in the pending commits' message
    @param jira_prefix: The prefix of the Jira issue
    @param remote_version: The version currently live on the remote server
    @param to_deploy_version: The version to be deployed
    @param git_path: The path of the local git repository
    @return: a list of Jira issues
    @rtype: List[Str]
    """
    path = os.path.join(os.getcwd(), git_path)
    changes = subprocess.check_output("git log --no-color --oneline".split() + [f"{remote_version}..{to_deploy_version}"],
                                      cwd=path, text=True)

    changes = changes.split("\n")

    issues = []

    for change in changes:
        test = re.match(f"(.*)({jira_prefix}\d+)(.*)", change)
        if test:
            issues.append(test.groups()[1])

    return issues


class JiraReleaseHelper(object):
    """
    Tool used at deploy-time that uses the Atlassian Jira API to post comments and
    change the state of Jira issues that are being deployed.
    """

    def __init__(self):
        from jira import JIRA

        try:
            username = os.environ["JIRA_USERNAME"]
            password = os.environ["JIRA_PASSWORD"]
            url = os.environ["JIRA_URL"]
        except KeyError:
            sys.exit("Please set JIRA_USERNAME, JIRA_PASSWORD and JIRA_URL environment variables")

        try:
            self.jira = JIRA(url, basic_auth=(username, password))
        except Exception:
            sys.exit("Jira authentication issue")

    def __comment_confirm_deploy(self, environment, issue):
        if (
            input(
                f"Do you want to comment about the deployment of {issue} to {environment} on the Jira issue? [y/N]: "
            ).lower()
            == "y"
        ):
            self.jira.add_comment(
                issue, f"{issue} was deployed in the {environment} environment"
            )

    def __close_and_resolve(self, issue):
        jira_issue = self.jira.issue(issue)
        resolution_mapping = {"Bug": "Fixed"}
        resolution_name = resolution_mapping.get(
            jira_issue.fields.issuetype.name, "Done"
        )
        transitions = self.jira.transitions(jira_issue)
        close_transition_id = None
        for transition in transitions:
            if transition["name"] == "Close":
                close_transition_id = transition["id"]

        if close_transition_id is None:
            print(
                f"Skipping closing procedure for Jira issue {issue} in status {jira_issue.fields.status.name}"
            )
            return

        if (
            input(
                f"Do you want to close Jira issue {issue} and mark it as {resolution_name} ? [y/N]: "
            ).lower()
            == "y"
        ):
            self.jira.transition_issue(
                jira_issue,
                close_transition_id,
                resolution={"name": resolution_name},
            )

    def comment_after_deploy(
        self,
        jira_prefix,
        environment,
        remote_version,
        to_deploy_version="HEAD",
        git_path=".",
    ):
        """
        Posts a comment on JIRA issues that are to be deployed
        @param jira_prefix: The prefix of the JIRA issue
        @param environment: The environment to be deploy in
        @param remote_version: The version currently live on the remote server
        @param to_deploy_version: The version to be deployed
        @param git_path: The path of the local git repository
        @return: None
        """
        issues = get_issues_in_deployment(
            jira_prefix, remote_version, to_deploy_version, git_path
        )

        if not issues:
            return "No JIRA issues found in this deployment"

        for issue in issues:
            self.__comment_confirm_deploy(environment, issue)

    def comment_and_close_issues_to_deploy(
        self,
        jira_prefix,
        environment,
        remote_version,
        to_deploy_version="HEAD",
        git_path=".",
    ):
        """
        Posts a comment on JIRA issues that are to be deployed, and asks to close and
        resolve them.
        @param jira_prefix: The prefix of the JIRA issue
        @param environment: The environment to be deploy in
        @param remote_version: The version currently live on the remote server
        @param to_deploy_version: The version to be deployed
        @param git_path: The path of the local git repository
        @return: None
        """

        issues = get_issues_in_deployment(
            jira_prefix, remote_version, to_deploy_version, git_path
        )

        if not issues:
            return "No JIRA issues found in this deployment"

        for issue in issues:
            self.__comment_confirm_deploy(environment, issue)
            self.__close_and_resolve(issue)


def main():
    fire.Fire(JiraReleaseHelper)


if __name__ == "__main__":
    main()
