import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name='aioaws',
        version='0.1.1',
        author='David Poirier',
        author_email='dpoirier@y7mail.com',
        description='Async Python client for AWS services with no dependencies',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/david-poirier-csn/aioaws',
        packages=setuptools.find_packages(),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: Apache Software License'
        ]
)

