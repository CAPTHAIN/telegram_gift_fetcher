from setuptools import setup, find_packages

setup(
    name='telegram_gift_fetcher',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'telethon',
        'requests',
        'beautifulsoup4',
    ],
    author='@vetalkaaa (tg)',
    description='A Python library to fetch Telegram user gifts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/CAPTHAIN/telegram_gift_fetcher',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)