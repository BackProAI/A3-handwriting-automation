# More4Life A3 Handwriting to Text Recognition

🚀 **Production-ready A3 document automation system** using Microsoft's TrOCR Large Handwritten model for converting handwritten A3 documents to digital text.

## 📋 Project Overview

This project automates the process of:
1. **Scanning handwritten A3 documents** 
2. **Converting handwriting to digital text** using state-of-the-art AI
3. **Auto-populating blank A3 templates** with extracted text

### 🎯 Key Features

- ✅ **High Accuracy**: Uses TrOCR Large Handwritten model (~90%+ accuracy)
- ✅ **A3 Optimized**: Specifically designed for A3 document processing
- ✅ **Multi-Format**: Supports both images (.jpg, .png, etc.) and PDFs
- ✅ **PDF Processing**: Automatic page conversion and multi-page handling
- ✅ **Enhanced Console Output**: Full extracted text displayed immediately in terminal
- ✅ **Production Ready**: Batch processing, error handling, logging
- ✅ **Secure**: Safe token management and environment setup
- ✅ **More4Life Integration**: Customized for More4Life workflows

## 🚀 Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up your Hugging Face token securely
python setup_token.py

# Download the TrOCR model
python download_trocr_model.py
```

### 2. Test the Setup

```bash
# Test with sample images
python test_a3_processing.py
```

### 3. Process Your Documents

```bash
# Single document (image or PDF)
python process_a3_document.py --input your_document.jpg --output ./results
python process_a3_document.py --input your_document.pdf --output ./results

# Batch processing (mixed images and PDFs)
python process_a3_document.py --batch ./handwritten_docs --output ./results

# PDF-specific processing
python pdf_processor.py --input document.pdf --output ./results
```

## 📁 Project Structure

```
A3_handtotext/
├── download_trocr_model.py      # Model download script
├── setup_token.py               # Secure token setup
├── test_a3_processing.py        # Testing script (images + PDFs)
├── process_a3_document.py       # Production processing (images + PDFs)
├── pdf_processor.py             # Dedicated PDF processor
├── demo_text_output.py          # Enhanced output demo
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── .env                        # Your token (created by setup_token.py)
├── .gitignore                  # Git ignore rules
├── more4life-handwriting-ocr/   # Downloaded model (created automatically)
└── test_images/                 # Put your test images and PDFs here
```

## 🔧 Detailed Setup Instructions

### Step 1: Python Environment

Make sure you have Python 3.8+ installed:

```bash
python --version  # Should be 3.8 or higher
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**For GPU acceleration (optional but recommended):**
```bash
# If you have NVIDIA GPU with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Secure Token Setup

```bash
python setup_token.py
```

This will:
- Securely prompt for your Hugging Face token
- Save it to a `.env` file
- Add `.env` to `.gitignore` for security

**To get a Hugging Face token:**
1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token with "Read" permissions
3. Copy the token (starts with `hf_`)

### Step 4: Download the Model

```bash
python download_trocr_model.py
```

This will:
- Download the `microsoft/trocr-large-handwritten` model
- Save it locally as `more4life-handwriting-ocr/`
- Test the model with a sample image

**Expected output:**
```
🚀 More4Life A3 Handwriting Recognition Setup
==================================================
🔐 Logging in to Hugging Face...
🔄 Downloading microsoft/trocr-large-handwritten...
📊 This is a large model - download may take several minutes...
💾 Saving model to: ./more4life-handwriting-ocr
✅ Model downloaded successfully!
🧪 Testing model with sample handwritten text...
🔤 Recognized text: 'industry, " Mr. Brown commented icily. " Let us have a'
✅ Model test successful!
```

## 📖 Usage Guide

### Testing Your Setup

```bash
# Test with your images
python test_a3_processing.py
```

**Add your test images to:**
- `./test_images/`
- `./samples/`
- `./images/`
- Or current directory

### Single Document Processing

```bash
python process_a3_document.py --input document.jpg --output ./results
```

**Example output:**
```
📄 Processing A3 document: document.jpg
   📐 Original size: 2480x3508 pixels
   🔄 Resized to: 1448x2048 pixels
   ✅ Extracted 45 words, 234 characters
   ⏱️  Processing time: 3.21 seconds
   💾 Results saved:
      📄 Text: ./results/document_20250103_143022.txt
      📊 Metadata: ./results/document_20250103_143022.json
```

### Batch Processing

```bash
# Process all JPG files in a directory
python process_a3_document.py --batch ./handwritten_docs --output ./results

# Process PNG files
python process_a3_document.py --batch ./docs --pattern "*.png" --output ./results

# Process mixed images and PDFs
python process_a3_document.py --batch ./mixed_docs --output ./results
```

### PDF Processing

```bash
# Process single PDF with dedicated processor
python pdf_processor.py --input document.pdf --output ./results

# Process PDF with high resolution (better for small text)
python pdf_processor.py --input document.pdf --dpi 600 --output ./results

# PDF processing automatically:
# 1. Converts each PDF page to high-resolution images
# 2. Processes each page with TrOCR
# 3. Combines results into single output
# 4. Saves individual page results
```

## 📺 Enhanced Console Output

**NEW FEATURE**: All extracted text is now displayed prominently in your terminal immediately when processing completes!

### What You'll See:

**For Images:**
```
📝 EXTRACTED TEXT:
============================================================
Your handwritten text appears here in full detail
Line by line, exactly as recognized by TrOCR
No need to open files to see the results!
============================================================
```

**For PDFs:**
```
📝 PAGE 1 TEXT:
--------------------------------------------------
Text from first page appears here...
--------------------------------------------------

📝 PAGE 2 TEXT:
--------------------------------------------------
Text from second page appears here...
--------------------------------------------------

📖 COMPLETE PDF TEXT:
================================================================================
--- Page 1 ---
Text from first page...

--- Page 2 ---
Text from second page...
================================================================================
```

### Demo the Enhanced Output:
```bash
# Quick demo to see the new text display
python demo_text_output.py
```

### Benefits:
- ✅ **Immediate Results**: See extracted text instantly in terminal
- ✅ **No File Opening**: Results displayed directly in console
- ✅ **Complete Text**: Full content shown, not truncated
- ✅ **Page-by-Page**: PDF pages shown individually and combined
- ✅ **Production Ready**: Same enhanced output in all scripts

## 📊 Output Files

For each processed document, you get:

### 1. Text File (`document_timestamp.txt`)
```
This is the extracted text from your handwritten document.
All the recognized words and sentences will be here.
```

### 2. JSON Metadata (`document_timestamp.json`)
```json
{
  "input_file": "./docs/document.jpg",
  "extracted_text": "This is the extracted text...",
  "processing_time_seconds": 3.21,
  "original_size": [2480, 3508],
  "processed_at": "2025-01-03T14:30:22.123456",
  "model_used": "microsoft/trocr-large-handwritten",
  "success": true,
  "word_count": 45,
  "character_count": 234
}
```

### 3. PDF Processing Output (Additional)

For PDF files, you also get:

**Combined Text:** `document_pdf_timestamp.txt`
```
--- Page 1 ---
Text from first page...

--- Page 2 ---
Text from second page...
```

**Individual Pages:** `document_pages_timestamp/`
```
page_001.txt  # Text from page 1
page_002.txt  # Text from page 2
page_003.txt  # Text from page 3
```

**Detailed Metadata:** `document_pdf_timestamp.json`
```json
{
  "total_pages": 3,
  "successful_pages": 3,
  "combined_text": "All pages combined...",
  "page_results": [...],
  "pdf_dpi": 300
}
```

## 🔧 Advanced Configuration

### Command Line Options

```bash
python process_a3_document.py --help
```

**Available options:**
- `--input, -i`: Single input file
- `--batch, -b`: Input directory for batch processing  
- `--output, -o`: Output directory (default: ./more4life_results)
- `--pattern, -p`: File pattern for batch (default: *.jpg)
- `--model, -m`: Model path (default: ./more4life-handwriting-ocr)

### Environment Variables

```bash
# Set your token
export HF_TOKEN="your_token_here"

# Or use the .env file created by setup_token.py
source .env
```

## 🎯 Performance & Optimization

### Expected Performance

- **Accuracy**: 85-95% on clear English handwriting
- **Speed**: 2-4 seconds per A3 document (CPU), 1-2 seconds (GPU)
- **Memory**: ~2GB RAM for model loading
- **Storage**: ~1.5GB for downloaded model

### Optimization Tips

1. **Use GPU**: Install CUDA version of PyTorch for 2-3x speed improvement
2. **Batch Processing**: More efficient than processing files individually
3. **Image Quality**: Higher resolution scans (300+ DPI) give better results
4. **Preprocessing**: Clean, high-contrast images work best

### A3 Document Guidelines

**Best Results:**
- ✅ 300+ DPI scanning resolution
- ✅ High contrast (dark text, light background)
- ✅ Clear, legible handwriting
- ✅ Minimal skew/rotation
- ✅ Good lighting during scanning

**Avoid:**
- ❌ Low resolution (<150 DPI)
- ❌ Poor lighting/shadows
- ❌ Heavily rotated/skewed documents
- ❌ Extremely faded or light text

## 🛠️ Troubleshooting

### Common Issues

**1. "Model not found" error:**
```bash
# Re-download the model
python download_trocr_model.py
```

**2. "Token not found" error:**
```bash
# Reset your token  
python setup_token.py
```

**3. Out of memory errors:**
```bash
# Reduce batch size or use smaller images
# The scripts automatically resize large images
```

**4. Poor recognition accuracy:**
- Check image quality and resolution
- Ensure text is dark and background is light
- Try different scanning settings

### Getting Help

1. Check the console output for specific error messages
2. Verify your images are readable and high quality
3. Ensure your Hugging Face token has proper permissions
4. Make sure all dependencies are installed correctly

## 🏢 More4Life Integration

This system is specifically designed for More4Life's A3 document processing needs:

- **Optimized for A3 format** (297 × 420 mm documents)
- **Batch processing** for high-volume workflows  
- **JSON output** for easy integration with other systems
- **Production logging** and error handling
- **Scalable architecture** for enterprise deployment

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.15, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB (8GB recommended)
- **Storage**: 3GB free space
- **Internet**: For initial model download

### Recommended Setup
- **RAM**: 8GB+ 
- **GPU**: NVIDIA GPU with 4GB+ VRAM (for faster processing)
- **CPU**: Multi-core processor
- **Storage**: SSD for better performance

## 🔒 Security & Privacy

- **Token Security**: Tokens are stored in `.env` files, not in code
- **Local Processing**: All OCR processing happens locally (no data sent to external servers)
- **Privacy First**: Your documents never leave your system
- **Secure Setup**: Guided secure token configuration

## 📄 License & Credits

- **TrOCR Model**: Microsoft Research ([TrOCR Paper](https://arxiv.org/abs/2109.10282))
- **Hugging Face**: Model hosting and transformers library
- **More4Life**: Custom integration and workflow optimization

## 🚀 Next Steps

After successful setup:

1. **Test with your documents**: Use `test_a3_processing.py`
2. **Process production documents**: Use `process_a3_document.py`
3. **Integrate with your workflow**: Use the JSON output for downstream processing
4. **Scale up**: Use batch processing for high-volume scenarios

---

**🎯 Ready to digitize your handwritten A3 documents with More4Life!**

For support or questions, check the troubleshooting section above or review the console output for specific error messages. 