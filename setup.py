from setuptools import setup, find_packages

FULL_VERSION = '0.1.0'

with open('README.md') as f:
    readme = f.read()

setup(
    name='wgan',
    version=FULL_VERSION,
    description='Wasserstein GAN tensorflow implementation.',
    long_description=readme,
    author='Asahi Ushio',
    author_email='aushio@keio.jp',
    packages=find_packages(exclude=('scripts', 'dataset')),
    include_package_data=True,
    test_suite='scripts',
    install_requires=[
        'tensorflow',
        'numpy',
        'pandas',
        'Pillow',
        'toml',
        'scipy'
    ]
)
