from .document import InterviewDocument

class InterviewIterator:
    def __init__(self, *files : str):
        self.paragraphs : list[str] = []
        for file in files:
            if not isinstance(file, str):
                continue
            doc = InterviewDocument(file)
            self.paragraphs += doc.paragraphs
        self.current_index : int = 0

    def get_paragraphs(self) -> list[str]:
        return [p for p in self.paragraphs]
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index < len(self.paragraphs):
            paragraph = self.paragraphs[self.current_index]
            self.current_index += 1
            return paragraph
        else:
            raise StopIteration()