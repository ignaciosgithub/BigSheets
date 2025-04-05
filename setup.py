from setuptools import setup, find_packages

setup(
    name="BigSheets",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "pillow>=8.2.0",
        "sqlalchemy>=1.4.0",
        "pymysql>=1.0.2",
        "psycopg2-binary>=2.9.1",
        "pymongo>=3.12.0",
        "PyQt5>=5.15.0",
        "flask>=2.0.0",
        "plotly>=5.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "sphinx>=4.0.0",
        ],
    },
    author="Ignacio Savi",
    author_email="isavigualco@gmail.com",
    description="A next-generation spreadsheet application with advanced features",
    keywords="spreadsheet, data analysis, visualization",
    python_requires=">=3.8",
)
