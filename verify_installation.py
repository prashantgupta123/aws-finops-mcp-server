#!/usr/bin/env python3
"""Verify AWS FinOps MCP Server installation."""

import sys
from importlib import import_module


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires ≥3.10)")
        return False


def check_dependencies():
    """Check required dependencies."""
    print("\nChecking dependencies...")
    dependencies = {
        "mcp": "mcp",
        "boto3": "boto3",
        "botocore": "botocore",
    }
    
    all_ok = True
    for name, module in dependencies.items():
        try:
            mod = import_module(module)
            version = getattr(mod, "__version__", "unknown")
            print(f"✅ {name}: {version}")
        except ImportError:
            print(f"❌ {name}: not installed")
            all_ok = False
    
    return all_ok


def check_package_structure():
    """Check package structure."""
    print("\nChecking package structure...")
    modules = [
        "aws_finops_mcp",
        "aws_finops_mcp.session",
        "aws_finops_mcp.server",
        "aws_finops_mcp.tools.cleanup",
        "aws_finops_mcp.tools.capacity",
        "aws_finops_mcp.tools.cost",
        "aws_finops_mcp.tools.application",
        "aws_finops_mcp.tools.upgrade",
        "aws_finops_mcp.utils.helpers",
        "aws_finops_mcp.utils.metrics",
    ]
    
    all_ok = True
    for module in modules:
        try:
            import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_ok = False
    
    return all_ok


def check_tools():
    """Check tool availability."""
    print("\nChecking tools...")
    try:
        from aws_finops_mcp.server import mcp
        
        # FastMCP stores tools in _tools attribute
        if hasattr(mcp, '_tools'):
            tool_count = len(mcp._tools)
            print(f"✅ Found {tool_count} tools registered")
            return True
        else:
            # Try to count decorated functions
            import inspect
            from aws_finops_mcp import server
            
            tool_count = 0
            for name, obj in inspect.getmembers(server):
                if inspect.isfunction(obj) and not name.startswith('_'):
                    tool_count += 1
            
            print(f"✅ Found {tool_count} tool functions defined")
            return True
    except Exception as e:
        print(f"❌ Error checking tools: {e}")
        return False


def check_aws_credentials():
    """Check AWS credentials (optional)."""
    print("\nChecking AWS credentials (optional)...")
    try:
        import boto3
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials configured")
        print(f"   Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"⚠️  AWS credentials not configured or invalid")
        print(f"   This is optional - you can configure later")
        return True  # Not a failure


def main():
    """Run all checks."""
    print("=" * 60)
    print("AWS FinOps MCP Server - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Package Structure", check_package_structure),
        ("Tools", check_tools),
        ("AWS Credentials", check_aws_credentials),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results[:-1])  # Exclude AWS creds check
    
    if all_passed:
        print("\n🎉 Installation verified successfully!")
        print("\nNext steps:")
        print("1. Configure AWS credentials (if not done)")
        print("2. Add to MCP client configuration")
        print("3. Start using the tools!")
        print("\nSee QUICKSTART.md for usage examples.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nInstallation command:")
        print("  pip install .")
        return 1


if __name__ == "__main__":
    sys.exit(main())
