# DICOM Anonymizer - PyQt5 GUI Application

A professional, well-organized PyQt5 application for anonymizing DICOM medical images with single file and batch processing capabilities.

## Features

✨ **Multi-tab Interface**
- **Batch Processing**: Anonymize multiple DICOM files from a directory
- **Single File**: Process individual DICOM files
- **Metadata Explorer**: View and inspect DICOM metadata tags
- **Verification**: Compare original vs anonymized files
- **Settings**: Configure anonymization rules

🔒 **Comprehensive Anonymization**
- Remove patient personal information
- Strip physician and facility information
- Remove/shift dates (keep year only)
- Generate new random UIDs
- Remove manufacturer-specific private tags
- Preserve pixel data and image quality

⚡ **Performance**
- Multi-threaded batch processing
- Real-time progress tracking
- Preserves folder structure during batch processing
- Handles large datasets efficiently

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Quick Start

1. **Clone/Download the project**
   ```bash
   cd DICOM-anonymizer
   ```

2. **Install dependencies**
   ```bash
   pip install pydicom PyQt5 tqdm
   ```

3. **Run the application**
   ```bash
   python dicom_anonymizer_app.py
   ```

   Or use the launcher script:
   ```bash
   python run_app.py
   ```

## Usage

### Batch Processing Tab

1. **Set Input Directory**: Select folder containing DICOM files (`.dcm`)
2. **Set Output Directory**: Choose where anonymized files will be saved
3. **Click "Start Anonymization"**: Process begins with real-time progress
4. **Monitor Status**: View processing log with file-by-file updates

**Features:**
- Preserves original folder structure
- Displays progress bar and current file being processed
- Shows summary statistics upon completion
- Logs any errors encountered

### Single File Tab

1. **Load DICOM**: Browse and select a DICOM file
2. **View Info**: See file details and sample metadata
3. **Anonymize & Save**: Process file and save to output location

**Features:**
- Real-time file information display
- Shows number of tags before anonymization
- Confirms successful anonymization with tag count

### Metadata Explorer Tab

1. **Select DICOM File**: Browse for any DICOM file
2. **Click "Load Metadata"**: Display all tags in table format
3. **View Details**: See Tag, Name, and Value columns

**Features:**
- First 100 tags displayed in sortable table
- Easy inspection of file structure
- Useful for understanding DICOM content

### Verification Tab

1. **Select Original File**: Browse for original DICOM
2. **Select Anonymized File**: Browse for processed DICOM
3. **Click "Compare & Verify"**: Generate detailed comparison report

**Report Includes:**
- Tags removed count
- Sensitive information status
- Pixel data verification
- List of any remaining sensitive tags

### Settings Tab

- **Remove Patient Name**: Toggle patient identification removal
- **Remove/Shift Dates**: Enable date modification
- **Remove Physician Information**: Strip healthcare provider details
- **Generate New UIDs**: Create new random identifiers
- **Remove Private Tags**: Eliminate manufacturer-specific tags

## Application Structure

```
dicom_anonymizer_app.py
├── DicomAnonymizer (Core Logic)
│   ├── load_dicom()
│   ├── find_dicom_files()
│   └── anonymize_dicom()
├── AnonymizationWorker (Threading)
│   └── run() - Multi-threaded processing
└── DicomAnonymizerApp (GUI)
    ├── create_batch_tab()
    ├── create_single_tab()
    ├── create_metadata_tab()
    ├── create_verify_tab()
    ├── create_settings_tab()
    └── Event Handlers
```

## Anonymization Rules

### Removed Tags (30+)
- Patient Information: Name, ID, Birth Date, Sex, Address, Phone
- Study/Series Data: UIDs, Dates, Times, Descriptions
- Physician Info: Names, Institution, Department
- Device Info: Manufacturer, Model, Serial Number
- Private Tags: Manufacturer-specific extensions

### Replaced Tags
- PatientName → "ANONYMIZED"
- PatientID → "ANON-ID-001"
- PhysicianNames → "ANONYMIZED"
- InstitutionName → "ANONYMIZED"

### Date Modifications
- Original format: YYYYMMDD
- Modified format: YYYY0101 (keeps year, resets to Jan 1)

### UID Generation
- New random UIDs for:
  - SOPInstanceUID
  - StudyInstanceUID
  - SeriesInstanceUID

## Error Handling

✓ Invalid file path handling
✓ Missing DICOM files detection
✓ Permission error management
✓ Corrupted file detection
✓ Detailed error logging

## Performance Considerations

- **Batch Processing**: ~50-100 files/minute (depends on file size and system)
- **Memory Usage**: Minimal - processes one file at a time
- **Threading**: Non-blocking UI during long operations
- **Output**: Maintains original folder structure

## Troubleshooting

### Application won't start
```bash
# Reinstall PyQt5
pip install --upgrade PyQt5

# Check Python version
python --version  # Must be 3.7+
```

### DICOM files not found
- Ensure files have `.dcm` extension
- Check folder permissions
- Verify path is correct

### Anonymization fails
- Check output directory permissions
- Ensure input directory exists
- Verify disk space available

### Slow performance
- Close other applications
- Use SSD for output (faster writes)
- Process in smaller batches

## Example Workflow

1. **Prepare Data**: Gather DICOM files in `raw/train` folder
2. **Launch App**: `python dicom_anonymizer_app.py`
3. **Batch Process**: 
   - Input: `C:\path\to\raw\train`
   - Output: `C:\path\to\anonymized_output`
   - Click "Start Anonymization"
4. **Verify Results**: Use Verification tab to check anonymization
5. **Export**: Use anonymized files for research/sharing

## Default Directories

The application comes pre-configured with:
- **Input**: `DICOM-anonymizer\raw\train`
- **Output**: `DICOM-anonymizer\anonymized_output`

These can be changed in the GUI.

## Security Considerations

⚠️ **Important**: 
- This tool removes/anonymizes metadata but does NOT encrypt pixel data
- Always verify results with the Verification tab before using
- Keep backup of original files
- Follow HIPAA/GDPR requirements for your use case
- Consider additional encryption if required

## License

This application is provided as-is for medical image anonymization purposes.

## Support

For issues or questions:
1. Check Troubleshooting section
2. Review error logs in Status Log
3. Use Metadata Explorer to inspect file structure
4. Verify files with Verification tab

---

**Version**: 1.0
**Last Updated**: December 2025
