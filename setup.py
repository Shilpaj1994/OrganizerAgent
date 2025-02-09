from setuptools import setup, find_packages

setup(
    name="organizer_agent",
    version="0.1.0",
    author="Shilpaj Bhalerao",
    author_email="shilpajbhalerao@gmail.com",
    description="Organizer Agent with Tool Integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "google-generativeai",
        # Add other dependencies from your project
    ],
    tests_require=["pytest"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    # Uncomment if you have console scripts
    # entry_points={
    #     "console_scripts": [
    #         "ai-agent=agent:main",
    #     ],
    # }
) 