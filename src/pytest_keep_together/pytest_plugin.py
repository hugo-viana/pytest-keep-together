"""pytest-keep-together plugin."""

import logging
from dataclasses import dataclass, field
from inspect import getmodule
from typing import Any, List, Optional

from _pytest.python import Function

logger = logging.getLogger(__name__)


@dataclass
class Item:
    """Pytest test item (with custom attributes for keep_together plugin."""

    item: Function
    module: Any = field(init=False)
    group: Optional[str] = field(init=False, default=None)
    cls_name: Optional[str] = field(init=False, default=None)

    def __post_init__(self) -> "Item":
        """Calculate Item attributes on instance initialization.

        Returns:
            Item: self.

        """
        # Save module attr
        self.module = getmodule(self.item._obj)

        # Exit if not a 'keep_together' marked test
        if self.check_keep_together() is False:
            return self

        # Save class attr (if it's a method and not a independent function)
        try:
            self.cls_name = self.item._obj.__self__.__class__.__qualname__
        except AttributeError:
            pass

        logger.debug(f"New 'keep_together' item discovered: {self!s}")
        return self

    def check_keep_together(self) -> bool:
        """Check if item is a 'keep_together' test and store specific attrs.

        Returns:
            bool: True if it's a 'keep_together' test. False otherwise.

        Raises:
            ValueError: pytest keep_together marker argument can't start with
                parenthesis '('.

        """
        # Is this a 'keep_together' marked test?
        for mark in self.item.iter_markers(name="keep_together"):
            self.group = "(default group)"
            if mark.args:
                if str(mark.args[0]).startswith("("):
                    raise ValueError(
                        "pytest keep_together marker argument can't start "
                        + "with parenthesis '('",
                    )
                self.group = mark.args[0]
                break
        else:
            # No, it's not a 'keep_together' marked test
            logger.debug(f"New 'standard' item discovered: {self!s}")
            return False
        # Yes, it's a 'keep_together' marked test
        return True

    def __str__(self) -> str:
        """Get string representation of Item.

        Returns:
            str: string representation of Item.

        """
        txt_repr = str(self.module.__name__)
        if self.group:
            txt_repr += f"::{self.group}"
        if self.cls_name:
            txt_repr += f"::{self.cls_name}"
        txt_repr += f"::{self.item.name}"
        return txt_repr

    def __lt__(self, other: Any) -> bool:
        """Assert if self Item is less than other Item.

        Args:
            other: other Item instance.

        Returns:
            bool: True if self Item is less than other Item. False otherwise.

        """
        if not isinstance(other, Item):
            return NotImplemented

        # Handle null values
        self_group_str = self.group or ""
        other_group_str = other.group or ""
        self_cls_name = self.cls_name or ""
        other_cls_name = other.cls_name or ""
        self_module_name = self.module.__name__ or ""
        other_module_name = other.module.__name__ or ""

        # Calculate __lt__ by parts
        group_lt = self_group_str < other_group_str
        cls_name_lt = self_cls_name < other_cls_name
        module_name_lt = self_module_name < other_module_name

        # Evaluate aggregated __lt__ parts
        return any([group_lt, cls_name_lt, module_name_lt])


def pytest_collection_modifyitems(config: Any, items: List[Function]) -> None:
    """Alter pytest collection of item tests (ordering).

    Args:
        config: pytest config.
        items: list of collected test items.

    """
    if len(items) > 0:
        logger.debug(
            "Pytest test collection before keep_together reordering:\n> "
            + "\n> ".join(str(i) for i in items),
        )
    items_ = [Item(item) for item in items]
    items_.sort()
    items[:] = [i.item for i in items_]
    if len(items) > 0:
        logger.debug(
            "Pytest test collection after keep_together reordering:\n> "
            + "\n> ".join(str(i) for i in items_),
        )
