import requests
from datetime import date, timedelta


TIMEOUT = 30  # seconds


class RedmineClient:
    def __init__(self, url: str, user: str, password: str):
        self.base = url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.session.headers.update({'Content-Type': 'application/json'})

    def _get(self, path: str, params: dict) -> dict:
        """Single GET with 1 retry on timeout."""
        url = f"{self.base}{path}"
        for attempt in range(2):
            try:
                resp = self.session.get(url, params=params, timeout=TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except requests.Timeout:
                if attempt == 1:
                    raise
            except requests.HTTPError as e:
                raise RuntimeError(
                    f"Redmine API error {e.response.status_code}: {path}"
                ) from e
        return {}

    def get_today_time_entries(self) -> list:
        today = date.today().isoformat()
        data = self._get('/time_entries.json', {
            'user_id': 'me',
            'spent_on': today,
            'limit': 100,
        })
        entries = []
        for e in data.get('time_entries', []):
            entries.append({
                'id': e['id'],
                'issue_id': e.get('issue', {}).get('id'),
                'issue_title': e.get('issue', {}).get('name', '(no issue)'),
                'project': e.get('project', {}).get('name', ''),
                'hours': e.get('hours', 0),
                'activity': e.get('activity', {}).get('name', ''),
                'comments': e.get('comments', ''),
            })
        return entries

    def get_issues_due(self, on_date: date) -> list:
        data = self._get('/issues.json', {
            'assigned_to_id': 'me',
            'due_date': on_date.isoformat(),
            'status_id': 'open',
            'limit': 100,
        })
        issues = []
        for i in data.get('issues', []):
            issues.append({
                'id': i['id'],
                'subject': i.get('subject', ''),
                'project': i.get('project', {}).get('name', ''),
                'status': i.get('status', {}).get('name', ''),
                'priority': i.get('priority', {}).get('name', ''),
                'due_date': i.get('due_date', ''),
                'url': f"{self.base}/issues/{i['id']}",
            })
        return issues

    def get_issues_due_today(self) -> list:
        return self.get_issues_due(date.today())

    def get_issues_due_tomorrow(self) -> list:
        return self.get_issues_due(date.today() + timedelta(days=1))
