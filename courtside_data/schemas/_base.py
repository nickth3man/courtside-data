from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BRRow(BaseModel):
    """Base model for every Basketball-Reference row schema.

    - ``populate_by_name=True`` lets callers pass values by alias or by the
      stable Python attribute name.
    - ``extra="ignore"`` keeps the model resilient to new data-stat columns BR
      adds without warning.
    - ``str_strip_whitespace=True`` removes incidental padding.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore", str_strip_whitespace=True)

    def __getitem__(self, key: str) -> object:
        return getattr(self, key)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            dumped = self.model_dump(mode="python")
            return all(dumped.get(key) == value for key, value in other.items())
        return super().__eq__(other)
