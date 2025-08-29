import datetime
import json
from bson import ObjectId  # from pymongo

def to_mongo_str(value):
    try:
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, datetime.datetime):
            return f'ISODate("{value.isoformat()}")'
        if isinstance(value, ObjectId):
            return f'ObjectId("{str(value)}")'
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, dict):
            return "{ " + ", ".join(f"{json.dumps(k)}: {to_mongo_str(v)}" for k, v in value.items()) + " }"
        if isinstance(value, list):
            return "[ " + ", ".join(to_mongo_str(v) for v in value) + " ]"
        return str(value)
    except Exception as e:
        return f'"{str(value)}" /* error: {e} */'

def getPipelineString(pipeline):
    pipelineString = '['
    try:
        for i, stage in enumerate(pipeline):
            comma = "," if i < len(pipeline) - 1 else ""
            pipelineString += "  " + to_mongo_str(stage) + comma
        pipelineString += "]"
        return pipelineString
    except Exception as e:
        print(f"/* Failed to print pipeline: {e} */")

def copy_pipeline(pipeline):
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        from dzgroshared.models.enums import ENVIRONMENT
        env = ENVIRONMENT(os.getenv("ENV", None))
        if env==ENVIRONMENT.LOCAL:
            import subprocess
            subprocess.run("clip", text=True, input=getPipelineString(pipeline))
        print(f"/* Pipeline Copies to Clipboard */")
    except Exception as e:
        print(f"/* Failed to copy pipeline: {e} */")
