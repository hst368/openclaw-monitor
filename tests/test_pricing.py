"""
Tests for pricing_manager module
"""

import os
import json
import pytest
import tempfile
import shutil
from pricing_manager import PricingManager


class TestPricingManager:
    """Test cases for PricingManager"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def pricing_manager(self, temp_config_dir, monkeypatch):
        """Create PricingManager with temp config"""
        monkeypatch.setattr(PricingManager, 'CONFIG_DIR', temp_config_dir)
        monkeypatch.setattr(PricingManager, 'CONFIG_FILE', 
                          os.path.join(temp_config_dir, 'pricing.json'))
        return PricingManager()
    
    def test_default_config_creation(self, pricing_manager):
        """Test default config is created"""
        config = pricing_manager.get_all_pricing()
        assert config['currency'] in ['CNY', 'USD']
        assert 'models' in config
        assert 'default' in config['models']
    
    def test_get_model_pricing(self, pricing_manager):
        """Test getting model pricing"""
        pricing = pricing_manager.get_model_pricing('moonshot/kimi-k2.5')
        assert 'input_per_1k' in pricing
        assert 'output_per_1k' in pricing
        assert pricing['currency'] in ['CNY', 'USD']
    
    def test_update_model_pricing(self, pricing_manager):
        """Test updating model pricing"""
        success = pricing_manager.update_model_pricing(
            'test-model',
            0.001,
            0.002,
            'CNY',
            'Test Provider',
            'Test update'
        )
        assert success is True
        
        # Verify update
        pricing = pricing_manager.get_model_pricing('test-model')
        assert pricing['input_per_1k'] == 0.001
        assert pricing['output_per_1k'] == 0.002
        assert pricing['currency'] == 'CNY'
    
    def test_calculate_cost(self, pricing_manager):
        """Test cost calculation"""
        result = pricing_manager.calculate_cost(
            'moonshot/kimi-k2.5',
            1000,  # input tokens
            500    # output tokens
        )
        
        assert 'input_cost' in result
        assert 'output_cost' in result
        assert 'total_cost' in result
        assert result['input_tokens'] == 1000
        assert result['output_tokens'] == 500
        assert result['total_cost'] > 0
    
    def test_currency_conversion(self, pricing_manager):
        """Test currency conversion"""
        pricing_manager.set_display_currency('USD')
        
        result = pricing_manager.calculate_cost(
            'moonshot/kimi-k2.5',
            1000,
            500
        )
        
        assert result['currency'] == 'USD'
    
    def test_delete_model_pricing(self, pricing_manager):
        """Test deleting model pricing"""
        # First add a model
        pricing_manager.update_model_pricing(
            'temp-model',
            0.001,
            0.002,
            'CNY'
        )
        
        # Then delete it
        success = pricing_manager.delete_model_pricing('temp-model')
        assert success is True
        
        # Verify deletion
        pricing = pricing_manager.get_model_pricing('temp-model')
        assert pricing == pricing_manager.get_model_pricing('default')
