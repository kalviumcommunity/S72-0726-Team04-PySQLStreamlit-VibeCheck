import os
from unittest import mock

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from . import utils

class DashboardKPIsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    def test_get_kpis(self):
        response = self.client.get('/api/kpis/')
        self.assertEqual(response.status_code, 200)

class AnalyticsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_kpis_endpoint(self):
        response = self.client.get('/api/kpis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avg_onboarding_days', response.data)
        self.assertIn('time_to_value', response.data)
        self.assertIn('avg_tickets', response.data)
        self.assertIsInstance(response.data['avg_onboarding_days'], (int, float))

    def test_charts_endpoint(self):
        response = self.client.get('/api/charts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('scatter', response.data)
        self.assertIn('blockers', response.data)
        self.assertIn('tool_adoption', response.data)
        self.assertIn('buddy_impact', response.data)

    def test_employee_friction_table(self):
        response = self.client.get('/api/employees/?limit=10')
        self.assertEqual(response.status_code, 200)

    def test_employees_endpoint(self):
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if len(response.data) > 0:
            first_emp = response.data[0]
            self.assertIn('employee_id', first_emp)
            self.assertIn('friction_score', first_emp)

    def test_employee_detail_endpoint_valid(self):
        # Fetch list first to pick a valid employee ID
        list_response = self.client.get('/api/employees/')
        if len(list_response.data) > 0:
            emp_id = list_response.data[0]['employee_id']
            response = self.client.get(f'/api/employees/{emp_id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['employee_id'], emp_id)
            self.assertIn('tickets', response.data)
            self.assertIn('tool_usage', response.data)

    def test_employee_detail_endpoint_invalid(self):
        response = self.client.get('/api/employees/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FakeQuery:
    """Stand-in for supabase's table().select().range().execute() chain."""

    def __init__(self, rows):
        self.rows = rows
        self.bounds = None

    def select(self, _columns):
        return self

    def range(self, start, end):
        self.bounds = (start, end)
        return self

    def execute(self):
        start, end = self.bounds
        return mock.Mock(data=self.rows[start:end + 1])


class FetchTableTests(TestCase):
    SUPABASE_ENV = {'SUPABASE_URL': 'https://example.supabase.co', 'SUPABASE_ANON_KEY': 'test-key'}

    def supabase_returning(self, rows):
        client = mock.Mock()
        client.table.return_value = FakeQuery(rows)
        return mock.patch.object(utils, 'get_supabase_client', return_value=client)

    def test_without_credentials_reads_local_csv(self):
        with mock.patch.dict(os.environ):
            os.environ.pop('SUPABASE_URL', None)
            os.environ.pop('SUPABASE_ANON_KEY', None)
            self.assertEqual(len(utils.fetch_table_as_df('onboarding')), 1470)

    def test_reads_every_page_beyond_the_1000_row_cap(self):
        rows = [{'usage_id': i} for i in range(2500)]
        with mock.patch.dict(os.environ, self.SUPABASE_ENV), self.supabase_returning(rows):
            self.assertEqual(len(utils.fetch_table_as_df('tool_usage')), 2500)

    def test_empty_supabase_response_falls_back_to_csv(self):
        with mock.patch.dict(os.environ, self.SUPABASE_ENV), self.supabase_returning([]):
            with self.assertLogs('api.utils', level='WARNING'):
                self.assertEqual(len(utils.fetch_table_as_df('onboarding')), 1470)

    def test_supabase_errors_are_logged_not_swallowed(self):
        failing = mock.patch.object(utils, 'get_supabase_client', side_effect=ConnectionError('timeout'))
        with mock.patch.dict(os.environ, self.SUPABASE_ENV), failing:
            with self.assertLogs('api.utils', level='WARNING') as logs:
                utils.fetch_table_as_df('employees')
        self.assertIn('using the local CSV fallback', logs.output[0])

    def test_missing_csv_explains_how_to_restore_it(self):
        with mock.patch.dict(os.environ):
            os.environ.pop('SUPABASE_URL', None)
            with self.assertRaisesMessage(FileNotFoundError, 'git checkout -- data/payroll.csv'):
                utils.fetch_table_as_df('payroll')
