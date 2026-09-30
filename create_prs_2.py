import os
import subprocess

REPO_DIR = r'c:\Users\v4paw\Desktop\vibe\S72-0726-Team04-PySQLStreamlit-VibeCheck'
os.chdir(REPO_DIR)

changes = [
    {
        'branch': 'vedant/fix-error-handling',
        'file': 'backend/api/utils.py',
        'search': '        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), \'data\', f\'{table_name}.csv\')\n        return pd.read_csv(csv_path)',
        'replace': '        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), \'data\', f\'{table_name}.csv\')\n        if os.path.exists(csv_path):\n            return pd.read_csv(csv_path)\n        else:\n            print(f"Warning: {csv_path} not found")\n            return pd.DataFrame()',
        'msg': 'Improve Data Fetching Error Handling'
    },
    {
        'branch': 'vedant/test-kpi-view',
        'file': 'backend/api/tests.py',
        'search': 'class AnalyticsApiTests(TestCase):',
        'replace': 'class DashboardKPIsTest(TestCase):\n    def setUp(self):\n        self.client = APIClient()\n    def test_get_kpis(self):\n        response = self.client.get(\'/api/kpis/\')\n        self.assertEqual(response.status_code, 200)\n\nclass AnalyticsApiTests(TestCase):',
        'msg': 'Unit Tests for Dashboard KPIs'
    },
    {
        'branch': 'vedant/test-friction-table',
        'file': 'backend/api/tests.py',
        'search': '    def test_employees_endpoint(self):\n        response = self.client.get(\'/api/employees/\')',
        'replace': '    def test_employee_friction_table(self):\n        response = self.client.get(\'/api/employees/?limit=10\')\n        self.assertEqual(response.status_code, 200)\n\n    def test_employees_endpoint(self):\n        response = self.client.get(\'/api/employees/\')',
        'msg': 'Unit Tests for Friction Table'
    }
]

created_branches = 0
for i, change in enumerate(changes):
    subprocess.run(['git', 'checkout', '-q', 'main'])
    try:
        subprocess.run(['git', 'branch', '-D', change['branch']], capture_output=True)
    except:
        pass
        
    subprocess.run(['git', 'checkout', '-q', '-b', change['branch']])
    
    modified = False
    
    if os.path.exists(change['file']):
        with open(change['file'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        if change['search'] in content:
            new_content = content.replace(change['search'], change['replace'])
            with open(change['file'], 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified = True
            
    if modified:
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-q', '-m', f"feat: {change['msg']}"])
        created_branches += 1
        print(f"Created branch {i+1}/3: {change['branch']}")
    else:
        print(f"Warning: Could not apply changes for {change['branch']}")
    
subprocess.run(['git', 'checkout', '-q', 'main'])
print(f'Done processing remaining branches. Created {created_branches} branches.')
