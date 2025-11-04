#!/usr/bin/env python3
"""
DeepSeek OCR Testing Script for OmniDocBench Subset
Fast evaluation using DeepSeek API with minimal setup
"""

import os
import json
import base64
import requests
from pathlib import Path
import time
from typing import Dict, List, Any
import argparse

class DeepSeekOCRTester:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API call"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def process_image(self, image_path: str, prompt: str = "<|grounding|>Convert the document to markdown.") -> Dict[str, Any]:
        """Process single image through DeepSeek OCR API"""
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare API request
            payload = {
                "model": "deepseek-chat",  # Using chat model with vision capabilities
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1
            }
            
            # Make API call
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                markdown_content = result['choices'][0]['message']['content']
                return {
                    "success": True,
                    "markdown": markdown_content,
                    "usage": result.get('usage', {}),
                    "image_path": image_path
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error {response.status_code}: {response.text}",
                    "image_path": image_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception: {str(e)}",
                "image_path": image_path
            }
    
    def process_batch(self, image_dir: str, output_dir: str, max_images: int = 18) -> Dict[str, Any]:
        """Process batch of images and save results"""
        image_dir = Path(image_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Get image files
        image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
        image_files = image_files[:max_images]  # Limit for quick test
        
        print(f"Processing {len(image_files)} images...")
        
        results = []
        total_tokens = 0
        successful_conversions = 0
        
        for i, image_path in enumerate(image_files, 1):
            print(f"Processing {i}/{len(image_files)}: {image_path.name}")
            
            # Process image
            result = self.process_image(str(image_path))
            results.append(result)
            
            if result["success"]:
                successful_conversions += 1
                
                # Save markdown output
                output_file = output_dir / f"{image_path.stem}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result["markdown"])
                
                # Track token usage
                if "usage" in result:
                    total_tokens += result["usage"].get("total_tokens", 0)
                
                print(f"✓ Success: {output_file}")
            else:
                print(f"✗ Failed: {result['error']}")
            
            # Small delay to be respectful to API
            time.sleep(0.5)
        
        # Save batch results
        batch_summary = {
            "total_images": len(image_files),
            "successful_conversions": successful_conversions,
            "success_rate": successful_conversions / len(image_files) * 100,
            "total_tokens_used": total_tokens,
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        summary_file = output_dir / "batch_results.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(batch_summary, f, indent=2, ensure_ascii=False)
        
        return batch_summary

def main():
    parser = argparse.ArgumentParser(description="DeepSeek OCR Testing on OmniDocBench subset")
    parser.add_argument("--api-key", required=True, help="DeepSeek API key")
    parser.add_argument("--image-dir", default="OmniDocBench/demo_data/omnidocbench_demo/images", 
                       help="Directory containing test images")
    parser.add_argument("--output-dir", default="deepseek_ocr_results", 
                       help="Output directory for results")
    parser.add_argument("--max-images", type=int, default=18, 
                       help="Maximum number of images to process")
    
    args = parser.parse_args()
    
    # Validate API key
    if not args.api_key or args.api_key == "your_api_key_here":
        print("❌ Please provide a valid DeepSeek API key using --api-key")
        print("   Get your API key from: https://api.deepseek.com")
        return
    
    # Initialize tester
    tester = DeepSeekOCRTester(args.api_key)
    
    # Run batch processing
    print("🚀 Starting DeepSeek OCR batch processing...")
    start_time = time.time()
    
    results = tester.process_batch(args.image_dir, args.output_dir, args.max_images)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Print summary
    print("\n" + "="*50)
    print("📊 BATCH PROCESSING SUMMARY")
    print("="*50)
    print(f"Total Images: {results['total_images']}")
    print(f"Successful Conversions: {results['successful_conversions']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Total Tokens Used: {results['total_tokens_used']}")
    print(f"Processing Time: {processing_time:.1f} seconds")
    print(f"Average Time per Image: {processing_time/results['total_images']:.1f} seconds")
    print(f"Results saved to: {args.output_dir}/")
    
    if results['success_rate'] > 80:
        print("✅ Great success rate! Ready for evaluation.")
    elif results['success_rate'] > 50:
        print("⚠️  Moderate success rate. Check failed conversions.")
    else:
        print("❌ Low success rate. Check API key and network connection.")

if __name__ == "__main__":
    main()
