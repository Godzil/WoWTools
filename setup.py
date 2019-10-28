import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wowfile',
    use_scm_version={
        'write_to': 'WowFile/_version.py',
    },
    setup_requires=['setuptools_scm'],
    author="Manoel <godzil> Trapier",
    author_email="wowfile@godzil.net",
    description="A library and simple viewer to manipulate SparkMaker WOW files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['bin/wowviewer'],
    url="https://github.com/Godzil/WoWTools",
    packages=["WowFile"],
    install_requires=[
        "Pillow",
        "tkinter",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    python_requires='>=3.6',
)
