class Config:
    """Base configuration class."""
    DEBUG = False
    TESTING = False
    DATABASE_URI = ''

class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    """Configuration for production environment."""
    DATABASE_URI = 'postgresql://user:pass@localhost/prod'

class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    DATABASE_URI = 'sqlite:///test.db'