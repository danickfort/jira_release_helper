from setuptools import setup, find_packages
setup(
    name='jira-release-helper',
    version='1.0',
    author='Danick Fort',
    description='Helps commenting on Jira issues when deploying code',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['jira_release=jira_release.jira_release:main']
    },
    install_requires=[
        'setuptools',
        'fire >= 0.4.0',
        'jira >= 3.0.1'
    ],
    python_requires='>=3.5'
)
