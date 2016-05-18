import setuptools

setuptools.setup(
    description="Logging and metric reporting for Rhoana pipeline",
    entry_points={
        "rh_logger.backend": {
            "default = rh_logger.backends.backend_python_logging:get_logger"
        }
    },
    install_requires=["enum34>=1.0.4"],
    name="rh_logger",
    packages=["rh_logger", "rh_logger.backends"],
    url="https://github.com/Rhoana/rh_logger",
    version="0.1.0"
)
