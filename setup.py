import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvisascope",
    version="0.0.1",
    author="Julius Zimmermann",
    author_email="julius.zimmermann@uni-rostock.de",
    description="PyVISAScope provides an interface to different scopes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j-zimmermann/PyVISAScope.git",
    packages=setuptools.find_packages(),
    install_requires=[
   'pyvisa>1.5'],
)
