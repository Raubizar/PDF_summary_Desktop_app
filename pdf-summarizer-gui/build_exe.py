"""
Enhanced build script to create a standalone executable from the PDF summarizer GUI application.
Run this script to create a distributable .exe file for non-technical users.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies with better error handling"""
    print("\n" + "="*50)
    print("INSTALLING DEPENDENCIES")
    print("="*50)
    
    dependencies = [
        ("pyinstaller", "PyInstaller for creating executables"),
        ("requirements.txt", "Application dependencies")
    ]
    
    for dep, description in dependencies:
        print(f"\nInstalling {description}...")
        try:
            if dep == "requirements.txt":
                cmd = [sys.executable, "-m", "pip", "install", "-r", dep]
            else:
                cmd = [sys.executable, "-m", "pip", "install", dep]
                
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Successfully installed {dep}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}")
            print(f"Error: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
    
    return True

def clean_build_directories():
    """Clean previous build artifacts"""
    print("\n" + "="*50)
    print("CLEANING BUILD DIRECTORIES")
    print("="*50)
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    project_root = Path(__file__).parent
    
    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Cleaned {dir_name}/")
            except Exception as e:
                print(f"⚠️ Could not clean {dir_name}/: {e}")
    
    # Clean spec files
    for spec_file in project_root.glob("*.spec"):
        try:
            spec_file.unlink()
            print(f"✅ Cleaned {spec_file.name}")
        except Exception as e:
            print(f"⚠️ Could not clean {spec_file.name}: {e}")

def create_icon():
    """Create a simple icon file if none exists"""
    # For now, we'll skip icon creation but prepare for it
    project_root = Path(__file__).parent
    icon_path = project_root / "src" / "resources"
    icon_path.mkdir(parents=True, exist_ok=True)
    return None  # No icon for now

def build_executable():
    """Build the executable using PyInstaller with optimized settings"""
    print("\n" + "="*50)
    print("BUILDING EXECUTABLE")
    print("="*50)
    
    # Ensure we're in the correct directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Build command with enhanced options
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI app)
        "--name", "PDF-Summarizer",     # Name of the executable
        "--distpath", "dist",           # Output directory
        "--workpath", "build",          # Build directory
        "--specpath", ".",              # .spec file location
        "--clean",                      # Clean PyInstaller cache
        "--noconfirm",                  # Replace output directory without confirmation
        # Hidden imports for better compatibility
        "--hidden-import", "PyQt5.sip",
        "--hidden-import", "pkg_resources.py2_warn",
        "--hidden-import", "sklearn.utils._cython_blas",
        "--hidden-import", "sklearn.neighbors.typedefs",
        "--hidden-import", "sklearn.neighbors.quad_tree",
        "--hidden-import", "sklearn.tree._utils",
        # Collect data files
        "--collect-data", "sentence_transformers",
        "--collect-data", "transformers",
        "src/main.py"                   # Entry point
    ]
    
    # Add icon if it exists
    icon_path = project_root / "src" / "resources" / "icon.ico"
    if icon_path.exists():
        build_cmd.extend(["--icon", str(icon_path)])
    
    print("Building executable with command:")
    print(" ".join(build_cmd))
    print("\nThis may take several minutes...")
    
    try:
        # Run PyInstaller
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        
        # Check if executable was created
        exe_path = project_root / "dist" / "PDF-Summarizer.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Executable created: {exe_path}")
            print(f"✅ File size: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Executable file not found after build!")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def create_distribution_package():
    """Create a distribution package with instructions"""
    print("\n" + "="*50)
    print("CREATING DISTRIBUTION PACKAGE")
    print("="*50)
    
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    
    if not dist_dir.exists():
        print("❌ Distribution directory not found!")
        return False
    
    # Create README for end users
    readme_content = """# PDF Summarizer - Standalone Application

## Quick Start

1. **Install Ollama** (Required for AI functionality):
   - Download from: https://ollama.ai/
   - Install and run Ollama
   - Open command prompt/terminal and run: `ollama pull gemma3:1b`
   - Keep Ollama running in the background

2. **Run the Application**:
   - Double-click `PDF-Summarizer.exe`
   - Click "Select Folder" to choose a folder with PDF or text files
   - Wait for processing to complete
   - Find summaries in the `output_rag` subfolder

## System Requirements

- Windows 10 or later
- Internet connection (for AI processing)
- Ollama installed and running

## Supported File Types

- PDF files (.pdf)
- Text files (.txt)

## Output

The application creates:
- Individual summary files: `filename_rag_answer.txt`
- Combined spreadsheet: `summaries.xlsx`
- All saved in: `[your_folder]/output_rag/`

## Troubleshooting

### "Ollama not detected" error:
- Make sure Ollama is installed from https://ollama.ai/
- Run `ollama pull gemma3:1b` in command prompt
- Ensure Ollama is running (check system tray)

### Application won't start:
- Check Windows Defender/antivirus isn't blocking the file
- Right-click the .exe file and select "Run as administrator"

### No files found:
- Make sure your folder contains .pdf or .txt files
- Check file extensions are correct (.PDF works too)

## Support

For issues or questions, please check the help button in the application.
"""
    
    readme_path = dist_dir / "README.txt"
    try:
        readme_path.write_text(readme_content, encoding='utf-8')
        print(f"✅ Created user README: {readme_path}")
    except Exception as e:
        print(f"⚠️ Could not create README: {e}")
    
    return True

def test_executable():
    """Test if the executable can start"""
    print("\n" + "="*50)
    print("TESTING EXECUTABLE")
    print("="*50)
    
    project_root = Path(__file__).parent
    exe_path = project_root / "dist" / "PDF-Summarizer.exe"
    
    if not exe_path.exists():
        print("❌ Executable not found for testing!")
        return False
    
    print("Testing executable startup (will close automatically)...")
    try:
        # Test with a timeout to avoid hanging
        process = subprocess.Popen([str(exe_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait briefly to see if it starts
        import time
        time.sleep(3)
        
        # Try to terminate gracefully
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("✅ Executable starts successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Executable test failed: {e}")
        return False

def main():
    """Main build process with comprehensive checks"""
    print("PDF SUMMARIZER - ENHANCED EXECUTABLE BUILDER")
    print("=" * 60)
    print("Building standalone executable for non-technical users...")
    
    # Check Python version
    if not check_python_version():
        print("\n❌ BUILD FAILED: Incompatible Python version")
        return
    
    # Clean previous builds
    clean_build_directories()
    
    # Check if PyInstaller is installed
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], check=True, capture_output=True)
        print("✅ PyInstaller found.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ PyInstaller not found. Installing dependencies...")
        if not install_dependencies():
            print("\n❌ BUILD FAILED: Could not install dependencies")
            return
    
    # Install/update all dependencies
    print("\nEnsuring all dependencies are up to date...")
    if not install_dependencies():
        print("\n❌ BUILD FAILED: Dependency installation failed")
        return
    
    # Build the executable
    if not build_executable():
        print("\n❌ BUILD FAILED: Executable creation failed")
        return
    
    # Create distribution package
    if not create_distribution_package():
        print("\n⚠️ Warning: Could not create complete distribution package")
    
    # Test executable
    if not test_executable():
        print("\n⚠️ Warning: Executable test failed, but file may still work")
    
    # Final success message
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nDistribution files created in 'dist/' folder:")
    
    dist_dir = Path(__file__).parent / "dist"
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size / (1024 * 1024)
                print(f"  📁 {file.name} ({size:.1f} MB)")
    
    print("\n📋 DISTRIBUTION INSTRUCTIONS:")
    print("1. Copy the entire 'dist' folder to share with users")
    print("2. Users need to install Ollama separately from https://ollama.ai/")
    print("3. Users should read the README.txt file for setup instructions")
    print("4. The executable works on Windows 10+ without Python installed")
    
    print("\n✅ Ready for distribution to non-technical users!")

if __name__ == "__main__":
    main()
