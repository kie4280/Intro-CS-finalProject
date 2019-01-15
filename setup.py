from setuptools import setup


setup(
    # Application name:
    name="DriveTube",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="kie",
    author_email="kie",

    # Packages
    packages=["app"],

    # Include additional files into the package
    data_files=[("json", ["client_secret.json", "apikey.json"])],
    include_package_data=True, 

    # Details
    url="https://github.com/kie4280/finalProject",

    #
    # license="LICENSE.txt",
    description="Useful towel-related stuff.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    
    install_requires=[
        "requests", "beautifulsoup4", "httplib2", "google-api-python-client", "oauth2client", "cloudconvert"
    ]
)