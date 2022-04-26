from login import login

def convert_readable_dates(self, epoch):
    '''
        @param: date in epoch milliseconds
        @return: human-readable date
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch/1000.0))

session = login()

stream_client = session.create_streaming_session()

stream_client.write_behavior(
    write='csv',
    file_path=r'data/stream/raw_data.csv',
    append_mode=True
)

stream_client.timesale(
    service='TIMESALE_FUTURES',
    symbols=['/ES'],
    fields=[1, 2, 3, 4]
)

stream_client.stream()