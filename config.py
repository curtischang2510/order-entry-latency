"""Shared YAML configuration for benchmark variants in this repository."""

from dataclasses import dataclass, field
from math import isfinite
from pathlib import Path

import yaml


def _required_text(mapping: dict, key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"config field {key!r} must be a nonempty string")
    return value.strip()


def _positive_number(value, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"config field {name!r} must be a positive number") from exc
    if not isfinite(number) or number <= 0:
        raise ValueError(f"config field {name!r} must be a positive number")
    return number


@dataclass(frozen=True)
class Config:
    account_address: str
    private_key: str = field(repr=False)
    coin: str
    price: float
    size: float

    @classmethod
    def from_yaml(cls, path: str | Path = "config.yaml") -> "Config":
        path = Path(path)
        try:
            with path.open(encoding="utf-8") as config_file:
                data = yaml.safe_load(config_file)
        except yaml.YAMLError:
            # A parser traceback may quote the line containing the private key.
            raise ValueError(f"invalid YAML in {path}") from None

        if not isinstance(data, dict):
            raise TypeError("config.yaml must contain a mapping")
        order = data.get("order")
        if not isinstance(order, dict):
            raise TypeError("config field 'order' must be a mapping")

        raw_size = order.get("size", 0.001)
        return cls(
            account_address=_required_text(data, "account_address"),
            private_key=_required_text(data, "private_key"),
            coin=_required_text(order, "coin"),
            price=_positive_number(order.get("price"), "order.price"),
            size=raw_size,
        )
