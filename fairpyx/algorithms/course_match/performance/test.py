
import timeit  # Check performance of functions by running them many times

cy = timeit.timeit('main_course_match_p.main_course_match()',
                    setup='import main_course_match_p',
                    number = 100000 )

py = timeit.timeit('main_course_match.main_course_match()',
                    setup='import main_course_match',
                    number = 100000 )

print(f'cy = {cy}')
print(f'py = {py}')
print(f'Cython is {py/cy} times faster')