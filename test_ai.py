#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Test Script - ReisBot Premium
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Test environment
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.env")
load_dotenv(config_path)

OPENAI_API_KEY = os.getenv("OPENAI_KEY")

def test_openai_connection():
    """Test OpenAI API connection"""
    print("🔍 Testing OpenAI connection...")
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ OpenAI API key not found or invalid")
        return False
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test with a simple prompt
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Merhaba, bu bir test mesajıdır."}],
            max_tokens=50
        )
        
        print("✅ OpenAI connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI error: {str(e)}")
        return False

def test_api_key_validity():
    """Test if API key is valid"""
    print("\n🔍 Testing API key validity...")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test with minimal request
        response = client.models.list()
        print("✅ API key is valid!")
        return True
        
    except Exception as e:
        print(f"❌ API key error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🤖 ReisBot Premium AI Test")
    print("=" * 50)
    
    # Test API key
    api_valid = test_api_key_validity()
    
    # Test connection
    conn_valid = test_openai_connection()
    
    print("\n" + "=" * 50)
    if api_valid and conn_valid:
        print("🎉 All tests passed! AI should work in Telegram bot.")
    else:
        print("⚠️  Issues found. Check the errors above.")
