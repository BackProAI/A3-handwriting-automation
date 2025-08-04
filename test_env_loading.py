#!/usr/bin/env python3
"""
Test environment variable loading for A3 OCR system
"""

import os
from sectioned_gpt4o_ocr import SectionedGPT4oOCR

print('🧪 Testing A3 OCR Environment Loading...')
print('='*50)

print('\n📋 Environment Variables:')
print(f'   OPENAI_API_KEY present: {"OPENAI_API_KEY" in os.environ}')
print(f'   GITHUB_TOKEN present: {"GITHUB_TOKEN" in os.environ}')

if "OPENAI_API_KEY" in os.environ:
    api_key = os.environ["OPENAI_API_KEY"]
    if api_key == "your_openai_api_key_here":
        print(f'   ⚠️ OPENAI_API_KEY is still placeholder')
    else:
        print(f'   ✅ OPENAI_API_KEY configured (starts with: {api_key[:8]}...)')

if "GITHUB_TOKEN" in os.environ:
    github_token = os.environ["GITHUB_TOKEN"]
    if github_token == "your_github_token_here":
        print(f'   ⚠️ GITHUB_TOKEN is still placeholder')
    else:
        print(f'   ✅ GITHUB_TOKEN configured (starts with: {github_token[:8]}...)')

print('\n🔧 Testing OCR Initialization:')
try:
    ocr = SectionedGPT4oOCR()
    print('✅ OCR initialized successfully!')
    print(f'   📂 Section config: {ocr.section_config_path}')
    print(f'   🎯 Sections loaded: {len(ocr.sections) if ocr.sections else 0}')
except Exception as e:
    print(f'❌ OCR initialization failed: {e}')

print('\n💡 Next Steps:')
print('   1. Edit .env file and add your actual API keys')
print('   2. OpenAI API key: Get from https://platform.openai.com/api-keys')
print('   3. GitHub token: Get from https://github.com/settings/tokens')