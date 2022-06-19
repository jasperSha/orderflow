from login import login

def convert_readable_dates(self, epoch):
    '''
        @param: date in epoch milliseconds
        @return: human-readable date
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch/1000.0))

"""
level one futures (time n sales):
1: bid
2: ask
3: last
4: bid size
5: ask size

8: total volume (from day begin to current)
9: last traded size
10: time of last quote (ms)
11: time of last trade (ms)
12: day's highest traded price
13: day's lowest traded price
14: previous closing price


"""

session = login()

stream_client = session.create_streaming_session()

stream_client.write_behavior(
    write='csv',
    file_path=r'data/stream/raw_data.csv',
    append_mode=True
)

# stream_client._level_two_futures(
#     symbols=['/ES'],
#     fields=[0, 1, 2]
# )

stream_client.timesale(
    service='TIMESALE_FUTURES',
    symbols=['/ES'],
    fields=[1, 2, 3, 4]
)

stream_client.stream()