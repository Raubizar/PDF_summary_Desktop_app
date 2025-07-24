from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="pdf-summarizer-gui",
    version="1.0.0",
    author="PDF Summarizer Team",
    author_email="support@pdfsummarizer.app",
    description="A desktop application for AI-powered PDF and text document summarization using RAG technology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pdfsummarizer/pdf-summarizer-gui",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyPDF2>=3.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "sentence-transformers>=2.2.0",
        "ollama>=0.1.0",
        "PyQt5>=5.15.0",
        "openpyxl>=3.0.0",
        "requests>=2.25.0"
    ],
    extras_require={
        'dev': [
            'pyinstaller>=5.0',
            'pytest>=6.0',
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Environment :: X11 Applications :: Qt",
    ],
    keywords="pdf summarizer ai rag artificial-intelligence document-processing gui desktop-application",
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'pdf-summarizer=main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)