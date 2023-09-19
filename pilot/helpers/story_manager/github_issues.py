import os
import requests
from dotenv import load_dotenv
from github import Github, Auth
from .issue_management_system import IssueManagementSystem

load_dotenv()


class GitHubIssues(IssueManagementSystem):
    """
    See https://docs.github.com/en/rest/issues/issues
    """

    def __init__(self, project):
        # super().__init__()
        self.access_token = os.getenv('GITHUB_TOKEN')
        # auth = None  # Auth.Token(project.args['github_token'])
        auth = Auth.Token(self.access_token)
        self.g = Github(auth=auth)
        self.repo_id = 'Pythagora-io/gpt-pilot'
        # self.repo_id = 'nalbion/auto-gpt-action'
        self.owner, self.repo_name = self.repo_id.split('/')
        self.repo = self.g.get_repo(self.repo_id)

        if self.repo.organization is None:
            self.query_root = f'user(login: "{self.owner}")'
            self.data_root = 'user'
        else:
            self.query_root = f'organization(login: "{self.owner}")'
            self.data_root = 'organization'

        self.project_number = None

    def get_issues(self):
        issues = []
        # state can be 'open', 'closed', or 'all'
        # , labels = ['gpt-pilot']
        # , milestone = 'sprint-1'

        for issue in self.repo.get_issues(state='open'):
            issues.append({
                'id': issue.number,
                'title': issue.title,
                'body': issue.body
            })

        return issues

    def get_issues_for_iteration(self, iteration_id, label=None):
        issues = []
        project_number = self.get_project_number()
        cursor = None

        while True:
            data = self.send_graphql_query(
                'query($project_number: Int!, $cursor: String) {' + self.query_root + '''
                    {
                        projectV2(number: $project_number) {
                            items(first: 100, after: $cursor) {
                                pageInfo {
                                    hasNextPage
                                    endCursor
                                }
                                nodes {
                                    type
                                    content {
                                        ...on Issue {
                                            number
                                            title
                                            state
                                        }
                                    }
                                
                                    fieldValues(first: 10) {
                                        nodes {
                                            __typename
                                            ... on ProjectV2ItemFieldIterationValue {
                                               title
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }''', {
                    'project_number': project_number,
                    'cursor': cursor,
                })

            for node in data[self.data_root]["projectV2"]["items"]["nodes"]:
                if node["type"] == "ISSUE" and node["content"]["state"] == "OPEN":
                    if label and all(lbl["name"] != label for lbl in node["content"]["labels"]["nodes"]):
                        continue

                    for field_value in node["fieldValues"]["nodes"]:
                        if field_value["__typename"] == "ProjectV2ItemFieldIterationValue" \
                                and field_value["title"] == iteration_id:
                            issue = {
                                "number": node["content"]["number"],
                                "title": node["content"]["title"]
                            }
                            issues.append(issue)

            if data[self.data_root]["projectV2"]["items"]["pageInfo"]["hasNextPage"]:
                cursor = data[self.data_root]["projectV2"]["items"]["pageInfo"]["endCursor"]
            else:
                break

        return issues

    def get_project_number(self):
        if self.project_number is None:
            data = self.send_graphql_query(
                'query($repo_name: String!) {' + self.query_root + '''
                    {
                        projectsV2(query:$repo_name, first:1) {
                            ...on ProjectV2Connection {
                                nodes {
                                    number
                                }
                            }
                        }
                    }
                }''', {
                    'repo_name': self.repo_name,
                }
            )

            self.project_number = data[self.data_root]['projectsV2']['nodes'][0]['number']

        return self.project_number

    def send_graphql_query(self, query, variables):
        url = 'https://api.github.com/graphql'
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

        if response.status_code == 200:
            return response.json()['data']
        else:
            raise Exception('Error sending GraphQL query'.format(response.text))