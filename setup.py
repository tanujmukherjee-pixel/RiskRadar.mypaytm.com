from setuptools import setup, find_packages

setup(
    name="agency",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "": ["data/*"],  # Include all files in the data directory
    }
) 
