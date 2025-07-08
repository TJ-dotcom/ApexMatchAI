print("Testing if basic Python works in this environment")

# Now try to import our modules - this will either succeed or print an error
try:
    from backend.app.matcher import extract_job_requirements
    print("Successfully imported matcher module")
except Exception as e:
    print(f"Error importing matcher module: {e}")

# If this works, try a basic test
try:
    print("Testing basic functionality...")
    from backend.app.matcher import extract_job_requirements
    result = extract_job_requirements("This is a test job requiring 5 years experience.", "Senior Engineer")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error in test: {e}")
