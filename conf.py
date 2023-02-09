from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='COFFRE-FORT',
    version='1.1',
    description='Projet qui permet l’archivage des fichiers, dans le but de faciliter et améliorer la gestion des fichiers d’une manière sécurisée',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Charki soumia et Amina bengannoun',
    author_email='aminabengannoune@gmail.com',
    url='https://github.com/G1307/COFFRE-FORT',
    license='MIT',
    py_modules=['COFFRE-FORT'],
    install_requires=['cryptography', 'pyAesCrypt'],
    entry_points={
        'console_scripts': [
            'COFFRE-FORT = COFFRE-FORT:main',
        ],
    },
    classifiers=[
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
    ],
)
