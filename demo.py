#!/usr/bin/env python3
"""
Demo script showing how to use the DeepSeek OCR testing system
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 DeepSeek OCR Testing Demo")
    print("="*50)
    
    # Check if we're in the right directory
    if not Path("OmniDocBench").exists():
        print("❌ OmniDocBench directory not found!")
        print("   Make sure you're running this from the DeepSeek_OCR directory")
        return 1
    
    # Check for images
    image_dir = Path("OmniDocBench/demo_data/omnidocbench_demo/images")
    if not image_dir.exists():
        print("❌ Demo images not found!")
        return 1
    
    image_count = len(list(image_dir.glob("*.jpg")))
    print(f"✅ Found {image_count} demo images ready for testing")
    
    # Show available commands
    print("\n📋 Available Commands:")
    print("="*30)
    
    print("\n1️⃣  **COMPLETE TEST PIPELINE** (Recommended):")
    print("   python run_complete_test.py --api-key YOUR_API_KEY")
    print("   → Runs everything automatically in ~20-40 minutes")
    
    print("\n2️⃣  **OCR PROCESSING ONLY**:")
    print("   python deepseek_ocr_test.py --api-key YOUR_API_KEY --max-images 15")
    print("   → Just converts images to markdown")
    
    print("\n3️⃣  **EVALUATION ONLY** (after OCR):")
    print("   python evaluate_results.py")
    print("   → Compares OCR results with ground truth")
    
    print("\n🔑 **Get Your API Key:**")
    print("   1. Visit: https://api.deepseek.com")
    print("   2. Sign up and get your API key")
    print("   3. Replace YOUR_API_KEY with your actual key")
    
    print("\n💡 **Quick Test (5 images):**")
    print("   python run_complete_test.py --api-key YOUR_KEY --max-images 5")
    
    print("\n📊 **Expected Results:**")
    print("   • Processing Time: 15-30 minutes")
    print("   • Success Rate: 80-95%")
    print("   • Word Overlap: 50-70%")
    print("   • Cost: ~$0.10-0.50")
    
    print("\n📁 **Output Files:**")
    print("   • deepseek_ocr_results/*.md - Individual OCR outputs")
    print("   • deepseek_ocr_results/batch_results.json - Processing summary")
    print("   • evaluation_results.json - Evaluation metrics")
    
    print("\n🎯 **Next Steps:**")
    print("   1. Get your DeepSeek API key")
    print("   2. Run: python run_complete_test.py --api-key YOUR_KEY")
    print("   3. Check results in generated files")
    print("   4. Scale to larger datasets if satisfied")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
