setup(
    name="lingshe-tradebot-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "asyncio>=3.4.3",
        "aiohttp>=3.9.1",
        "pydantic>=2.5.2",
        "SQLAlchemy>=2.0.23",
        "aiosqlite>=0.19.0",
        "cryptography>=41.0.7",
        "ccxt>=4.1.13",
        "pandas>=2.1.3",
        "numpy>=1.26.2",
        "loguru>=0.7.2",
        "prometheus-client>=0.19.0",
    ],
    python_requires=">=3.9",
    author="LingShe Team",
    author_email="team@lingshe.com",
    description="LingShe TradeBot Backend",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lingshe/tradebot",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
