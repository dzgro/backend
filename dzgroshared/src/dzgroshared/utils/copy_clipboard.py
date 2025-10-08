def copy(data):
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        from dzgroshared.db.enums import ENVIRONMENT
        env = ENVIRONMENT(os.getenv("ENV", None))
        if env==ENVIRONMENT.LOCAL:
            import subprocess
            subprocess.run("clip", text=True, input=data)
        print(f"/* Pipeline Copied to Clipboard */")
    except Exception as e:
        pass