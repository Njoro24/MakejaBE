from app import create_app


app = create_app()

# Entry point for WSGI servers like Gunicorn or uWSGI
if __name__ == "__main__":
    app.run()