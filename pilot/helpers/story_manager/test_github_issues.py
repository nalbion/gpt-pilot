from unittest.mock import patch, Mock
from .github_issues import GitHubIssues

github_issues = GitHubIssues(None)
github_issues.project_number = 1


MOCK_RESPONSE = {
    "organization": {
        "projectV2": {
            "items": {
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": "Mg"
                },
                "nodes": [
                    {
                        "type": "ISSUE",
                        "content": {
                            "number": 1,
                            "title": "pylint is not passing",
                            "state": "OPEN",
                            "labels": {
                                "nodes": [
                                    {
                                        "name": "gpt-pilot"
                                    }
                                ]
                            }
                        },
                        "fieldValues": {
                            "nodes": [
                                {
                                    "__typename": "ProjectV2ItemFieldRepositoryValue"
                                },
                                {
                                    "__typename": "ProjectV2ItemFieldLabelValue"
                                },
                                {
                                    "__typename": "ProjectV2ItemFieldTextValue"
                                },
                                {
                                    "__typename": "ProjectV2ItemFieldIterationValue",
                                    "title": "Sprint 1"
                                }
                            ]
                        }
                    },
                    {
                        "type": "ISSUE",
                        "content": {
                            "number": 2,
                            "title": "Need to actually call AutoGPT",
                            "state": "OPEN",
                            "labels": {
                                "nodes": []
                            }
                        },
                        "fieldValues": {
                            "nodes": [
                                {
                                    "__typename": "ProjectV2ItemFieldRepositoryValue"
                                },
                                {
                                    "__typename": "ProjectV2ItemFieldTextValue"
                                },
                                {
                                    "__typename": "ProjectV2ItemFieldIterationValue",
                                    "title": "Sprint 2"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
}


class TestGitHubIssues:
    def test_get_issues(self):
        issues = github_issues.get_issues()

        print(issues)

    # def test_get_project_number(self):
    #     project_number = github_issues.get_project_number()
    #     assert project_number == 1

    @patch.object(github_issues, 'send_graphql_query', return_value=MOCK_RESPONSE)
    def test_get_issues_for_iteration(self, mock_send):
        # When
        issues = github_issues.get_issues_for_iteration('Sprint 1')

        assert len(issues) == 1

    @patch.object(github_issues, 'send_graphql_query', return_value=MOCK_RESPONSE)
    def test_get_issues_for_iteration_with_label(self, mock_send):
        # When
        issues = github_issues.get_issues_for_iteration('Sprint 1', 'bad-label')

        assert len(issues) == 0
