#!/usr/bin/env python3
"""
Quick evaluation script for DeepSeek OCR results against OmniDocBench ground truth
"""

import json
import os
from pathlib import Path
import argparse
from typing import Dict, List, Any
import re

class QuickEvaluator:
    def __init__(self, ground_truth_file: str, results_dir: str):
        self.ground_truth_file = ground_truth_file
        self.results_dir = Path(results_dir)
        self.ground_truth_data = self.load_ground_truth()
        
    def load_ground_truth(self) -> Dict[str, Any]:
        """Load OmniDocBench ground truth data"""
        with open(self.ground_truth_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_text_from_annotations(self, annotations: List[Dict]) -> str:
        """Extract text content from OmniDocBench annotations"""
        text_parts = []
        
        # Sort by order if available
        sorted_annotations = sorted(annotations, key=lambda x: x.get('order', 0))
        
        for annotation in sorted_annotations:
            if 'text' in annotation and annotation['text'].strip():
                text_parts.append(annotation['text'].strip())
        
        return '\n'.join(text_parts)
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove markdown formatting for basic comparison
        text = re.sub(r'[#*_`]', '', text)
        return text.strip().lower()
    
    def calculate_word_overlap(self, pred_text: str, gt_text: str) -> float:
        """Calculate word-level overlap between prediction and ground truth"""
        pred_words = set(self.normalize_text(pred_text).split())
        gt_words = set(self.normalize_text(gt_text).split())
        
        if not gt_words:
            return 0.0
        
        overlap = len(pred_words.intersection(gt_words))
        return overlap / len(gt_words)
    
    def evaluate_single_result(self, image_name: str, predicted_md: str) -> Dict[str, Any]:
        """Evaluate single OCR result against ground truth"""
        # Find corresponding ground truth
        gt_entry = None
        for entry in self.ground_truth_data:
            if 'image_path' in entry and image_name in entry['image_path']:
                gt_entry = entry
                break
        
        if not gt_entry:
            return {
                "image_name": image_name,
                "found_gt": False,
                "error": "No ground truth found"
            }
        
        # Extract ground truth text
        gt_text = self.extract_text_from_annotations(gt_entry.get('layout_dets', []))
        
        # Calculate metrics
        word_overlap = self.calculate_word_overlap(predicted_md, gt_text)
        
        # Basic structure detection (headers, lists, etc.)
        has_headers = bool(re.search(r'^#+\s', predicted_md, re.MULTILINE))
        has_lists = bool(re.search(r'^\s*[-*+]\s', predicted_md, re.MULTILINE))
        has_tables = bool(re.search(r'\|.*\|', predicted_md))
        
        return {
            "image_name": image_name,
            "found_gt": True,
            "word_overlap": word_overlap,
            "gt_text_length": len(gt_text),
            "pred_text_length": len(predicted_md),
            "structure_detected": {
                "headers": has_headers,
                "lists": has_lists,
                "tables": has_tables
            },
            "gt_preview": gt_text[:200] + "..." if len(gt_text) > 200 else gt_text,
            "pred_preview": predicted_md[:200] + "..." if len(predicted_md) > 200 else predicted_md
        }
    
    def evaluate_batch(self) -> Dict[str, Any]:
        """Evaluate all results in the results directory"""
        md_files = list(self.results_dir.glob("*.md"))
        
        if not md_files:
            return {"error": "No markdown files found in results directory"}
        
        print(f"Evaluating {len(md_files)} OCR results...")
        
        evaluations = []
        total_word_overlap = 0
        valid_evaluations = 0
        structure_stats = {"headers": 0, "lists": 0, "tables": 0}
        
        for md_file in md_files:
            # Read predicted markdown
            with open(md_file, 'r', encoding='utf-8') as f:
                predicted_md = f.read()
            
            # Evaluate
            result = self.evaluate_single_result(md_file.stem, predicted_md)
            evaluations.append(result)
            
            if result.get("found_gt"):
                valid_evaluations += 1
                total_word_overlap += result["word_overlap"]
                
                # Count structure elements
                for struct_type, detected in result["structure_detected"].items():
                    if detected:
                        structure_stats[struct_type] += 1
        
        # Calculate summary metrics
        avg_word_overlap = total_word_overlap / valid_evaluations if valid_evaluations > 0 else 0
        
        summary = {
            "total_files": len(md_files),
            "valid_evaluations": valid_evaluations,
            "average_word_overlap": avg_word_overlap,
            "structure_detection_rate": {
                k: v / valid_evaluations * 100 if valid_evaluations > 0 else 0 
                for k, v in structure_stats.items()
            },
            "evaluations": evaluations
        }
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="Evaluate DeepSeek OCR results")
    parser.add_argument("--ground-truth", 
                       default="OmniDocBench/demo_data/omnidocbench_demo/OmniDocBench_demo.json",
                       help="Path to ground truth JSON file")
    parser.add_argument("--results-dir", default="deepseek_ocr_results",
                       help="Directory containing OCR results")
    parser.add_argument("--output", default="evaluation_results.json",
                       help="Output file for evaluation results")
    
    args = parser.parse_args()
    
    # Run evaluation
    evaluator = QuickEvaluator(args.ground_truth, args.results_dir)
    results = evaluator.evaluate_batch()
    
    # Save detailed results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 EVALUATION SUMMARY")
    print("="*50)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    print(f"Total Files Evaluated: {results['total_files']}")
    print(f"Valid Evaluations: {results['valid_evaluations']}")
    print(f"Average Word Overlap: {results['average_word_overlap']:.2%}")
    
    print("\n📋 Structure Detection Rates:")
    for struct_type, rate in results['structure_detection_rate'].items():
        print(f"  {struct_type.title()}: {rate:.1f}%")
    
    # Quality assessment
    overlap_score = results['average_word_overlap']
    if overlap_score > 0.7:
        print("\n✅ Excellent OCR quality!")
    elif overlap_score > 0.5:
        print("\n✅ Good OCR quality")
    elif overlap_score > 0.3:
        print("\n⚠️  Moderate OCR quality")
    else:
        print("\n❌ Poor OCR quality - check results")
    
    print(f"\n📄 Detailed results saved to: {args.output}")

if __name__ == "__main__":
    main()
