from .iterator import InterviewIterator

import json

class InterviewDataset:
    
    def __init__(self, data : list[str] | InterviewIterator | dict[int, str] = []):
        if isinstance(data, list):
            self._data : dict[int, str] = {i : p for i, p in enumerate(data)}
        elif isinstance(data, InterviewIterator):
            self._data : dict[int, str] = {i : p for i, p in enumerate(data.get_paragraphs())}
        elif isinstance(data, dict):
            self._data : dict[int, str] = data.copy()
        else:
            raise ValueError("Input data type {0} is not of valid type".format(type(data)))
    
    def __str__(self):
        return "[{0}, len: {1}]".format(self, len(self))
    
    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, key : int):
        if key in self._data:
            return self._data[key]
        else:
            raise IndexError("Dataset {0} has no entry {1}".format(self, key))

    def __setitem__(self, key : int, value : str):
        self._data[key] = value
    
    def __delitem__(self, key : int):
        if key in self._data:
            del self._data[key]
        else:
            raise IndexError("Dataset {0} has no entry {1}".format(self, key))
    
    def ids(self) -> list[int]:
        return list(self._data.keys())
    
    def data(self) -> list[str]:
        return list(self._data.values())
    
    def as_dict(self) -> dict[int, str]:
        return self._data.copy()
    
    def save(self, file_path : str):
        with open(file_path, 'w') as f:
            for entry in [{"id":i, "data":d} for i, d in self._data.items()]:
                json_string = json.dumps(entry)
                f.write(json_string + "\n")
    
    def load(self, file_path : str):
        self._data = {}
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                entry = json.loads(line)
                self._data[entry["id"]] = entry["data"]
                