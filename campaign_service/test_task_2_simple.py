#!/usr/bin/env python3
"""
Simple Task 2 Validation Test
"""

import sys
import os

# Set up test environment
os.environ['TESTING'] = 'true'
os.environ['SECRET_KEY'] = 'test_key'
os.environ['APP_NAME'] = 'test_app'
os.environ['APP_ENV'] = 'testing'
os.environ['DEBUG'] = 'true'

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all Task 2 components can be imported."""
    print("🧪 Testing Task 2 Imports...")
    
    try:
        # Test creation factory imports
        from src.services.creation_factory import CampaignCreationFactory, CampaignCreationOptions
        print("✅ Creation factory imports: OK")
        
        # Test creation service imports
        from src.services.creation import CampaignCreationService, CampaignCreationConfig
        print("✅ Creation service imports: OK")
        
        # Test model imports
        from src.models.campaign_creation_models import (
            CampaignFromScratchRequest, CampaignSkeletonRequest, 
            CampaignRefinementRequest, CampaignCreationType
        )
        print("✅ Model imports: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factory_creation():
    """Test factory instantiation."""
    print("🧪 Testing Factory Creation...")
    
    try:
        from src.services.creation_factory import CampaignCreationFactory
        
        # Create mock LLM service
        class MockLLM:
            pass
        
        factory = CampaignCreationFactory(MockLLM())
        
        # Check factory has required methods
        assert hasattr(factory, 'create_from_scratch'), "Missing create_from_scratch method"
        assert hasattr(factory, 'evolve_existing'), "Missing evolve_existing method"
        
        print("✅ Factory creation: OK")
        return True
        
    except Exception as e:
        print(f"❌ Factory creation failed: {e}")
        return False

def test_service_creation():
    """Test service instantiation."""
    print("🧪 Testing Service Creation...")
    
    try:
        from src.services.creation import CampaignCreationService, CampaignCreationConfig
        
        # Create mock LLM service
        class MockLLM:
            pass
        
        config = CampaignCreationConfig()
        service = CampaignCreationService(MockLLM(), config)
        
        # Check service has required methods
        assert hasattr(service, 'create_content'), "Missing create_content method"
        assert hasattr(service, 'refine_content'), "Missing refine_content method"
        
        print("✅ Service creation: OK")
        return True
        
    except Exception as e:
        print(f"❌ Service creation failed: {e}")
        return False

def check_task_2_implementation():
    """Check that Task 2 methods are implemented."""
    print("🧪 Checking Task 2 Implementation...")
    
    try:
        from src.services.creation_factory import CampaignCreationFactory
        import inspect
        
        # Check that placeholder methods are replaced
        factory = CampaignCreationFactory()
        
        # Get method source to check if it's implemented
        create_method = getattr(factory, '_create_campaign_from_scratch')
        source = inspect.getsource(create_method)
        
        if 'NotImplementedError' in source:
            print("❌ _create_campaign_from_scratch still has NotImplementedError")
            return False
        
        skeleton_method = getattr(factory, '_create_campaign_skeleton')
        source = inspect.getsource(skeleton_method)
        
        if 'NotImplementedError' in source:
            print("❌ _create_campaign_skeleton still has NotImplementedError")
            return False
        
        evolve_method = getattr(factory, '_evolve_campaign')
        source = inspect.getsource(evolve_method)
        
        if 'NotImplementedError' in source:
            print("❌ _evolve_campaign still has NotImplementedError")
            return False
        
        print("✅ Task 2 methods implemented: OK")
        return True
        
    except Exception as e:
        print(f"❌ Implementation check failed: {e}")
        return False

def main():
    """Run simple Task 2 validation."""
    print("🚀 Simple Task 2 Validation")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_factory_creation,
        test_service_creation,
        check_task_2_implementation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("=" * 50)
    if all(results):
        print("🎉 TASK 2 BASIC VALIDATION: PASSED")
        print("✅ All components can be imported and instantiated")
        print("✅ Core methods are implemented (not placeholders)")
        print("✅ Ready for endpoint testing")
    else:
        print("❌ TASK 2 BASIC VALIDATION: FAILED")
        print("Some components have issues")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
