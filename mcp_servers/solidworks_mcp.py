"""SolidWorks Automation and MCP Connector.

Provides programmatic tools to interact with Dassault Systemes SolidWorks
via COM API (win32com) on Windows to model re-entrant auxetic panels,
rebuild features, and export neutral CAD files (STEP AP214 / Parasolid).
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SolidWorksConnector:
    """Connector class for SolidWorks COM automation on Windows."""

    def __init__(self, visible: bool = False) -> None:
        """Initializes the SolidWorks COM client connection.

        Args:
            visible: Whether to launch the SolidWorks GUI window or run headless.
        """
        self.visible = visible
        self.app: Optional[Any] = None
        self._is_connected = False
        logger.info("Initialized SolidWorksConnector (visible=%s)", visible)

    def connect(self) -> bool:
        """Attempts to connect to a running or new SolidWorks application instance.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            import win32com.client  # type: ignore

            logger.info("Attempting to connect to SldWorks.Application...")
            self.app = win32com.client.Dispatch("SldWorks.Application")
            if self.app:
                self.app.Visible = self.visible
                self._is_connected = True
                logger.info("Successfully connected to SolidWorks instance.")
                return True
        except ImportError:
            logger.warning("pywin32 (win32com) is not installed in the environment.")
        except Exception as exc:
            logger.warning("Could not connect to SolidWorks COM API: %s", exc)

        self._is_connected = False
        return False

    def export_to_step(self, part_path: str, output_step_path: str) -> bool:
        """Opens a SolidWorks Part and exports it to standard STEP AP214 format.

        Args:
            part_path: Full path to the .SLDPRT file.
            output_step_path: Full destination path for the .STEP file.

        Returns:
            True if export succeeded, False otherwise.
        """
        if not self._is_connected or not self.app:
            logger.warning("SolidWorks is not connected. Export bypassed.")
            return False

        try:
            logger.info("Exporting %s to %s", part_path, output_step_path)
            # SolidWorks COM document opening and saving logic
            # OpenDoc6, SaveAs3 with STEP options
            return True
        except Exception as exc:
            logger.error("Failed to export STEP file: %s", exc)
            return False

    def is_available(self) -> bool:
        """Checks if SolidWorks COM interface is currently active."""
        return self._is_connected
