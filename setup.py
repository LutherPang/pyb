from setuptools import setup, find_packages

setup(
    name="pyb",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            "pyb = pyb._pyb:main",
            ],
    },
    description="web bench",
    author="luther",
    author_email="",
    zip_safe=False,
    include_package_data=True,
)
