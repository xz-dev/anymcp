"""
Behave environment setup
"""
from pathlib import Path
import tempfile
import shutil

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

def before_all(context):
    """Setup before all tests"""
    # Create a temporary directory for all tests
    context.test_root = Path(tempfile.mkdtemp(prefix="anymcp_test_"))
    context.original_tools_dir = Path("tools")

def after_all(context):
    """Cleanup after all tests"""
    # Clean up the test directory
    if hasattr(context, 'test_root') and context.test_root.exists():
        shutil.rmtree(context.test_root)
    
    # Clean up any generated test files
    import glob
    for test_file in glob.glob("features/test_*.feature"):
        Path(test_file).unlink(missing_ok=True)
    for step_file in glob.glob("features/steps/test_*_steps.py"):
        Path(step_file).unlink(missing_ok=True)

def before_scenario(context, scenario):
    """Setup before each scenario"""
    context.results = []
    context.execution_result = None
    context.creation_result = None
    
    # Create a unique test directory for this scenario
    import hashlib
    scenario_hash = hashlib.md5(scenario.name.encode()).hexdigest()[:8]
    context.test_dir = context.test_root / f"scenario_{scenario_hash}"
    context.test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create tools directory for this scenario
    context.tools_dir = context.test_dir / "tools"
    context.tools_dir.mkdir(exist_ok=True)
    
    # Don't copy original tools by default - let each test set up what it needs

def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Clean up scenario-specific directory
    if hasattr(context, 'test_dir') and context.test_dir.exists():
        shutil.rmtree(context.test_dir)