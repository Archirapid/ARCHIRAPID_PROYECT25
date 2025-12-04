import sys
import traceback

try:
    import app
    print("App imported successfully")
except Exception as e:
    print(f"Error importing app: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    # Try to run the main dispatcher
    if __name__ == "__main__":
        print("Running main dispatcher")
        # Simulate the main logic
        import streamlit as st
        st.set_page_config(layout='wide')
        print("Streamlit config set")
        # Add more simulation if needed
except Exception as e:
    print(f"Error in main: {e}")
    traceback.print_exc()
    sys.exit(1)