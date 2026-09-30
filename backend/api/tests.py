from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

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
