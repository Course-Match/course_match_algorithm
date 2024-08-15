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
        "remove_oversubscription_p",
        sources=["fairpyx/algorithms/course_match/performance/remove_oversubscription_p.pyx"],
    ),
    Extension(
        "reduce_undersubscription_p",
        sources=["fairpyx/algorithms/course_match/performance/reduce_undersubscription_p.pyx"],
    ),
    Extension(
        "A_CEEI_p",
        sources=["fairpyx/algorithms/course_match/performance/A_CEEI_p.pyx"],
    ),
    Extension(
        "main_course_match_p",
        sources=["fairpyx/algorithms/course_match/performance/main_course_match_p.pyx"],
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


"""
python3 fairpyx/algorithms/course_match/performance/setup.py build_ext --inplace
python3 fairpyx/algorithms/course_match/performance/test.py 
"""