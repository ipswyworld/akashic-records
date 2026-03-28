import sys
import os

# Add backend directory to path to import privacy_utils
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from privacy_utils import redactor

def test_direct_redaction():
    print("--- Testing Redactor Class Directly ---")
    
    # Test Email Redaction
    email_text = "Contact me at john.doe@example.com or support@google.co.uk"
    scrubbed_email = redactor.scrub(email_text)
    print(f"Original: {email_text}")
    print(f"Scrubbed: {scrubbed_email}")
    
    if "[EMAIL_REDACTED]" in scrubbed_email:
        print("✅ Email Redaction PASS")
    else:
        print("❌ Email Redaction FAIL")

    # Test Phone Redaction
    phone_text = "Call me at +1 555-0123 or 07700 900123"
    scrubbed_phone = redactor.scrub(phone_text)
    print(f"Original: {phone_text}")
    print(f"Scrubbed: {scrubbed_phone}")
    
    if "[PHONE_REDACTED]" in scrubbed_phone:
        print("✅ Phone Redaction PASS")
    else:
        print("❌ Phone Redaction FAIL")

    # Test Name Redaction (Aggressive Mode)
    name_text = "My name is John Smith and my partner is Jane Doe."
    scrubbed_name = redactor.scrub(name_text, mode="aggressive")
    print(f"Original: {name_text}")
    print(f"Scrubbed: {scrubbed_name}")
    
    if "[NAME_REDACTED]" in scrubbed_name:
        print("✅ Name Redaction PASS")
    else:
        print("❌ Name Redaction FAIL")

if __name__ == "__main__":
    test_direct_redaction()
