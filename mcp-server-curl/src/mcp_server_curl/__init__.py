from . import server

def main():
    """Main entry point for the package."""
    import asyncio
    asyncio.run(server.main())

# Expose important items at package level
__all__ = ['main', 'server']