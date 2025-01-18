from app import create_app

app = create_app()

if __name__ == "__main__":
    context = ("cert.pem", "key.pem")
    app.run(ssl_context=context)
