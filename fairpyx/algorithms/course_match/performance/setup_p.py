# from setuptools import setup
# from Cython.Build import cythonize

# setup(
#     ext_modules=cythonize("fairpyx/algorithms/course_match/performance/remove_oversubscription.pyx"),
# )


from setuptools import setup, Extension
from Cython.Build import cythonize

# List of source files to be compiled
ext_modules = [
    Extension(
        "remove_oversubscription1",
        sources=["fairpyx/algorithms/course_match/performance/remove_oversubscription1.pyx"],
    ),
    Extension(
        "reduce_undersubscription",
        sources=["fairpyx/algorithms/course_match/performance/reduce_undersubscription.pyx"],
    ),
]

setup(
    name="course_allocation_tools",
    version="1.0",
    description="A package for course allocation algorithms",
    ext_modules=cythonize(ext_modules),
    install_requires=[
        "fairpyx",  # Assuming fairpyx is a required package
        "cython",
    ],
)
