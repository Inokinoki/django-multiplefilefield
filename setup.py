from setuptools import setup, find_packages


setup(
    name='django-multiplefilefield',
    version=__import__('multiplefilefield').__version__,
    description='Django Model and Form fields which can store multiple files',
    url='https://github.com/Inokinoki/django-multiplefilefield',
    author='Weixuan XIAO(BNBLord)',
    author_email='veyx.shaw@gmail.com',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    package_data={
        'multiplefilefield': [
            'locale/*/LC_MESSAGES/*',
        ],
    },
)