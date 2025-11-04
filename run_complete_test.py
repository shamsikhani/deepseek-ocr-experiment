#!/usr/bin/env python3
"""
Complete DeepSeek OCR Test Runner
Orchestrates the entire testing pipeline within 1 hour
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception running command: {cmd}")
        print(f"Error: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        import PIL
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing required packages...")
        return run_command("pip install requests pillow")

def main():
    parser = argparse.ArgumentParser(description="Complete DeepSeek OCR Test Pipeline")
    parser.add_argument("--api-key", required=True, help="DeepSeek API key")
    parser.add_argument("--max-images", type=int, default=15, 
                       help="Maximum images to process (default: 15 for speed)")
    
    args = parser.parse_args()
    
    print("🚀 DeepSeek OCR Complete Test Pipeline")
    print("="*50)
    
    start_time = time.time()
    
    # Step 1: Check dependencies
    print("1️⃣  Checking dependencies...")
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        return 1
    print("✅ Dependencies ready")
    
    # Step 2: Verify data availability
    print("\n2️⃣  Verifying test data...")
    image_dir = Path("OmniDocBench/demo_data/omnidocbench_demo/images")
    gt_file = Path("OmniDocBench/demo_data/omnidocbench_demo/OmniDocBench_demo.json")
    
    if not image_dir.exists():
        print(f"❌ Image directory not found: {image_dir}")
        return 1
    
    if not gt_file.exists():
        print(f"❌ Ground truth file not found: {gt_file}")
        return 1
    
    image_count = len(list(image_dir.glob("*.jpg")))
    print(f"✅ Found {image_count} test images")
    
    # Step 3: Run OCR processing
    print("\n3️⃣  Running DeepSeek OCR processing...")
    ocr_cmd = f'python deepseek_ocr_test.py --api-key "{args.api_key}" --max-images {args.max_images}'
    
    ocr_start = time.time()
    if not run_command(ocr_cmd):
        print("❌ OCR processing failed")
        return 1
    ocr_time = time.time() - ocr_start
    print(f"✅ OCR processing completed in {ocr_time:.1f} seconds")
    
    # Step 4: Run evaluation
    print("\n4️⃣  Running evaluation...")
    eval_cmd = "python evaluate_results.py"
    
    eval_start = time.time()
    if not run_command(eval_cmd):
        print("❌ Evaluation failed")
        return 1
    eval_time = time.time() - eval_start
    print(f"✅ Evaluation completed in {eval_time:.1f} seconds")
    
    # Step 5: Generate final report
    print("\n5️⃣  Generating final report...")
    
    total_time = time.time() - start_time
    
    # Read results
    results_file = Path("deepseek_ocr_results/batch_results.json")
    eval_file = Path("evaluation_results.json")
    
    if results_file.exists() and eval_file.exists():
        import json
        
        with open(results_file) as f:
            ocr_results = json.load(f)
        
        with open(eval_file) as f:
            eval_results = json.load(f)
        
        print("\n" + "="*60)
        print("📊 FINAL TEST REPORT")
        print("="*60)
        print(f"⏱️  Total Runtime: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"🖼️  Images Processed: {ocr_results['total_images']}")
        print(f"✅ OCR Success Rate: {ocr_results['success_rate']:.1f}%")
        print(f"🔤 Average Word Overlap: {eval_results.get('average_word_overlap', 0):.1%}")
        print(f"💰 Total Tokens Used: {ocr_results['total_tokens_used']}")
        
        print("\n📋 Structure Detection:")
        for struct_type, rate in eval_results.get('structure_detection_rate', {}).items():
            print(f"   {struct_type.title()}: {rate:.1f}%")
        
        # Performance assessment
        print("\n🎯 Performance Assessment:")
        word_overlap = eval_results.get('average_word_overlap', 0)
        success_rate = ocr_results['success_rate']
        
        if word_overlap > 0.6 and success_rate > 80:
            print("   🏆 EXCELLENT - Ready for production testing")
        elif word_overlap > 0.4 and success_rate > 60:
            print("   ✅ GOOD - Suitable for most use cases")
        elif word_overlap > 0.2 and success_rate > 40:
            print("   ⚠️  MODERATE - Needs improvement")
        else:
            print("   ❌ POOR - Significant issues detected")
        
        print(f"\n📁 Detailed results available in:")
        print(f"   - OCR outputs: deepseek_ocr_results/")
        print(f"   - Evaluation: evaluation_results.json")
        
        # Time efficiency check
        if total_time < 3600:  # 1 hour
            print(f"\n⏰ Completed within 1-hour target! ({60-total_time/60:.1f} minutes to spare)")
        else:
            print(f"\n⏰ Exceeded 1-hour target by {total_time/60-60:.1f} minutes")
    
    else:
        print("❌ Could not find result files for final report")
        return 1
    
    print("\n🎉 Test pipeline completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
