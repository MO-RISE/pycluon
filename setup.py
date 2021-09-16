from skbuild import setup


setup(
    name="pycluon",
    version="0.1.0",
    description="A python wrapper around libcluon",
    author="Fredrik Olsson",
    packages=["pycluon"],
    cmake_install_dir=".",
    include_package_data=True,
    package_data={
        "pycluon": ["bin/*", "resources/*"],
    },
    entry_points={
        "console_scripts": [
            "cluon-msc=pycluon.scripts:script_entrypoint",
            "cluon-OD4toStdout=pycluon.scripts:script_entrypoint",
            "cluon-OD4toJSON=pycluon.scripts:script_entrypoint",
            "cluon-LCMtoJSON=pycluon.scripts:script_entrypoint",
            "cluon-filter=pycluon.scripts:script_entrypoint",
            "cluon-livefeed=pycluon.scripts:script_entrypoint",
            "cluon-rec2csv=pycluon.scripts:script_entrypoint",
            "cluon-replay=pycluon.scripts:script_entrypoint",
        ]
    },
    install_requires=["protobuf", "protoc-wheel-0"],
)
