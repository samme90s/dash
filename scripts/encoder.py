import json

from scripts.tile import Tile


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Tile):
            return obj.to_dict()

        # Add more types here if needed:
        # if isinstance(obj, ...):
        #     return obj.to_dict()

        # For everything else.
        return super().default(obj)
