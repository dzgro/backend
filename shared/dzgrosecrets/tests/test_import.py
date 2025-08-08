# test_import.py
try:
    import models
    print(f"Models package found at: {models.__file__}")
    from models.model import DzgroSecrets
    print("DzgroSecrets class successfully imported")
    from secrets.helper import SecretManager
    secrets = SecretManager()
    print(secrets.secrets)
except ImportError as e:
    print(f"Import error: {e}")