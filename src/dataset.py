from __future__ import annotations
from .iterator import InterviewIterator

import json
from collections.abc import Iterator

class InterviewDataset:
    
    _current_id = 0
    
    INTERVIEW_ID = "interview_id"
    PARAGRAPH_ID = "paragraph_id"
    DATA = "data"
    METADATA = "metadata"
    
    def __init__(self):
        self.data_shape = {self.INTERVIEW_ID:"", self.PARAGRAPH_ID:"", self.DATA:"", self.METADATA:{}}
        self._data : list[dict] = []
        self.interviews = []
    
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
    
    @staticmethod
    def _get_next_id() -> int:
        next = InterviewDataset._current_id
        InterviewDataset._current_id += 1
        return next
    
    def _transform_iterator(self, data : Iterator) -> tuple[str, list[dict]]:
        ret = []
        new_id = str(InterviewDataset._get_next_id())
        for i, entry in enumerate(data):
            new_entry = {**self.data_shape}
            new_entry[self.INTERVIEW_ID] = new_id
            new_entry[self.PARAGRAPH_ID] = f"{new_id}_{i}"
            new_entry[self.DATA] = entry
            ret.append(new_entry)
        return new_id, ret
    
    def _transform_dict(self, data : dict, interview_id = None, paragraph_id = None, data_path = None, metadata = None) -> tuple[str, list[dict]]:
        ret = []
        new_id = str(InterviewDataset._get_next_id())
        if len(data.keys()) == 1:
            for id, entry in zip(data.items()):
                new_entry = {**self.data_shape}
                new_entry[self.INTERVIEW_ID] = new_id
                new_entry[self.PARAGRAPH_ID] = f"{new_id}_{id}"
                new_entry[self.DATA] = entry
                ret.append(new_entry)
        elif interview_id and interview_id in data and paragraph_id and paragraph_id in data and data_path and data_path in data:
            for _, entry in zip(data.items()):
                new_entry = {**self.data_shape}
                new_entry[self.INTERVIEW_ID] = data[interview_id]
                new_entry[self.PARAGRAPH_ID] = data[paragraph_id]
                new_entry[self.DATA] = data[data_path]
                if metadata:
                    new_entry[self.METADATA] = data[metadata]
                ret.append(new_entry)
        else:
            raise ValueError(f"Input dict is not of shape dict[variant, str] or the given keys [{interview_id}, {paragraph_id}, {data_path}, {metadata}] do not exist")
        return new_id, ret
    
    def add_interviews(self, *data : list[str] | InterviewIterator | dict):
        for interview in data:
            if isinstance(interview, (list, InterviewIterator)):
                new_id, new_dicts = self._transform_iterator(interview)
                self._data += new_dicts
                self.interviews.append(new_id)
            elif isinstance(interview, dict):
                new_id, new_dicts = self._transform_dict(interview)
                self._data += new_dicts
                self.interviews.append(new_id)
            else:
                raise ValueError("data is not of type list[str], InterviewIterator, or dict")
    
    def filter_data(self, id : str) -> list[dict]:
        return list(filter(lambda dict: dict[self.PARAGRAPH_ID].startswith(id), self._data))
    
    def assign_interview_id(self, prev_id : str, new_id : str) -> None:
        matching_entries = self.filter_data(prev_id)
        for i, entry in enumerate(matching_entries):
            entry[self.INTERVIEW_ID] = new_id
            entry[self.PARAGRAPH_ID] = f"{new_id}_{i}" 
    
    def assign_metadata(self, interview_id : str, key : str, value : str) -> None:
        matching_entries = self.filter_data(interview_id)
        for entry in matching_entries:
            entry[self.METADATA][key] = value
    
    def ids(self) -> list[int]:
        return [d[self.PARAGRAPH_ID] for d in self._data]
    
    def data(self) -> list[str]:
        return [d[self.DATA] for d in self._data]
    
    def as_dict(self) -> dict[int, str]:
        return self._data.copy()
    
    def save(self, file_path : str):
        with open(file_path, 'w') as f:
            for entry in self._data:
                json_str = json.dumps(entry)
                f.write(json_str + "\n")
    
    @staticmethod
    def load(file_path : str) -> InterviewDataset:
        dataset = InterviewDataset()
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                entry = json.loads(line)
                dataset._data.append(entry)
        return dataset