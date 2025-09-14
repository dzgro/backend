def open(objectKey: str|None):
    if objectKey: return { "$set": {objectKey: execute(f"${objectKey}")} }
    return { "$replaceRoot": { "newRoot": execute("$$ROOT")} }

def execute(key: str):
    return {
          "$arrayToObject": {
            "$reduce": {
              "input": {"$objectToArray": key},
              "initialValue": [],
              "in": {
                    "$concatArrays": [
                      "$$value",
                      {
                        "$cond": [
                          {"$eq": [{"$type": "$$this.v"},"object"]},
                          {"$objectToArray": "$$this.v"},
                          ["$$this"]
                        ]
                      }
                      
                    ]
                  }
            }
          }
        }