import uvicorn


def main():
    uvicorn.run("app.main:app", host="127.0.0.1", port=3000, reload=True,
                reload_includes=["*.py", "*.json"])


if __name__ == "__main__":
    main()
