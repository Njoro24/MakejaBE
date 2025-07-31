from app import create_app


app = create_app()

# Entry point for WSGI servers like Gunicorn or uWSGI
if __name__ == "__main__":
    app.run()

print("=== WSGI.PY STARTING ===")
try:
    from app import create_app
    print("=== IMPORT SUCCESSFUL ===")
except Exception as e:
    print(f"=== IMPORT FAILED: {e} ===")

try:
    app = create_app()
    print("=== CREATE_APP CALLED ===")
except Exception as e:
    print(f"=== CREATE_APP FAILED: {e} ===")

if __name__ == "__main__":
    app.run()