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
        self._data : list[dict] = []
        self.interviews = []
    
    def __str__(self):
        return "[{0}, len: {1}]".format(self, len(self))
    
    def __len__(self):
        return len(self._data)
    
    def __add__(self, other) -> InterviewDataset:
        if not isinstance(other, InterviewDataset):
            raise TypeError(f"Cannot add type {type(other)} with InterviewDataset")
        total_data = self._data + other._data
        return InterviewDataset.from_dict(total_data)
    
    def get_entry(self, key) -> dict:
        for d in self._data:
            if d[self.PARAGRAPH_ID] == key:
                return d
        return self.shape()
    
    def __getitem__(self, key : int):
        entry = self.get_entry(key)
        return entry[self.DATA]

    def __setitem__(self, key : int, value):
        entry = self.get_entry(key)
        entry[self.DATA] = value
    
    def __delitem__(self, key : int):
        entry = self.get_entry(key)
        self._data.remove(entry)
    
    @staticmethod
    def shape() -> dict:
        return {InterviewDataset.INTERVIEW_ID:"", InterviewDataset.PARAGRAPH_ID:"", InterviewDataset.DATA:"", InterviewDataset.METADATA:{}}
    
    @staticmethod
    def _get_next_id() -> int:
        next = InterviewDataset._current_id
        InterviewDataset._current_id += 1
        return next
    
    def _transform_iterator(self, data : Iterator) -> tuple[str, list[dict]]:
        ret = []
        new_id = str(InterviewDataset._get_next_id())
        for i, entry in enumerate(data):
            new_entry = {**self.shape()}
            new_entry[self.INTERVIEW_ID] = new_id
            new_entry[self.PARAGRAPH_ID] = f"{new_id}_{i}"
            new_entry[self.DATA] = entry
            ret.append(new_entry)
        return new_id, ret
    
    def add_interviews(self, *data : list[str] | InterviewIterator, interview_id=None):
        for interview in data:
            if isinstance(interview, (list, InterviewIterator)):
                new_id, new_dicts = self._transform_iterator(interview)
                self._data += new_dicts
                self.interviews.append(interview_id if interview_id is not None else new_id)
            else:
                raise ValueError("data is not of type list[str], InterviewIterator, or dict")
    
    def filter_data(self, id : str) -> InterviewDataset:
        if id not in self.interviews:
            print(f"{id} not in {self.interviews}")
            return InterviewDataset()
        return self.from_dict([d for d in self._data if d[self.INTERVIEW_ID] == id])
    
    def assign_interview_id(self, prev_id : str, new_id : str) -> None:
        for i, entry in enumerate(self._data):
            if entry[self.INTERVIEW_ID] == prev_id:
                entry[self.INTERVIEW_ID] = new_id
                entry[self.PARAGRAPH_ID] = f"{new_id}_{i}"
        self.interviews.remove(prev_id)
        self.interviews.append(new_id)
    
    def assign_metadata(self, interview_id : str, key : str, value : str) -> None:
        for entry in self._data:
            if entry[self.INTERVIEW_ID] == interview_id:
                entry[self.METADATA][key] = value
    
    def ids(self) -> list[int]:
        return [d[self.PARAGRAPH_ID] for d in self._data]
    
    def data(self) -> list:
        return [d[self.DATA] for d in self._data]
    
    def metadata(self, interview_id) -> dict:
        for entry in self._data:
            if entry[self.INTERVIEW_ID] == interview_id:
                return entry[self.METADATA]
        return {}
    
    def as_dict(self) -> list[dict]:
        return self._data.copy()
    
    @staticmethod
    def from_dict(data : list[dict]) -> InterviewDataset:
        if len(data) == 0:
            return InterviewDataset()
        if not all(key in data[0] for key in [InterviewDataset.INTERVIEW_ID, InterviewDataset.PARAGRAPH_ID, InterviewDataset.DATA, InterviewDataset.METADATA]):
            return InterviewDataset()
        
        ds = InterviewDataset()
        ds._data = data
        ds.interviews = list({d[InterviewDataset.INTERVIEW_ID] for d in data})
        return ds
    
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