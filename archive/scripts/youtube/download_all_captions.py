"""
Download and combine chunked VTT caption files into a single transcript
"""

import urllib.request
import re
import os
from pathlib import Path

# All the VTT URLs from the video
VTT_URLS = [
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/4.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNmY2OTlhMTc0NTUwODMyODEyNDI4NTJiMTQxYTBiMmNhY2IzNjcwYjA5MGM3ZmRkOTM3ODViYWQxMDQ5OTIxNA==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/5.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYzdiMzVlZTQ2MDc0ZDlhYzJkOTQ2YjIwNTdhNGQ3MWQ2MWNhMjA4NTkxY2EwY2JjZjJkMGZjN2ZiNGY4NmViZQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/6.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfODZiYTExYTljMGY2Zjc5ZTE5YmExMDU3NGJkOTk5MzM2YjA4MWZiNjZjYzJkNjJlM2RmMTJmNTlhNzQ2YjI5OA==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/7.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfOWRhZGJkODdlZGNkYWU3NDk4YzM2NjNjZDk3MWFhYzBmZjkzYzkwMTUxOWNkYmI5YjNmMWQzZjQxNmEzOWQ2OA==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/8.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfMWI2MzI0ZmY1NjQxZGE4NGU0OGI1ZmEzYjJmN2Y2M2M1OWY1NGUwYmNlYWJkNmI0MjIyMzViODA2YjUzNzEzOQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/9.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfMGUzYjllMTlkYzdlNjU2NTk1MGIzMGVhMzBkYWIwNzRiYjIyYTAxNmE1ODY1ZDVlOWMxZTM3ZDgyZDI3MjMxNw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/10.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYTc5N2JhMjY1NzA5NDIxZDUxY2JiZTY4MmFlYTBmNmI1NWU1YWQ1MjE4ZTNkZWU5ZTA3YTUxNWIxOWJlM2ExYg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/11.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYjRkMmRkMWU1YTQ2NWI4NDYxMjRiYTJiNDRkMTk2NGY3M2IyNzg5M2EzNmVlOWJiNjY1N2I0ODZkMTEyYzEzNQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/12.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNGMwOWIyYjRhMzQ3MjYwZjdjYWVhNTQ2ODc0Y2MyNjAwYjQ2NGM3NDA2NGQ0ZTMzMDU5Zjk4YjUyMDBiZTZmNQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/13.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYWU0MTY2M2VjOGRhZDk0ZGE3MDFmNDA2ODMzMzY1OTFjN2U4MzZiMDNmM2Y5NDM2NTcxMjc0ODNhYWM0Mzk0NA==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/14.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYjU3ZmFlZGZmZmIzMGQ4MWQwYTU2MWVhOTViODc0N2FjM2FkMTMwMDI4NzgzYTY5ZTJkZmMyODYyMWZkOGRkMg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/15.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfZjc5ZDIyOTAxMTQxZmE0MmRiZjAyMzFlZDE4OTA3MjlmZjQ0NmU4MmExOTE3Zjg1ZDA4MWRjZDk2ZmE3ZWZiMw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/16.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfMGIyM2QwOTY1YzdmOTFjMmM4NjdkYjg4ZjM4ZjliZGMxYTJkZjQxNGE2ZmNjOGNmY2NlNzc0ZTk5NDFkODAyNQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/17.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfZmUxODI5ZTgxMDBjYzdlZjdiMjVhYWU1YzViM2UxMWM5N2E3YzE2ZTVlZDU5NjA4ODU0MmI0ZDhkYTlkMThhMw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/64.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfN2JkZTc2N2ZjYWEzMzcyNmQ1ZTk0NjJhZjJkMmEyMTY5ZWY3MjVlNmM1YTQ3NTJmZDdkMGY4YzAzOTJlNzRiYw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/65.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYjRkOTMzMzhjNDFkMjU0ZWI3NTVmMDk4MzJkNDJmYjY3MzlkZjg2MzkyMzQzODM0MmMyYzk5YzFiNTNmZTE4OQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/66.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNWU0YmRjNjNlYTA3NjhjMTYyNzU2M2M3MTI1NmI5Y2VjNmI0ZTk0ODYzYWMzNTA5Y2E0NGEyMjViNzAwNDdkZg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/67.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfZTBkZjcxMWFlMDliMmYyYWFiMGU5ZjgwY2JiYWM5MTgyMzVjMDgwNWVmMDM4OTUwMmU5OWQzYzFmNjlmNTg5Mw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/68.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYTZlZDM1OGNiODRiZGJhZGYwMzg2NmM3NjNiNjk1ZDY3OTM3MmEyNzVkZGM3MzgwN2FhYjdlMDEzYzU4ZDI2NQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/69.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYTY3ZDRiODQ4MzM3YzMzYzgyMjJkZTFlMGI4MmIxNGIzODY0NDJmZjJmOWRkOTdhNjFhZDg2ZWEzMTg0MTIwMQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/70.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfMTA4NzlkMTI4ZWNjYmMzMDg2ZWI4MmY5NTEwNjYwNjllOGQzMjczNDdiNWFiZGQ1OTJkZTAyZjcyMDk1N2ZkZQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/71.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfZTlhMGVjNTNiY2JhYjMzOTI3MDkyM2JlYWNiOGQ4NWE1YTdjOTI0MmRkMGExZTE5NWNmZmIxNGY5YzRiYTJhZQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/72.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfZDE5ZjA0YTdkMjYwNjIxOWUyODRmNWFkZTNmMmRiM2YyYzljMjhhZDJhYzBhMDJmYzc2YWY0MGVlMWE3MTYzNw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/127.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfM2Y0ZmIzMTQ0YWVjMTI0YTAxMmM1Yzc1NDIwOGI4YWI4ZmVkOGMyZWRkNTVjNDQ4YjM3NWM3Mjk5MTQyZTUwMg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/128.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfM2NkZWE5NmY5MjU4ZGE2YWIxMzQwYTU4YjhiMzc2MzY3ODVmYjdiNTEyNGIwMGJmMjhlYTExZWE2MWZkZmI2Yg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/129.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfODQ4ZTg1YTI1YjA4MjEzYjFhOTZkMThkMmUzYmEzYTFiZDU5YTU0YzZlOWMyMDUzMTBlOWUzNzJjOWNhNDIyNg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/130.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYTZiYzI3YWUzMjlkM2FkYmZiYjVmNmYyOTBjNzkzZTQ4ZWU4ZTRiNWU0NjE0Mjk5ODVhNGEyYzQwOGU0ZTk3ZQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/131.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYzM1NjYwZmJhYmQ1Y2QwY2RiMDE2MzhmNzQwODJjZDdjMjZmZTVkODVmN2U2MGVjZGIyN2VjMDI1NjI1YzVjZg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/132.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNWI0N2U4NzcwZjBkZTMyOTIzZTUxNDhhNWE2MzFkMWQxOGE5ZmUzOGIwMDk1OTMwY2M3ZmM5ZjY4ZjU3NWQxNw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/133.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNjE0N2M2YTk1NWQ5NmJhMTg1YmM2OTQ1OTU1MjE0MjRjM2E1YTVlZDE3ZWJjMzVlNzRhMGEzOWZiZWM2MTU2NQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/134.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNDk0NTI4YzA4MTk0ZmZiMzdkYzUwMjIwZjE4YjQ1YTllMGJhZDU3YTI4YjA3ZWFhMzMwOTM4MDZmZmUzODA3Zg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/135.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYThkYzA3OGYzMmI2OTc4ZTlhMjIyN2ExYWFhOWI2ODg4NDc5ZWZlYmNiODVlNzAxOTk0YzhiZWJjNjE3NDE5OQ==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/136.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNjczYjY0NzViZDI2ZjYyZjMxODEyZmI0ZWYxNGU4ZWFiNzkwZWY0OTQ2NWE1ZDg3ZWU0Zjg3MjE1MDAwYTFhOA==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/141.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNWM3ZDYyMjEzMmM1N2Q3N2QyMTMxNGYwZDg0ZjYzZDM3ZTZiNmY5NjA5YWUxMDE1NzY3YjdhOGJlMWJjNGE5Yg==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/142.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfNzIzNGU2N2Q0ZWUzZjMwNjQ1MDgwM2UwNmU2YmY3OGU0MDc2ZjE4ZDhmZDYwN2E5YTA0NWJkYzhmZDNjZjU3Mw==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/143.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfZjI4NDcyMDY0NjdhMGQ4MmVmZGUxZjc5NDk3NWQ2ODRjZjRiZWE3Yjk2ZGU0MDBmZGY2ZjU3NTJhMTk4ZjQ0Ng==",
    "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/144.vtt?skid=edgemv-default-1&signature=NjkyNTYyMDBfYWZjMGM3MmJhZTY2MWNiNjU2OGM3Mjg2ZDY2YmRiZTlkZTBiZDVlNThkYzRmZTAzYjZiMmMyNGJkOTg5MzIyYQ==",
]

def extract_chunk_number(url):
    """Extract chunk number from URL"""
    match = re.search(r'/(\d+)\.vtt', url)
    return int(match.group(1)) if match else 999999

def clean_vtt_line(line):
    """Clean a single VTT caption line"""
    # Remove HTML tags
    line = re.sub(r'<[^>]+>', '', line)
    # Remove VTT styling tags
    line = re.sub(r'</?[a-z].*?>', '', line)
    return line.strip()

def download_and_parse_vtt(url):
    """Download VTT file and extract text content"""
    try:
        print(f"  Downloading chunk {extract_chunk_number(url)}...", end=" ")
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read().decode('utf-8')

        lines = content.split('\n')
        text_lines = []

        for line in lines:
            line = line.strip()

            # Skip these lines
            if (not line or
                line.startswith('WEBVTT') or
                '-->' in line or
                line.isdigit() or
                line.startswith(('STYLE', 'NOTE', 'Kind:', 'Language:'))):
                continue

            cleaned = clean_vtt_line(line)
            if cleaned:
                text_lines.append(cleaned)

        print("✓")
        return text_lines
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def main():
    print("=" * 60)
    print("VTT Caption Downloader & Transcript Generator")
    print("=" * 60)
    print(f"\nFound {len(VTT_URLS)} caption chunks to download\n")

    # Sort URLs by chunk number
    sorted_urls = sorted(VTT_URLS, key=extract_chunk_number)

    print("Downloading and parsing VTT files:")
    all_text = []

    for url in sorted_urls:
        text_lines = download_and_parse_vtt(url)
        all_text.extend(text_lines)

    # Combine into single transcript
    full_transcript = '\n'.join(all_text)

    # Save to file
    output_file = 'rd_framework_context_window_mastery_transcript.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcript)

    print("\n" + "=" * 60)
    print("✓ TRANSCRIPT EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"\n📄 File saved: {output_file}")
    print(f"📊 Total characters: {len(full_transcript):,}")
    print(f"📊 Total words: {len(full_transcript.split()):,}")
    print(f"📊 Total lines: {len(all_text):,}")
    print("\n" + "=" * 60)
    print("Preview (first 1000 characters):")
    print("=" * 60)
    print(full_transcript[:1000])
    if len(full_transcript) > 1000:
        print("\n... (transcript continues)")
    print("=" * 60)

if __name__ == "__main__":
    main()
