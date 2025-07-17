#!/usr/bin/env python3
"""Check flake8 compliance for the modified test_llm.py file."""

import sys

def check_line_lengths():
    """Check that all lines are 79 characters or less."""
    with open('/Users/soheiyagi/sou-co/langchain-iointelligence/tests/test_llm.py', 'r') as f:
        lines = f.readlines()
    
    long_lines = []
    blank_lines_with_whitespace = []
    
    for i, line in enumerate(lines, 1):
        # Remove newline for length check
        line_content = line.rstrip('\n')
        
        # Check line length
        if len(line_content) > 79:
            long_lines.append((i, len(line_content), line_content))
        
        # Check for whitespace in blank lines
        if line_content.strip() == '' and len(line_content) > 0:
            blank_lines_with_whitespace.append((i, line_content))
    
    print(f"📊 Checked {len(lines)} lines")
    
    if long_lines:
        print(f"\n❌ Found {len(long_lines)} lines exceeding 79 characters:")
        for line_num, length, content in long_lines:
            print(f"  Line {line_num}: {length} chars - {content[:60]}...")
    else:
        print("\n✅ All lines are 79 characters or less")
    
    if blank_lines_with_whitespace:
        print(f"\n❌ Found {len(blank_lines_with_whitespace)} blank lines with whitespace:")
        for line_num, content in blank_lines_with_whitespace:
            print(f"  Line {line_num}: '{content}' (length: {len(content)})")
    else:
        print("\n✅ No blank lines contain whitespace")
    
    return len(long_lines) == 0 and len(blank_lines_with_whitespace) == 0

if __name__ == "__main__":
    success = check_line_lengths()
    if success:
        print("\n🎉 File passes flake8 line length and whitespace checks!")
        sys.exit(0)
    else:
        print("\n❌ File has flake8 issues that need to be fixed")
        sys.exit(1)
