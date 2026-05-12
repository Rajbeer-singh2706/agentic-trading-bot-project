"""Core application configuration."""
import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API configuration."""
    base_url: str = field(default_factory=lambda: os.getenv("API_BASE_URL", "http://localhost:8000"))
    host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("API_PORT", 8000)))
    workers: int = field(default_factory=lambda: int(os.getenv("API_WORKERS", 4)))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")
    
    def validate(self) -> None:
        """Validate API configuration."""
        if self.port <= 0 or self.port > 65535:
            raise ValueError(f"Invalid API port: {self.port}")
        if self.workers < 1:
            raise ValueError(f"Invalid worker count: {self.workers}")
        if self.environment not in ["development", "staging", "production"]:
            raise ValueError(f"Invalid environment: {self.environment}")


@dataclass
class SecurityConfig:
    """Security configuration."""
    # Default dev secret: 32+ characters for development
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "dev-secret-key-at-least-32-chars-long-for-development-only"))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_expiry_hours: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRY_HOURS", 24)))
    cors_origins: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501,http://localhost:8000").split(","))
    rate_limit_per_minute: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", 60)))
    require_api_key: bool = field(default_factory=lambda: os.getenv("REQUIRE_API_KEY", "false").lower() == "true")

    def validate(self) -> None:
        """Validate security configuration."""
        # Skip strict JWT validation in development mode (JWT_SECRET can be anything)
        environment = os.getenv("ENVIRONMENT", "development").lower()
        
        # Production mode: enforce strict JWT validation
        if environment == "production":
            if not self.jwt_secret or len(self.jwt_secret) < 32:
                raise ValueError("JWT secret must be at least 32 characters in production")
        
        if self.jwt_expiry_hours <= 0:
            raise ValueError("JWT expiry must be positive")
        if self.rate_limit_per_minute <= 0:
            raise ValueError("Rate limit must be positive")


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))
    file_path: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE_PATH"))
    max_bytes: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_BYTES", 10485760)))
    backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", 5)))

    def validate(self) -> None:
        """Validate logging configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}")
        if self.max_bytes <= 0:
            raise ValueError("Log max bytes must be positive")
        if self.backup_count < 0:
            raise ValueError("Log backup count cannot be negative")


@dataclass
class VectorDBConfig:
    """Vector database configuration."""
    provider: str = field(default_factory=lambda: os.getenv("VECTOR_DB_PROVIDER", "pinecone"))
    api_key: str = field(default_factory=lambda: os.getenv("PINECONE_API_KEY", ""))
    index_name: str = field(default_factory=lambda: os.getenv("PINECONE_INDEX_NAME", "tradingbot"))
    namespace: Optional[str] = field(default_factory=lambda: os.getenv("PINECONE_NAMESPACE"))
    dimension: int = field(default_factory=lambda: int(os.getenv("VECTOR_DIMENSION", 384)))
    top_k: int = field(default_factory=lambda: int(os.getenv("VECTOR_TOP_K", 5)))
    score_threshold: float = field(default_factory=lambda: float(os.getenv("VECTOR_SCORE_THRESHOLD", 0.5)))

    def validate(self) -> None:
        """Validate vector DB configuration."""
        if not self.api_key:
            raise ValueError("Vector DB API key is required")
        if not self.index_name:
            raise ValueError("Vector DB index name is required")
        if self.dimension <= 0:
            raise ValueError("Vector dimension must be positive")
        if self.top_k <= 0:
            raise ValueError("Vector top_k must be positive")
        if not 0 <= self.score_threshold <= 1:
            raise ValueError("Score threshold must be between 0 and 1")


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = field(default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() == "true")
    provider: str = field(default_factory=lambda: os.getenv("CACHE_PROVIDER", "redis"))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    ttl_seconds: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL_SECONDS", 3600)))

    def validate(self) -> None:
        """Validate cache configuration."""
        if self.ttl_seconds <= 0:
            raise ValueError("Cache TTL must be positive")
        if self.provider not in ["redis", "memory"]:
            raise ValueError(f"Invalid cache provider: {self.provider}")


@dataclass
class ModelConfig:
    """Model configuration."""
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "groq"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "mixtral-8x7b-32768"))
    llm_temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", 0.7)))
    llm_max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", 2048)))
    
    embeddings_provider: str = field(default_factory=lambda: os.getenv("EMBEDDINGS_PROVIDER", "huggingface"))
    embeddings_model: str = field(default_factory=lambda: os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2"))
    
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    hf_token: Optional[str] = field(default_factory=lambda: os.getenv("HF_TOKEN"))

    def validate(self) -> None:
        """Validate model configuration."""
        if not self.llm_model:
            raise ValueError("LLM model is required")
        if not self.embeddings_model:
            raise ValueError("Embeddings model is required")
        if self.llm_temperature < 0 or self.llm_temperature > 2:
            raise ValueError("LLM temperature must be between 0 and 2")
        if self.llm_max_tokens <= 0:
            raise ValueError("LLM max tokens must be positive")
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("Groq API key is required when using Groq provider")


@dataclass
class ExternalAPIsConfig:
    """External APIs configuration."""
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    tavily_max_results: int = field(default_factory=lambda: int(os.getenv("TAVILY_MAX_RESULTS", 5)))
    
    polygon_api_key: str = field(default_factory=lambda: os.getenv("POLYGON_API_KEY", ""))
    
    request_timeout: int = field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", 30)))
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", 3)))

    def validate(self) -> None:
        """Validate external APIs configuration."""
        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


@dataclass
class AppConfig:
    """Main application configuration."""
    api: APIConfig = field(default_factory=APIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    vector_db: VectorDBConfig = field(default_factory=VectorDBConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    external_apis: ExternalAPIsConfig = field(default_factory=ExternalAPIsConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        config = cls()
        return config

    def validate_all(self) -> None:
        """Validate all configuration sections."""
        self.api.validate()
        self.security.validate()
        self.logging.validate()
        self.vector_db.validate()
        self.cache.validate()
        self.model.validate()
        self.external_apis.validate()

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.api.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.api.environment == "development"


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get global configuration instance (singleton)."""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
        _config.validate_all()
    return _config


def reset_config() -> None:
    """Reset global configuration (for testing)."""
    global _config
    _config = None
