# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('A3_templates', 'A3_templates'), ('processed_documents', 'processed_documents'), ('custom_field_positions.json', '.'), ('app_config.json', '.'), ('version.txt', '.'), ('a3_template_processor.py', '.'), ('a3_sectioned_automation.py', '.'), ('sectioned_gpt4o_ocr.py', '.'), ('section_definition_tool.py', '.'), ('field_positioning_tool.py', '.'), ('create_pdf_template.py', '.'), ('manual_page_order_tool.py', '.')],
    hiddenimports=['tkinter', 'tkinter.filedialog', 'tkinter.messagebox', 'PIL', 'fitz', 'requests', 'openai'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='A3_Automation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
