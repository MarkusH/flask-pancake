import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="flask-pancake",
    author="Markus Holtermann",
    author_email="info@markusholtermann.eu",
    description="Feature Flagging for Flask",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarkusH/flask-pancake",
    packages=setuptools.find_packages(),
    install_requires=["flask>=1.0", "flask-redis>=0.4.0"],
    use_scm_version=True,
    setup_requires=["setuptools_scm>=3.4.2,<4"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
)
