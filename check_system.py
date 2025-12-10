#!/usr/bin/env python3
"""
System Check Script for Pet Roast AI Service

Verifies all components are properly configured:
- Python environment
- Required packages
- IndicTrans2 integration
- Revid.ai client
- Pet detection (YOLOv5)
- Environment variables
- File structure
"""

import sys
import os
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")


def check_python_version():
    """Check Python version."""
    print_header("1. Python Version Check")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version_str} - Compatible")
        return True
    else:
        print_error(f"Python {version_str} - Requires Python 3.10+")
        return False


def check_required_packages():
    """Check if required packages are installed."""
    print_header("2. Required Packages Check")

    packages = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'httpx': 'HTTP client',
        'pydantic': 'Data validation',
        'redis': 'Redis client',
        'torch': 'PyTorch (YOLOv5)',
        'torchvision': 'Computer vision',
        'PIL': 'Image processing',
        'numpy': 'Numerical computing',
        'cv2': 'OpenCV',
    }

    all_installed = True
    for package, description in packages.items():
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'cv2':
                __import__('cv2')
            else:
                __import__(package)
            print_success(f"{description} ({package})")
        except ImportError:
            print_error(f"{description} ({package}) - NOT INSTALLED")
            all_installed = False

    return all_installed


def check_file_structure():
    """Check if all required files and directories exist."""
    print_header("3. File Structure Check")

    required_paths = {
        'app/': 'Application directory',
        'app/main.py': 'Main application',
        'app/api/routes.py': 'API routes',
        'app/clients/revid.py': 'Revid.ai client',
        'app/clients/ai4bharat.py': 'AI4Bharat client',
        'app/services/pet_detection.py': 'Pet detection service',
        'app/core/config.py': 'Configuration',
        'app/core/webhook.py': 'Webhook utilities',
        'Dockerfile': 'Docker configuration',
        'railway.json': 'Railway configuration',
        'requirements.txt': 'Python dependencies',
        '.env.example': 'Environment template',
    }

    all_exist = True
    for path, description in required_paths.items():
        full_path = Path(path)
        if full_path.exists():
            print_success(f"{description} - {path}")
        else:
            print_error(f"{description} - {path} - MISSING")
            all_exist = False

    return all_exist


def check_indictrans2():
    """Check IndicTrans2 integration."""
    print_header("4. IndicTrans2 Integration Check")

    indictrans_path = Path('IndicTrans2')

    if not indictrans_path.exists():
        print_error("IndicTrans2 directory not found")
        print_info("IndicTrans2 is optional but recommended for Indian language support")
        return False

    required_files = [
        'IndicTrans2/inference_server.py',
        'IndicTrans2/README.md',
        'IndicTrans2/fairseq/',
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Found: {file_path}")
        else:
            print_warning(f"Missing: {file_path}")
            all_exist = False

    if all_exist:
        print_success("IndicTrans2 is properly integrated")
    else:
        print_warning("IndicTrans2 integration incomplete - Indian languages may not work")

    return all_exist


def check_environment_variables():
    """Check environment variables."""
    print_header("5. Environment Variables Check")

    # Check if .env file exists
    env_file = Path('.env')
    env_example = Path('.env.example')

    if not env_file.exists():
        if env_example.exists():
            print_warning(".env file not found")
            print_info("Run: cp .env.example .env")
            print_info("Or run: ./setup_backend.sh")
            return False
        else:
            print_error(".env.example not found")
            return False

    print_success(".env file exists")

    # Check critical environment variables
    required_vars = {
        'REVID_API_KEY': 'Revid.ai API key (required)',
        'BACKEND_WEBHOOK_URL': 'Backend webhook URL (optional)',
        'REDIS_URL': 'Redis connection (required)',
    }

    try:
        from dotenv import load_dotenv
        load_dotenv()

        all_set = True
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value and value != f'your_{var.lower()}':
                print_success(f"{var} - Configured")
            else:
                if 'optional' in description:
                    print_warning(f"{var} - Not set ({description})")
                else:
                    print_error(f"{var} - Not set ({description})")
                    all_set = False

        return all_set

    except ImportError:
        print_warning("python-dotenv not installed - cannot check .env")
        return False


def check_api_clients():
    """Check API client implementations."""
    print_header("6. API Clients Check")

    try:
        # Try importing clients
        from app.clients.revid import RevidClient
        print_success("Revid.ai client - OK")
    except Exception as e:
        print_error(f"Revid.ai client - {e}")
        return False

    try:
        from app.clients.ai4bharat import AI4BharatClient
        print_success("AI4Bharat client - OK")
    except Exception as e:
        print_error(f"AI4Bharat client - {e}")
        return False

    try:
        from app.services.pet_detection import PetDetectionService
        print_success("Pet detection service - OK")
    except Exception as e:
        print_error(f"Pet detection service - {e}")
        return False

    return True


def check_documentation():
    """Check documentation files."""
    print_header("7. Documentation Check")

    docs = {
        'README.md': 'Project overview',
        'QUICK_START_BACKEND.md': 'Quick start guide',
        'BACKEND_INTEGRATION.md': 'Backend integration guide',
        'API_REFERENCE.md': 'API documentation',
        'RAILWAY_DEPLOYMENT.md': 'Railway deployment guide',
        'DEPLOYMENT_CHECKLIST.md': 'Deployment checklist',
    }

    all_exist = True
    for doc, description in docs.items():
        if Path(doc).exists():
            print_success(f"{description} - {doc}")
        else:
            print_warning(f"{description} - {doc} - Missing")
            all_exist = False

    return all_exist


def main():
    """Run all system checks."""
    print(f"\n{Colors.BOLD}🔍 Pet Roast AI Service - System Check{Colors.ENDC}\n")

    results = {
        'Python Version': check_python_version(),
        'Required Packages': check_required_packages(),
        'File Structure': check_file_structure(),
        'IndicTrans2': check_indictrans2(),
        'Environment Variables': check_environment_variables(),
        'API Clients': check_api_clients(),
        'Documentation': check_documentation(),
    }

    # Summary
    print_header("System Check Summary")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for check, result in results.items():
        if result:
            print_success(f"{check}: PASSED")
        else:
            print_error(f"{check}: FAILED")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.ENDC}\n")

    if passed == total:
        print_success("✨ All checks passed! System is ready for deployment! 🚀")
        return 0
    else:
        print_warning(f"⚠️  {total - passed} check(s) failed. Please review and fix.")
        print_info("\nNext steps:")
        if not results['Environment Variables']:
            print_info("  1. Run: ./setup_backend.sh")
        if not results['Required Packages']:
            print_info("  2. Run: pip install -r requirements.txt")
        if not results['IndicTrans2']:
            print_info("  3. IndicTrans2 is optional for Indian languages")
        return 1


if __name__ == '__main__':
    sys.exit(main())
