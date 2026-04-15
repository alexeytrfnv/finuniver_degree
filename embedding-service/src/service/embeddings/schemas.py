from dataclasses import dataclass
from typing import List, Dict


@dataclass
class SparceEmbedding:
    indices: List[int]
    values: List[float]

    def as_object(self) -> Dict[str, List[float]]:
        return {
            "values": self.values,
            "indices": self.indices,
        }

    def as_dict(self) -> Dict[int, float]:
        return {idx: val for idx, val in zip(self.indices, self.values)}
