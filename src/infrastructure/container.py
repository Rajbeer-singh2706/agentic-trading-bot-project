"""Dependency injection container."""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import asyncio

from infrastructure.config import get_config
from infrastructure.logging import get_logger


class ServiceContainer:
    """Dependency injection container for managing application services."""

    def __init__(self):
        """Initialize service container."""
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._logger = get_logger(__name__)

    def register(
        self,
        name: str,
        factory,
        singleton: bool = False,
    ) -> None:
        """Register a service.
        
        Args:
            name: Service name
            factory: Callable that creates the service
            singleton: Whether to cache the service instance
        """
        self._services[name] = {
            "factory": factory,
            "singleton": singleton,
        }
        self._logger.debug(f"Registered service: {name}")

    def get(self, name: str) -> Any:
        """Get service instance.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not registered
        """
        if name not in self._services:
            raise KeyError(f"Service not registered: {name}")

        service_config = self._services[name]
        
        # Return singleton if already created
        if service_config["singleton"] and name in self._singletons:
            return self._singletons[name]

        # Create instance
        instance = service_config["factory"]()

        # Cache if singleton
        if service_config["singleton"]:
            self._singletons[name] = instance

        return instance

    def reset(self) -> None:
        """Reset all services."""
        self._singletons.clear()
        self._logger.debug("Services reset")


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get global service container (singleton)."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """Reset global container (for testing)."""
    global _container
    _container = None


class Service(ABC):
    """Base class for services."""

    @abstractmethod
    async def startup(self) -> None:
        """Called when service starts up."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Called when service shuts down."""
        pass


class ApplicationContext:
    """Application context managing service lifecycle."""

    def __init__(self):
        """Initialize application context."""
        self.config = get_config()
        self.container = get_container()
        self.logger = get_logger(__name__)
        self._services: Dict[str, Service] = {}

    def register_service(self, name: str, service: Service) -> None:
        """Register a managed service."""
        self._services[name] = service

    async def startup(self) -> None:
        """Start all registered services."""
        self.logger.info("Application starting up...")
        for name, service in self._services.items():
            try:
                await service.startup()
                self.logger.info(f"Service started: {name}")
            except Exception as e:
                self.logger.error(f"Failed to start service {name}: {e}")
                raise

    async def shutdown(self) -> None:
        """Shut down all registered services."""
        self.logger.info("Application shutting down...")
        for name, service in reversed(list(self._services.items())):
            try:
                await service.shutdown()
                self.logger.info(f"Service stopped: {name}")
            except Exception as e:
                self.logger.error(f"Failed to stop service {name}: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()


# Global application context
_app_context: Optional[ApplicationContext] = None


def get_app_context() -> ApplicationContext:
    """Get global application context (singleton)."""
    global _app_context
    if _app_context is None:
        _app_context = ApplicationContext()
    return _app_context


def reset_app_context() -> None:
    """Reset global application context (for testing)."""
    global _app_context
    _app_context = None
