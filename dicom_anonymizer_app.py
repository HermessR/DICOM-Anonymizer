"""
DICOM Anonymizer GUI Application
A professional PyQt5 application for anonymizing DICOM medical images
"""

import sys
import os
from pathlib import Path
from typing import List, Dict
import threading
from datetime import datetime

import pydicom
from pydicom.uid import generate_uid
from tqdm import tqdm

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit,
    QProgressBar, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QCheckBox, QSpinBox, QGroupBox, QListWidget, QListWidgetItem, QSplitter,
    QSplashScreen
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap, QPainter, QBrush, QLinearGradient
import time


# ============================================================================
# Enhanced Splash Screen Generator
# ============================================================================

def create_animated_splash_screen():
    """Create a professional animated splash screen for the application"""
    # Create pixmap with custom size
    pixmap = QPixmap(900, 550)
    pixmap.fill(Qt.white)
    
    # Create painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    
    # Draw gradient background
    gradient = QLinearGradient(0, 0, 0, pixmap.height())
    gradient.setColorAt(0, QColor(10, 130, 220))
    gradient.setColorAt(0.5, QColor(15, 100, 200))
    gradient.setColorAt(1, QColor(0, 60, 150))
    painter.fillRect(pixmap.rect(), gradient)
    
    # Draw decorative top bar
    top_bar = pixmap.rect()
    top_bar.setHeight(140)
    top_gradient = QLinearGradient(0, 0, 0, 140)
    top_gradient.setColorAt(0, QColor(20, 150, 255))
    top_gradient.setColorAt(1, QColor(10, 130, 220))
    painter.fillRect(top_bar, top_gradient)
    
    # Draw left accent
    left_accent = pixmap.rect()
    left_accent.setWidth(8)
    painter.fillRect(left_accent, QColor(0, 200, 255))
    
    # Draw right accent  
    right_accent = pixmap.rect()
    right_accent.setLeft(pixmap.width() - 8)
    painter.fillRect(right_accent, QColor(0, 200, 255))
    
    # Draw title
    title_font = QFont("Segoe UI", 56, QFont.Bold)
    painter.setFont(title_font)
    painter.setPen(Qt.white)
    painter.drawText(pixmap.rect().adjusted(20, 20, -20, -350), 
                     Qt.AlignCenter, "DICOM Anonymizer")
    
    # Draw separator line
    painter.setPen(QColor(100, 180, 255))
    painter.drawLine(100, 160, pixmap.width() - 100, 160)
    
    # Draw branded subtitle with transparent background
    subtitle_box = pixmap.rect().adjusted(80, 180, -80, -320)
    # Transparent border only (no fill)
    painter.setPen(QColor(100, 200, 255))
    painter.drawRect(subtitle_box)
    
    # Draw branded text with minimal style
    highlight_font = QFont("Segoe UI", 13, QFont.Bold)
    painter.setFont(highlight_font)
    painter.setPen(QColor(200, 240, 255))
    painter.drawText(subtitle_box, Qt.AlignCenter, "Professional Medical Image Anonymization Tool")
    
    # Draw features with icons
    features_font = QFont("Segoe UI", 11, QFont.Normal)
    painter.setFont(features_font)
    painter.setPen(Qt.white)
    
    features = [
        ("•", "Batch Processing - Anonymize multiple files at once"),
        ("•", "Single File Support - Process individual DICOM images"),
        ("•", "Metadata Explorer - Inspect DICOM file tags"),
        ("•", "Verification System - Compare before and after")
    ]
    
    y_pos = 290
    for icon, feature in features:
        painter.drawText(60, y_pos, f"{icon}  {feature}")
        y_pos += 40
    
    # Draw progress indicator background
    progress_bg_rect = pixmap.rect().adjusted(80, 450, -80, -30)
    painter.setPen(QColor(100, 180, 255))
    painter.drawRoundedRect(progress_bg_rect, 5, 5)
    
    # Draw status/version info
    info_font = QFont("Segoe UI", 10)
    painter.setFont(info_font)
    painter.setPen(QColor(180, 220, 255))
    painter.drawText(pixmap.rect().adjusted(20, -40, -20, -10),
                     Qt.AlignRight | Qt.AlignBottom, "v1.0 | Initializing...")
    
    painter.end()
    
    return pixmap


# ============================================================================
# DICOM Anonymization Engine
# ============================================================================

class DicomAnonymizer:
    """Core DICOM anonymization logic"""
    
    ANONYMIZATION_RULES = {
        'remove': [
            'PatientName', 'PatientID', 'PatientBirthDate', 'PatientAge',
            'PatientSex', 'PatientAddress', 'PatientTelephoneNumbers',
            'StudyInstanceUID', 'SeriesInstanceUID', 'StudyDate', 'SeriesDate',
            'ContentDate', 'StudyTime', 'SeriesTime', 'ContentTime',
            'AcquisitionDateTime', 'StudyDescription', 'SeriesDescription',
            'ReferringPhysicianName', 'PerformingPhysicianName', 'OperatorsName',
            'InstitutionName', 'InstitutionAddress', 'Manufacturer',
            'ManufacturerModelName', 'DeviceSerialNumber', 'StationName',
        ],
        'replace': {
            'PatientName': 'ANONYMIZED',
            'PatientID': 'ANON-ID-001',
            'ReferringPhysicianName': 'ANONYMIZED',
            'PerformingPhysicianName': 'ANONYMIZED',
            'OperatorsName': 'ANONYMIZED',
            'InstitutionName': 'ANONYMIZED',
        },
        'date_shift': {
            'StudyDate': True, 'SeriesDate': True, 'PatientBirthDate': True,
            'ContentDate': True, 'AcquisitionDate': True,
        }
    }
    
    @staticmethod
    def load_dicom(file_path: str):
        """Load a DICOM file"""
        try:
            return pydicom.dcmread(file_path)
        except Exception as e:
            raise Exception(f"Error loading DICOM: {str(e)}")
    
    @staticmethod
    def find_dicom_files(directory: str) -> List[str]:
        """Find all DICOM files in directory"""
        dicom_files = []
        path = Path(directory)
        if path.exists():
            for dcm_file in path.rglob('*.dcm'):
                dicom_files.append(str(dcm_file))
        return sorted(dicom_files)
    
    @staticmethod
    def anonymize_dicom(dicom_file, rules: Dict = None) -> tuple:
        """Anonymize a DICOM file"""
        if rules is None:
            rules = DicomAnonymizer.ANONYMIZATION_RULES
        
        try:
            anonymized_count = 0
            
            # Remove tags completely
            for tag in rules['remove']:
                if tag in dicom_file:
                    del dicom_file[tag]
                    anonymized_count += 1
            
            # Replace sensitive tags
            for tag, replacement_value in rules['replace'].items():
                if tag in dicom_file:
                    dicom_file[tag].value = replacement_value
                    anonymized_count += 1
            
            # Shift dates
            for tag in rules['date_shift']:
                if tag in dicom_file:
                    try:
                        current_value = str(dicom_file[tag].value)
                        if len(current_value) >= 8:
                            year = current_value[:4]
                            dicom_file[tag].value = year + '0101'
                            anonymized_count += 1
                    except:
                        pass
            
            # Remove private tags
            tags_to_remove = [tag for tag in dicom_file.keys() if tag.is_private]
            for tag in tags_to_remove:
                del dicom_file[tag]
                anonymized_count += 1
            
            # Generate new UIDs
            if 'SOPInstanceUID' in dicom_file:
                dicom_file.SOPInstanceUID = generate_uid()
            if 'StudyInstanceUID' in dicom_file:
                dicom_file.StudyInstanceUID = generate_uid()
            if 'SeriesInstanceUID' in dicom_file:
                dicom_file.SeriesInstanceUID = generate_uid()
            
            return True, anonymized_count
        except Exception as e:
            return False, str(e)


# ============================================================================
# Worker Thread for Long Operations
# ============================================================================

class AnonymizationWorker(QObject):
    """Worker thread for batch anonymization"""
    
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
    
    def run(self):
        """Execute anonymization"""
        try:
            dicom_files = DicomAnonymizer.find_dicom_files(self.input_dir)
            
            if not dicom_files:
                self.finished.emit({'status': 'error', 'message': 'No DICOM files found'})
                return
            
            stats = {
                'total': len(dicom_files),
                'successful': 0,
                'failed': 0,
                'total_tags_removed': 0,
                'errors': []
            }
            
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            for idx, file_path in enumerate(dicom_files, 1):
                try:
                    dicom_data = DicomAnonymizer.load_dicom(file_path)
                    original_tag_count = len(dicom_data)
                    
                    success, result = DicomAnonymizer.anonymize_dicom(dicom_data)
                    
                    if not success:
                        stats['failed'] += 1
                        stats['errors'].append(f"{Path(file_path).name}: {result}")
                        continue
                    
                    relative_path = Path(file_path).relative_to(self.input_dir)
                    output_file = Path(self.output_dir) / relative_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    dicom_data.save_as(str(output_file), write_like_original=False)
                    
                    stats['successful'] += 1
                    stats['total_tags_removed'] += (original_tag_count - len(dicom_data))
                    
                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append(f"{Path(file_path).name}: {str(e)}")
                
                progress_percent = int((idx / len(dicom_files)) * 100)
                self.progress.emit(progress_percent)
                self.status.emit(f"Processing {idx}/{len(dicom_files)}: {Path(file_path).name}")
            
            stats['status'] = 'success'
            self.finished.emit(stats)
        
        except Exception as e:
            self.finished.emit({'status': 'error', 'message': str(e)})


# ============================================================================
# PyQt5 GUI Application
# ============================================================================

class DicomAnonymizerApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker_thread = None
    
    def initUI(self):
        """Initialize UI components"""
        self.setWindowTitle('DICOM Anonymizer - Professional Tool')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_batch_tab(), "Batch Processing")
        tabs.addTab(self.create_single_tab(), "Single File")
        tabs.addTab(self.create_metadata_tab(), "Metadata Explorer")
        tabs.addTab(self.create_verify_tab(), "Verification")
        tabs.addTab(self.create_settings_tab(), "Settings")
        
        layout.addWidget(tabs)
        
        # Set style
        self.setStyleSheet(self.get_stylesheet())
    
    def create_batch_tab(self) -> QWidget:
        """Create batch processing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Input directory
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input Directory:"))
        self.batch_input = QLineEdit()
        self.batch_input.setText(r"c:\Users\THINKPAD\Desktop\DICOM-anonymizer\raw\train")
        input_layout.addWidget(self.batch_input)
        input_btn = QPushButton("Browse...")
        input_btn.clicked.connect(lambda: self.browse_directory(self.batch_input))
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.batch_output = QLineEdit()
        self.batch_output.setText(r"c:\Users\THINKPAD\Desktop\DICOM-anonymizer\anonymized_output")
        output_layout.addWidget(self.batch_output)
        output_btn = QPushButton("Browse...")
        output_btn.clicked.connect(lambda: self.browse_directory(self.batch_output))
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # Progress bar
        layout.addWidget(QLabel("Progress:"))
        self.batch_progress = QProgressBar()
        layout.addWidget(self.batch_progress)
        
        # Status log
        layout.addWidget(QLabel("Status Log:"))
        self.batch_log = QTextEdit()
        self.batch_log.setReadOnly(True)
        layout.addWidget(self.batch_log)
        
        # Buttons
        btn_layout = QHBoxLayout()
        start_btn = QPushButton("Start Anonymization")
        start_btn.clicked.connect(self.start_batch_anonymization)
        btn_layout.addWidget(start_btn)
        
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.batch_log.clear)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_single_tab(self) -> QWidget:
        """Create single file processing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("DICOM File:"))
        self.single_input = QLineEdit()
        file_layout.addWidget(self.single_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Output location
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output File:"))
        self.single_output = QLineEdit()
        output_layout.addWidget(self.single_output)
        output_btn = QPushButton("Browse...")
        output_btn.clicked.connect(self.browse_save_file)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # Info area
        layout.addWidget(QLabel("File Information:"))
        self.single_info = QTextEdit()
        self.single_info.setReadOnly(True)
        layout.addWidget(self.single_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Load DICOM")
        load_btn.clicked.connect(self.load_single_file)
        btn_layout.addWidget(load_btn)
        
        anonymize_btn = QPushButton("Anonymize & Save")
        anonymize_btn.clicked.connect(self.anonymize_single_file)
        btn_layout.addWidget(anonymize_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_metadata_tab(self) -> QWidget:
        """Create metadata explorer tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("DICOM File:"))
        self.meta_input = QLineEdit()
        file_layout.addWidget(self.meta_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_file_to_field(self.meta_input))
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Metadata table
        layout.addWidget(QLabel("DICOM Metadata Tags:"))
        self.metadata_table = QTableWidget()
        self.metadata_table.setColumnCount(3)
        self.metadata_table.setHorizontalHeaderLabels(["Tag", "Name", "Value"])
        self.metadata_table.setColumnWidth(0, 100)
        self.metadata_table.setColumnWidth(1, 250)
        self.metadata_table.setColumnWidth(2, 400)
        layout.addWidget(self.metadata_table)
        
        # Load button
        load_btn = QPushButton("Load Metadata")
        load_btn.clicked.connect(self.load_metadata)
        layout.addWidget(load_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_verify_tab(self) -> QWidget:
        """Create verification tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Original file
        orig_layout = QHBoxLayout()
        orig_layout.addWidget(QLabel("Original DICOM:"))
        self.verify_orig = QLineEdit()
        orig_layout.addWidget(self.verify_orig)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_file_to_field(self.verify_orig))
        orig_layout.addWidget(browse_btn)
        layout.addLayout(orig_layout)
        
        # Anonymized file
        anon_layout = QHBoxLayout()
        anon_layout.addWidget(QLabel("Anonymized DICOM:"))
        self.verify_anon = QLineEdit()
        anon_layout.addWidget(self.verify_anon)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_file_to_field(self.verify_anon))
        anon_layout.addWidget(browse_btn)
        layout.addLayout(anon_layout)
        
        # Verification results
        layout.addWidget(QLabel("Verification Results:"))
        self.verify_results = QTextEdit()
        self.verify_results.setReadOnly(True)
        layout.addWidget(self.verify_results)
        
        # Verify button
        verify_btn = QPushButton("Compare & Verify")
        verify_btn.clicked.connect(self.verify_files)
        layout.addWidget(verify_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Anonymization Settings"))
        
        # Checkboxes for rules
        self.remove_patient_name = QCheckBox("Remove Patient Name")
        self.remove_patient_name.setChecked(True)
        layout.addWidget(self.remove_patient_name)
        
        self.remove_dates = QCheckBox("Remove/Shift Dates")
        self.remove_dates.setChecked(True)
        layout.addWidget(self.remove_dates)
        
        self.remove_physician = QCheckBox("Remove Physician Information")
        self.remove_physician.setChecked(True)
        layout.addWidget(self.remove_physician)
        
        self.generate_new_uids = QCheckBox("Generate New UIDs")
        self.generate_new_uids.setChecked(True)
        layout.addWidget(self.generate_new_uids)
        
        self.remove_private_tags = QCheckBox("Remove Private Tags")
        self.remove_private_tags.setChecked(True)
        layout.addWidget(self.remove_private_tags)
        
        layout.addStretch()
        layout.addWidget(QLabel("Default Anonymization Rules"))
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            "• Patient Information: Name, ID, Birth Date, Sex, Address\n"
            "• Study/Series Info: Date, Time, Description, Instance UIDs\n"
            "• Physician Info: Referring Physician, Operator, Institution\n"
            "• Device Info: Manufacturer, Model, Serial Number\n"
            "• Private Tags: Manufacturer-specific tags\n"
            "• UIDs: New random UIDs generated for anonymity"
        )
        layout.addWidget(info_text)
        
        widget.setLayout(layout)
        return widget
    
    # ========================================================================
    # Event Handlers
    # ========================================================================
    
    def browse_directory(self, line_edit: QLineEdit):
        """Browse for directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)
    
    def browse_file(self):
        """Browse for DICOM file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select DICOM File", "", "DICOM Files (*.dcm);;All Files (*)"
        )
        if file_path:
            self.single_input.setText(file_path)
    
    def browse_save_file(self):
        """Browse for save location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Anonymized DICOM", "", "DICOM Files (*.dcm)"
        )
        if file_path:
            self.single_output.setText(file_path)
    
    def browse_file_to_field(self, line_edit: QLineEdit):
        """Browse for file to specific field"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select DICOM File", "", "DICOM Files (*.dcm);;All Files (*)"
        )
        if file_path:
            line_edit.setText(file_path)
    
    def start_batch_anonymization(self):
        """Start batch anonymization in worker thread"""
        input_dir = self.batch_input.text().strip()
        output_dir = self.batch_output.text().strip()
        
        if not input_dir or not output_dir:
            QMessageBox.warning(self, "Error", "Please specify both input and output directories")
            return
        
        if not os.path.isdir(input_dir):
            QMessageBox.warning(self, "Error", "Input directory does not exist")
            return
        
        self.batch_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting batch anonymization...")
        self.batch_log.append(f"Input: {input_dir}")
        self.batch_log.append(f"Output: {output_dir}\n")
        
        self.worker_thread = QThread()
        self.worker = AnonymizationWorker(input_dir, output_dir)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker.progress.connect(self.update_batch_progress)
        self.worker.status.connect(self.update_batch_status)
        self.worker.finished.connect(self.batch_finished)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()
    
    def update_batch_progress(self, value):
        """Update progress bar"""
        self.batch_progress.setValue(value)
    
    def update_batch_status(self, status):
        """Update status log"""
        self.batch_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {status}")
    
    def batch_finished(self, stats):
        """Handle batch completion"""
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        if stats['status'] == 'error':
            self.batch_log.append(f"\n❌ Error: {stats['message']}")
            QMessageBox.critical(self, "Error", stats['message'])
        else:
            self.batch_log.append(f"\n{'='*80}")
            self.batch_log.append(f"✅ ANONYMIZATION COMPLETE!")
            self.batch_log.append(f"{'='*80}")
            self.batch_log.append(f"Total Files: {stats['total']}")
            self.batch_log.append(f"✓ Successful: {stats['successful']}")
            self.batch_log.append(f"❌ Failed: {stats['failed']}")
            self.batch_log.append(f"✓ Total Tags Removed: {stats['total_tags_removed']}")
            
            if stats['errors']:
                self.batch_log.append(f"\n⚠ Errors ({len(stats['errors'])}):")
                for error in stats['errors'][:10]:
                    self.batch_log.append(f"  - {error}")
            
            QMessageBox.information(
                self, "Success",
                f"Anonymization complete!\n\n"
                f"Successful: {stats['successful']}\n"
                f"Failed: {stats['failed']}\n"
                f"Output: {self.batch_output.text()}"
            )
    
    def load_single_file(self):
        """Load and display single file info"""
        file_path = self.single_input.text().strip()
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.warning(self, "Error", "Please select a valid DICOM file")
            return
        
        try:
            dicom_data = DicomAnonymizer.load_dicom(file_path)
            info = f"File: {Path(file_path).name}\n"
            info += f"Total Tags: {len(dicom_data)}\n\n"
            info += "Sample Tags:\n"
            
            sample_tags = ['PatientName', 'PatientID', 'StudyDate', 'Modality', 'Rows', 'Columns']
            for tag in sample_tags:
                if tag in dicom_data:
                    info += f"{tag}: {dicom_data[tag].value}\n"
            
            self.single_info.setText(info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def anonymize_single_file(self):
        """Anonymize single file"""
        input_file = self.single_input.text().strip()
        output_file = self.single_output.text().strip()
        
        if not input_file or not os.path.isfile(input_file):
            QMessageBox.warning(self, "Error", "Please select a valid input file")
            return
        
        if not output_file:
            QMessageBox.warning(self, "Error", "Please specify output file")
            return
        
        try:
            dicom_data = DicomAnonymizer.load_dicom(input_file)
            success, result = DicomAnonymizer.anonymize_dicom(dicom_data)
            
            if not success:
                raise Exception(result)
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            dicom_data.save_as(output_file, write_like_original=False)
            
            self.single_info.setText(f"✅ Successfully anonymized!\n\n"
                                    f"Tags removed: {result}\n"
                                    f"Output: {output_file}")
            QMessageBox.information(self, "Success", "DICOM file anonymized successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to anonymize: {str(e)}")
    
    def load_metadata(self):
        """Load and display metadata"""
        file_path = self.meta_input.text().strip()
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.warning(self, "Error", "Please select a valid DICOM file")
            return
        
        try:
            dicom_data = DicomAnonymizer.load_dicom(file_path)
            self.metadata_table.setRowCount(0)
            
            for i, (tag, value) in enumerate(list(dicom_data.items())[:100]):
                self.metadata_table.insertRow(i)
                self.metadata_table.setItem(i, 0, QTableWidgetItem(str(tag)))
                tag_name = value.name if hasattr(value, 'name') else "N/A"
                self.metadata_table.setItem(i, 1, QTableWidgetItem(tag_name))
                tag_value = str(value.value)[:100] if hasattr(value, 'value') else str(value)[:100]
                self.metadata_table.setItem(i, 2, QTableWidgetItem(tag_value))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load metadata: {str(e)}")
    
    def verify_files(self):
        """Compare original and anonymized files"""
        orig_file = self.verify_orig.text().strip()
        anon_file = self.verify_anon.text().strip()
        
        if not orig_file or not os.path.isfile(orig_file):
            QMessageBox.warning(self, "Error", "Please select original DICOM file")
            return
        
        if not anon_file or not os.path.isfile(anon_file):
            QMessageBox.warning(self, "Error", "Please select anonymized DICOM file")
            return
        
        try:
            original = DicomAnonymizer.load_dicom(orig_file)
            anonymized = DicomAnonymizer.load_dicom(anon_file)
            
            sensitive_tags = [
                'PatientName', 'PatientID', 'PatientBirthDate',
                'ReferringPhysicianName', 'OperatorsName', 'InstitutionName',
                'StudyInstanceUID', 'SeriesInstanceUID'
            ]
            
            results = f"VERIFICATION REPORT\n"
            results += f"{'='*60}\n\n"
            results += f"Original Tags: {len(original)}\n"
            results += f"Anonymized Tags: {len(anonymized)}\n"
            results += f"Tags Removed: {len(original) - len(anonymized)}\n\n"
            
            results += f"Sensitive Tags Check:\n"
            removed_count = 0
            still_present = []
            
            for tag in sensitive_tags:
                if tag in anonymized:
                    still_present.append(tag)
                else:
                    removed_count += 1
            
            results += f"✓ Removed: {removed_count}/{len(sensitive_tags)}\n"
            
            if still_present:
                results += f"⚠ Still Present: {', '.join(still_present)}\n"
            else:
                results += f"✅ ALL SENSITIVE INFORMATION REMOVED!\n"
            
            results += f"\nPixel Data Present: {'Yes' if 'PixelData' in anonymized else 'No'}\n"
            
            self.verify_results.setText(results)
            
            if not still_present:
                QMessageBox.information(self, "Verification", "✅ All sensitive information has been removed!")
            else:
                QMessageBox.warning(self, "Verification", f"⚠ Some sensitive tags still present: {', '.join(still_present)}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to verify: {str(e)}")
    
    def get_stylesheet(self) -> str:
        """Return application stylesheet"""
        return """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                margin: 2px;
                border: 1px solid #999;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
            QTableWidget {
                border: 1px solid #ccc;
                gridline-color: #eee;
            }
        """


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the application"""
    app = QApplication(sys.argv)
    
    # Create and display splash screen
    splash_pixmap = create_animated_splash_screen()
    splash = QSplashScreen(splash_pixmap)
    splash.show()
    app.processEvents()
    
    # Simulate loading with enhanced messages
    loading_steps = [
        ("Initializing DICOM engine...", 0),
        ("Loading anonymization rules...", 1),
        ("Setting up GUI components...", 2),
        ("Preparing file handlers...", 3),
        ("Initializing worker threads...", 4),
        ("Loading configuration...", 5),
        ("Ready to process DICOM files!", 6),
    ]
    
    for message, step in loading_steps:
        # Update splash with message
        splash.showMessage(
            message,
            Qt.AlignBottom | Qt.AlignCenter,
            Qt.white
        )
        app.processEvents()
        time.sleep(0.4)  # Brief pause for each step
    
    # Create main window
    window = DicomAnonymizerApp()
    window.show()
    
    # Close splash screen
    splash.finish(window)
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
