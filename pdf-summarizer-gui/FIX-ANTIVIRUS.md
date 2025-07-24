# Fixing Antivirus/Windows Defender Issues

## Problem: Executable Gets Deleted/Quarantined

PyInstaller executables are often flagged as suspicious by antivirus software.

## Solutions:

### Option 1: Temporary Disable Windows Defender
1. Open Windows Security (search "Windows Security")
2. Go to "Virus & threat protection"
3. Click "Manage settings" under "Virus & threat protection settings"
4. Turn off "Real-time protection" (temporarily)
5. Run the build script again
6. Turn protection back on after testing

### Option 2: Add Exclusion Folder
1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Manage settings" under "Virus & threat protection settings"
4. Click "Add or remove exclusions"
5. Add folder exclusion for: `C:\Users\ruben\Documents\GitHub\PDF_summary_Desktop_app\pdf-summarizer-gui\dist`

### Option 3: Check Quarantine
1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Protection history"
4. Look for "PDF-Summarizer.exe" in recent threats
5. Restore the file if found

### Option 4: Alternative Build Location
```powershell
# Build to a different location
mkdir C:\temp\pdf-build
cd C:\temp\pdf-build
# Copy source files here and build
```

## For Distribution:
- Sign the executable with a code signing certificate
- Submit to antivirus vendors for whitelisting
- Use alternative packaging methods (like NSIS installer) 