import speedtest

def RPi_speedtest():
    #def RPi_speedtest():
    # https://github.com/sivel/speedtest-cli/wiki
    servers = []
    # If you want to test against a specific server
    # servers = [1234]

    threads = None
    # If you want to use a single threaded test
    # threads = 1

    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads, pre_allocate=False)
    s.results.share()

    results_dict = s.results.dict()
    return [results_dict['download'], results_dict['upload'], results_dict['client']['isp']]
