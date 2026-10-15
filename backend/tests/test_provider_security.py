import contextlib
import io
import json
import unittest
from unittest.mock import patch, MagicMock
from app.db.models.providers import Provider
from app.services.provider import ProviderService

class ProviderSecurityTests(unittest.TestCase):
    def setUp(self):
        self.key = 'sk-audit-only-fake-credential-1234567890'
        self.provider = Provider(id='test', name='Test', logo='', type='custom', api_key=self.key, base_url='https://example.invalid', enabled=1)

    def test_list_masks_key(self):
        with patch('app.services.provider.get_all_providers', return_value=[self.provider]):
            result = ProviderService.get_all_providers_safe()
        self.assertNotIn(self.key, json.dumps(result))
        self.assertIn('*', result[0]['api_key'])
        self.assertEqual(result[0]['id'], 'test')

    def test_detail_masks_key(self):
        with patch('app.services.provider.get_provider_by_id', return_value=self.provider):
            result = ProviderService.get_provider_by_id_safe('test')
        self.assertNotIn(self.key, json.dumps(result))
        self.assertIn('*', result['api_key'])

    def test_internal_model_access_keeps_real_key(self):
        with patch('app.services.provider.get_provider_by_id', return_value=self.provider):
            result = ProviderService.get_provider_by_id('test')
        self.assertEqual(result['api_key'], self.key)

    def test_empty_list_and_short_keys(self):
        with patch('app.services.provider.get_all_providers', return_value=[]):
            self.assertEqual(ProviderService.get_all_providers_safe(), [])
        self.assertEqual(ProviderService.mask_key('abc'), '***')
        self.assertEqual(ProviderService.mask_key(''), '')

    def test_update_does_not_log_key_or_overwrite_with_mask(self):
        output = io.StringIO()
        with patch('app.services.provider.update_provider') as update, patch('app.services.provider.get_provider_by_id', return_value=self.provider), contextlib.redirect_stdout(output):
            ProviderService.update_provider('test', {'api_key': self.key})
            self.assertEqual(update.call_args.kwargs['api_key'], self.key)
            ProviderService.update_provider('test', {'api_key': ProviderService.mask_key(self.key), 'name': 'Test'})
            self.assertNotIn('api_key', update.call_args.kwargs)
        self.assertNotIn(self.key, output.getvalue())

    def test_update_error_does_not_log_sensitive_exception(self):
        output = io.StringIO()
        with patch('app.services.provider.update_provider', side_effect=Exception(self.key)), contextlib.redirect_stdout(output):
            self.assertIsNone(ProviderService.update_provider('test', {'api_key': self.key}))
        self.assertNotIn(self.key, output.getvalue())

    def test_database_failures_do_not_log_key(self):
        from app.db import provider_dao
        for action in ['insert', 'update', 'delete']:
            with self.subTest(action=action):
                db = MagicMock()
                db.query.return_value.filter_by.return_value.first.return_value = self.provider
                db.commit.side_effect = Exception(self.key)
                with patch.object(provider_dao, 'get_db', return_value=iter([db])), patch.object(provider_dao, 'logger') as logger:
                    if action == 'insert':
                        provider_dao.insert_provider('test', 'Test', self.key, 'https://example.invalid', '', 'custom')
                    elif action == 'update':
                        provider_dao.update_provider('test', api_key=self.key)
                    else:
                        provider_dao.delete_provider('test')
                    logger.error.assert_called_once()
                    self.assertNotIn(self.key, str(logger.mock_calls))

if __name__ == '__main__':
    unittest.main()
