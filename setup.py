from setuptools import setup, find_packages

setup(
    name='realsensepack',
    version='0.2',
    packages=find_packages(),
    include_package_data=False,
    description='A Package Of realsensepack Project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='William Kuang',
    author_email='dakuang2002@126.com',
    url='https://github.com/Ender-William',
    py_modeles = '__init__.py',
    pakages=['realsensepack'],
    install_requires=[
        # 依赖列表
        'numpy>=1.24.2',
        'opencv-python>=4.1.1',
        'pyrealsense2'
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 3 - Alpha"
    ]
)