import multiprocessing

bind = "0.0.0.0:8000"
backlog = 128
workers = multiprocessing.cpu_count() * 2 + 1
x_forwarded_for_header = True