import json


class JSONObject:
    def toJSON(self):
        return json.dumps(
            self,
            sort_keys=False,
            indent=2,
            default=lambda o: {k: v for k, v in o.__dict__.items() if not k.startswith("_")},
        )

    @classmethod
    def fromJSON(cls, data: str):
        return cls(**json.loads(data))
