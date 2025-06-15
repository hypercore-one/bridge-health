"""Background service for automatically updating orchestrator status data"""

import time
import threading
from typing import Optional

from app.services.status_service import StatusService


class BackgroundUpdater:
    """Background service that periodically updates orchestrator status."""
    
    def __init__(self, update_interval: int = 60, app=None):
        """
        Initialize the background updater.
        
        Args:
            update_interval: Time in seconds between updates (default: 60)
            app: Flask application instance
        """
        self.update_interval = update_interval
        self.app = app
        self.status_service = StatusService()
        self.stop_event = threading.Event()
        self.update_thread: Optional[threading.Thread] = None
        self.logger = None
        self.initial_update_done = threading.Event()
        
    def _get_logger(self):
        """Get logger instance."""
        if self.logger is None:
            try:
                from flask import current_app
                if hasattr(current_app, 'logger_instance'):
                    self.logger = current_app.logger_instance
                else:
                    raise RuntimeError("No logger in app context")
            except RuntimeError:
                # Fallback if called outside app context
                from config.logging import setup_logging
                self.logger = setup_logging('background_updater')
        return self.logger
    
    def _update_loop(self):
        """Main update loop that runs in the background thread."""
        logger = self._get_logger()
        logger.info(f"Background updater started with {self.update_interval}s interval")
        
        # Always wait for initial update signal or timeout
        self.initial_update_done.wait(timeout=10)
        
        while not self.stop_event.is_set():
            # Wait for the specified interval
            if self.stop_event.wait(self.update_interval):
                break  # Stop event was set
                
            try:
                # Update orchestrator status with app context
                logger.info("Starting background status update...")
                if self.app:
                    with self.app.app_context():
                        self.status_service.update_status()
                else:
                    self.status_service.update_status()
                logger.info("Background status update completed")
                
            except Exception as e:
                logger.error(f"Error in background update loop: {e}")
                # Wait a shorter time before retrying on error
                self.stop_event.wait(min(30, self.update_interval))
    
    def start(self):
        """Start the background updater thread."""
        if self.update_thread and self.update_thread.is_alive():
            self._get_logger().warning("Background updater is already running")
            return
        
        self.stop_event.clear()
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        self._get_logger().info("Background updater thread started")
    
    def stop(self):
        """Stop the background updater thread."""
        if self.update_thread and self.update_thread.is_alive():
            self._get_logger().info("Stopping background updater...")
            self.stop_event.set()
            # Only join if it's not the current thread
            if self.update_thread != threading.current_thread():
                self.update_thread.join(timeout=10)
                if self.update_thread.is_alive():
                    self._get_logger().warning("Background updater thread did not stop gracefully")
                else:
                    self._get_logger().info("Background updater stopped successfully")
            else:
                self._get_logger().info("Background updater stopped (current thread)")
        
        # Close the status service
        self.status_service.close()
    
    def is_running(self) -> bool:
        """Check if the background updater is currently running."""
        return self.update_thread is not None and self.update_thread.is_alive()
    
    def force_update(self):
        """Force an immediate status update."""
        try:
            logger = self._get_logger()
            logger.info("Forcing immediate status update...")
            if self.app:
                with self.app.app_context():
                    self.status_service.update_status()
            else:
                self.status_service.update_status()
            # Mark initial update as done
            self.initial_update_done.set()
            logger.info("Forced status update completed")
        except Exception as e:
            self._get_logger().error(f"Error in forced update: {e}")
            raise