"""
Sample Test Script
Demonstrates how to use the forensic analysis system programmatically
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.scorer import analyze_file_authenticity
from utils.hashing import calculate_file_hash
from utils.metadata import analyze_metadata
from utils.ela import analyze_image_ela
from utils.noise import analyze_noise
from loguru import logger


def test_comprehensive_analysis(file_path: str):
    """Run comprehensive analysis on a file"""
    
    logger.info("="*60)
    logger.info("COMPREHENSIVE FORENSIC ANALYSIS TEST")
    logger.info("="*60)
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return
    
    logger.info(f"\nAnalyzing file: {file_path.name}")
    logger.info("-"*60)
    
    # Run comprehensive analysis
    results = analyze_file_authenticity(file_path)
    
    # Display results
    print("\n" + "="*60)
    print("FORENSIC ANALYSIS REPORT")
    print("="*60)
    print(f"\nFile: {results['file_name']}")
    print(f"Path: {results['file_path']}")
    
    print("\n📊 COMPONENT SCORES:")
    print("-"*60)
    for component, score in results['component_scores'].items():
        print(f"  {component.capitalize():12s}: {score:6.2f}/100")
    
    print("\n🎯 OVERALL ASSESSMENT:")
    print("-"*60)
    print(f"  Overall Score: {results['overall_score']:.2f}/100")
    print(f"  Verdict:       {results['verdict']}")
    print(f"  Confidence:    {results['confidence']}")
    
    print("\n💡 RECOMMENDATIONS:")
    print("-"*60)
    for idx, rec in enumerate(results['recommendations'], 1):
        print(f"  {idx}. {rec}")
    
    print("\n" + "="*60)


def test_individual_analyses(file_path: str):
    """Test individual forensic analysis modules"""
    
    logger.info("\n" + "="*60)
    logger.info("INDIVIDUAL MODULE TESTS")
    logger.info("="*60)
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return
    
    # Test 1: Hash Calculation
    print("\n1️⃣  HASH CALCULATION")
    print("-"*60)
    try:
        file_hash = calculate_file_hash(file_path)
        print(f"SHA-256: {file_hash}")
        print("Status:  ✅ Success")
    except Exception as e:
        print(f"Status:  ❌ Failed - {str(e)}")
    
    # Test 2: Metadata Analysis (for images)
    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        print("\n2️⃣  METADATA ANALYSIS")
        print("-"*60)
        try:
            metadata_result = analyze_metadata(file_path)
            print(f"Score:   {metadata_result['metadata_score']:.2f}")
            print(f"Verdict: {metadata_result['overall_verdict']}")
            print("Status:  ✅ Success")
        except Exception as e:
            print(f"Status:  ❌ Failed - {str(e)}")
        
        # Test 3: ELA Analysis
        print("\n3️⃣  ERROR LEVEL ANALYSIS (ELA)")
        print("-"*60)
        try:
            ela_result = analyze_image_ela(file_path)
            print(f"Score:           {ela_result['ela_score']:.2f}")
            print(f"Verdict:         {ela_result['verdict']}")
            print(f"Tampered Regions: {ela_result['tampered_regions_count']}")
            print("Status:          ✅ Success")
        except Exception as e:
            print(f"Status:  ❌ Failed - {str(e)}")
        
        # Test 4: Noise Analysis
        print("\n4️⃣  NOISE PATTERN ANALYSIS")
        print("-"*60)
        try:
            noise_result = analyze_noise(file_path)
            print(f"Score:             {noise_result['noise_score']:.2f}")
            print(f"Verdict:           {noise_result['verdict']}")
            print(f"Anomalous Regions: {noise_result['anomalous_regions']}")
            print("Status:            ✅ Success")
        except Exception as e:
            print(f"Status:  ❌ Failed - {str(e)}")
    
    print("\n" + "="*60)


def main():
    """Main test function"""
    
    # Example usage
    print("\n🔍 AI-Powered Digital Forensics System - Test Script")
    print("="*60)
    
    # You can provide your own test file
    test_file = input("\nEnter path to test file (or press Enter for demo): ").strip()
    
    if not test_file:
        print("\n⚠️  No file provided. Please provide a test image to analyze.")
        print("\nExample usage:")
        print("  python scripts/test_analysis.py")
        print("  Then enter: path/to/your/image.jpg")
        return
    
    test_file = Path(test_file)
    
    if not test_file.exists():
        print(f"\n❌ Error: File not found: {test_file}")
        return
    
    # Run tests
    choice = input("\nSelect test type:\n[1] Comprehensive analysis\n[2] Individual module tests\n[3] Both\n\nChoice: ").strip()
    
    if choice == "1":
        test_comprehensive_analysis(test_file)
    elif choice == "2":
        test_individual_analyses(test_file)
    elif choice == "3":
        test_comprehensive_analysis(test_file)
        test_individual_analyses(test_file)
    else:
        print("Invalid choice. Exiting...")
    
    print("\n✅ Test complete!\n")


if __name__ == "__main__":
    main()
