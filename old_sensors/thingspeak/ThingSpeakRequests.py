import RPi.GPIO as GPIO
import time
import requests
import json
import numpy as np
import datetime

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BOARD)  # Number GPIOs by its pin location
DEFAULT = object()  # can use also None

"""
# ## initializing thingspeak http api
# chanel_id = '746133'
# api_key = 'F6G7Y748RPVAK8L9'
# inst_thingspeak = ThingSpeakRequests(api_key=api_key)
"""
class ThingSpeakRequests:
    """ThingSpeak HTTP API
    Init method

    Parameters
    ----------
    api_key : <string>
        (Required for private channels) Specify Read API Key for this specific channel. The Read API Key is found on
        the API Keys tab of the channel view.

    Attributes
    ----------
    api_key : <string>
        (Required for private channels) Specify Read API Key for this specific channel. The Read API Key is found on
        the API Keys tab of the channel view.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def Bulk_Write_JSON_Data(self, chanel_id=DEFAULT, values=DEFAULT, created_at=DEFAULT, delta_t=DEFAULT, latitude=DEFAULT,
                             longitude=DEFAULT, elevation=DEFAULT, status=DEFAULT):
        """Write many entries to a channel in JSON format with a single HTTP POST.
        To conserve device power or group channel updates, you can use the bulk-update API. When using the bulk-update
        API, you collect data over time, and then upload the data to ThingSpeak™. To write data in CSV format,
        see Bulk-Write CSV Data. To write a single entry, see Write Data.
        Webpage: https://it.mathworks.com/help/thingspeak/bulkwritejsondata.html

        Parameters
        ----------
        chanel_id : <string>
            Channel ID for the channel of interest.
        values : list of <any> in form: [[value of field 1 of block 1, value of field 2 of block 1,...], [value of field 1 of block 2, value of field 2 of block 2,...]]
             Data of the field(s)
        created_at : list of <string> in form: [datetime of block 1, datetime of block 2,...]
            (Required unless delta_t included) absolute time of the event in ISO 8601, EPOCH, or MYSQL formats. Must be unique within channel.
        delta_t : list of <string> in form: [datetime of block 1, datetime of block 2,...]
            (Required unless created_at included) Specify time between measurements with delta_t.
        latitude : list of <number> in form: [latitude of block 1, latitude of block 2,...], optional
            Latitude in degrees.
        longitude : list of <number> in form: [longitude of block 1, longitude of block 2,...], optional
            Longitude in degrees.
        elevation : list of <string> in form: [elevation of block 1, elevation of block 2,...], optional
            Elevation in meters.
        status : list of <string> in form: [status of block 1, status of block 2,...], optional
            Message for status field entry.

        Returns
        -------
        strings
            Error Codes: https://it.mathworks.com/help/thingspeak/error-codes.html

        References
        --------
        [1] https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard


        Examples
        --------
        """

        params = ['chanel_id', 'values', 'created_at', 'delta_t', 'latitude', 'longitude', 'elevation', 'status']
        locs = locals()
        params = [param for param in params if eval(param, locs) != DEFAULT]

        if ('created_at' or 'delta_t' in params) and ('values' in params) and ('chanel_id' in params):
            pass
        else:
            return 'Missing required parameters. Check: (created_at or delta_t), values and chanel_id.'


        # create a dictionary of each parameter(key) and their shapes(value)
        shape_list = [(i, self._check_shape(eval(i, locs))) for i in params]  # By using list comprehension, you actually define a new scope.
        shape_dict = {}
        shape_dict.update(shape_list)

        number_of_blocks = shape_dict['values'][0]
        number_of_fields = shape_dict['values'][1]

        # check the shape of each parameter. Apart from the parameter values, all should have exactly the length of
        # blocks.
        keys = [key for key, value in shape_dict.items()]
        for key in keys:
            if shape_dict[key][0] != 1 or shape_dict[key][1] != number_of_blocks:
                del shape_dict[key]
        try:
            del shape_dict['values']
        except:
            pass

        url = 'https://api.thingspeak.com/channels/{}/bulk_update.json'.format(chanel_id)

        # Fetch the remaining parameters, after filtering by size. If there is no remaining, exit.
        params = [key for key, _ in shape_dict.items()]
        if not params:  # means: if params is empty
            return 'Some parameter might have the wrong shape'

        # create the dictionary that eventually will be converted to JSON format.
        main_dict = {'write_api_key': self.api_key, 'updates': []}
        for i in range(number_of_blocks):
            blocks_dict = {}
            block_header = [('{}'.format(key), eval(key, locs)[i]) for key, _ in shape_dict.items()]
            block_params = [('field{}'.format(j+1), int(values[i][j])) for j in range(number_of_fields)]
            blocks_dict.update(block_header)
            blocks_dict.update(block_params)
            main_dict['updates'].append(blocks_dict)

        # converting dictionary to JSON.
        y = json.dumps(main_dict)

        print(y)
        r = requests.post(url, data=y, headers=self.headers)
        print(r.status_code, r.reason)

    def write_data_json(self, field_index=DEFAULT, field_value=DEFAULT, created_at=DEFAULT, lat=DEFAULT, long=DEFAULT,
                        elevation=DEFAULT, status=DEFAULT, twitter=DEFAULT, tweet=DEFAULT):
        """Update channel data with HTTP POST
        Webpage: https://it.mathworks.com/help/thingspeak/writedata.html
        Parameters
        ----------
        api_key : <string>
            (Required) Specify Write API Key for this specific channel. The Write API Key can optionally be sent via
            a THINGSPEAKAPIKEY HTTP header. The Write API Key is found on the API Keys tab of the channel view.
        field_index : <string>
            (Required) Channel ID for the channel of interest.
        field_value : <any>
             (Required) Data of the field(s)
        created_at : <datetime>
            (Optional) Date when feed entry was created, in ISO 8601 format, for example: 2014-12-31 23:59:59.
            Must be unique within channel. Time zones can be specified via the timezone parameter.
        lat : <decimal>
            (Optional) Latitude in degrees.
        long : <decimal>
            (Optional) Longitude in degrees.
        elevation : int
            (Optional) Elevation in meters.
        status : <string>
            (Optional) Message for status field entry.
        twitter : <string>
            (Optional) Twitter® username linked to ThingTweet.
        tweet : <string>
            (Optional) Twitter® username linked to ThingTweet.

        Returns
        -------
        strings
            Error Codes: https://it.mathworks.com/help/thingspeak/error-codes.html


        Examples
        --------
        """
        url = 'https://api.thingspeak.com/update.{}'.format('json')

        locs = locals()
        params = ['field_index', 'field_value', 'created_at', 'lat', 'long', 'elevation', 'status', 'twitter', 'tweet']
        params = [param for param in params if eval(param, locs) != DEFAULT]

        if ('field_index' in params) and ('field_value' in params):
            pass
        else:
            return 'Missing required parameters. Check: (created_at or delta_t), values and chanel_id.'

        shape_list = [(i, self._check_shape(eval(i, locs))) for i in params]  # By using list comprehension, you actually define a new scope.
        shape_dict = {}
        shape_dict.update(shape_list)

        if shape_dict['field_index'] != shape_dict['field_value']:
            return 'field_index and field_value not matching in size.'

        number_of_blocks = shape_dict['field_value'][0]
        if number_of_blocks != 1:
            return 'number of blocks > 1, for that, use Bulk_Write_JSON_Data function'
        number_of_fields = shape_dict['field_value'][1]

        keys = [key for key, value in shape_dict.items()]
        for key in keys:
            if shape_dict[key][0] != 1 or shape_dict[key][1] != 1:
                del shape_dict[key]

        keys = [key for key, value in shape_dict.items()]
        main_dict = {'api_key': self.api_key}
        params_dict = [('{}'.format(key), eval(key, locs)) for key, value in shape_dict.items()]
        fields_dict = [('field{}'.format(field_index[i]), field_value[i]) for i in range(number_of_fields)]
        main_dict.update(params_dict)
        main_dict.update(fields_dict)

        y = json.dumps(main_dict)
        print(y)
        r = requests.post(url, data=y, headers=self.headers)
        print(r.status_code, r.reason)
        #time.sleep(1)  # if you dnt put this, thingspeak do not get updated

    def ReadData(self, chanel_id=DEFAULT, format='json', results=DEFAULT, days=DEFAULT, minutes=DEFAULT, start=DEFAULT, end=DEFAULT,
                 timezone=DEFAULT, offset=DEFAULT, status=DEFAULT, metadata=DEFAULT, location=DEFAULT, min=DEFAULT,
                 max=DEFAULT, round=DEFAULT, timescale=DEFAULT, sum=DEFAULT, average=DEFAULT, median=DEFAULT,
                 callback=DEFAULT):
        """Read data from all fields in a channel with HTTP GET
        Webpage: https://it.mathworks.com/help/thingspeak/readdata.html

    Parameters
        ----------
        chanel_id : <string>
            (Required) Channel ID for the channel of interest.
        format : <string>
            (Required) Format for the HTTP response, specified as json or xml.
        results : <integer>
            (Optional) Number of entries to retrieve. The maximum number is 8,000.
        days: <integer>
            (Optional) Number of 24-hour periods before now to include in response. The default is 1.
        minutes : <integer>
            (Optional) Number of 60-second periods before now to include in response. The default is 1440.
        start : <datetime>
            (Optional) Start date in format YYYY-MM-DD%20HH:NN:SS
        end : <datetime>
            (Optional) End date in format YYYY-MM-DD%20HH:NN:SS.
        timezone : <integer>
            (Optional) Identifier from Time Zones Reference for this request.
            https://it.mathworks.com/help/thingspeak/time-zones-reference.html
        offset :
            (Optional) Timezone offset that results are displayed in. Use the timezone parameter for greater accuracy.
        status : <true/false>
            (Optional) Include status updates in feed by setting "status=true".
        metadata : <true/false>
            (Optional) Include metadata for a channel by setting "metadata=true".
        location : 	<true/false>
            (Optional) Include latitude, longitude, and elevation in feed by setting "location=true".
        min : <decimal>
            (Optional) Minimum value to include in response.
        max : <decimal>
            (Optional) Maximum value to include in response.
        round : <integer>
            (Optional) Round to this many decimal places.
        timescale : <integer> or <string>
            (Optional) Get first value in this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        sum : <integer> or <string>
            (Optional) Get sum of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        average : <integer> or <string>
            (Optional) Get average of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        median : <integer> or <string>
            (Optional) Get median of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        callback : <string>
            (Optional) Function name to be used for JSONP cross-domain requests.
        Returns
        -------
        strings
            The response is a JSON object of the channel feed.
            Error Codes: https://it.mathworks.com/help/thingspeak/error-codes.html

        Examples
        --------
        """
        locs = locals()
        params = ['chanel_id', 'format', 'results', 'days', 'minutes', 'start', 'end',
                     'timezone', 'offset', 'status', 'metadata', 'location', 'min',
                     'max', 'round', 'timescale', 'sum', 'average', 'median',
                     'callback'
                 ]
        params = [param for param in params if eval(param, locs) != DEFAULT]
        if 'chanel_id' in params and 'format' in params and (format == 'json' or format == 'xml'):
            pass
        else:
            return 'Required parameter: chanel_id, format and json. Something went wrong.'

        shape_list = [(i, self._check_shape(eval(i, locs))) for i in params]  # By using list comprehension,
        # you actually define a new scope. This list comprehension disconsiders all parameters with value DEFAULT.
        shape_dict = {}
        shape_dict.update(shape_list)

        keys = [key for key, value in shape_dict.items()]
        for key in keys:
            if shape_dict[key][0] != 0 or shape_dict[key][1] != 0:
                del shape_dict[key]
        try:
            del shape_dict['chanel_id']
            del shape_dict['format']

        except:
            return 'Parameters: chanel_id or format not valid.'

        keys = [key for key, value in shape_dict.items()]

        url = 'https://api.thingspeak.com/channels/{}/feeds.json'.format(chanel_id, format)
        query_str_begin = '?'
        query_str_separator = '&'
        paramNames_equalSign_paramValues = ['{}={}'.format(key, eval(key, locs)) for key in keys]
        s = query_str_separator.join(paramNames_equalSign_paramValues)
        y = url+query_str_begin+s
        r = requests.get(y)
        print(r.status_code, r.reason, r.json())

    def ReadField(self, chanel_id=DEFAULT, field_id=DEFAULT, format='json', results=DEFAULT, days=DEFAULT,
                  minutes=DEFAULT, start=DEFAULT, end=DEFAULT,
                 timezone=DEFAULT, offset=DEFAULT, status=DEFAULT, metadata=DEFAULT, location=DEFAULT, min=DEFAULT,
                 max=DEFAULT, round=DEFAULT, timescale=DEFAULT, sum=DEFAULT, average=DEFAULT, median=DEFAULT,
                 callback=DEFAULT):
        """Read data from a single field of a channel with HTTP GET
        Webpage: https://it.mathworks.com/help/thingspeak/readfield.html

        Parameters
        ----------
        chanel_id : <string>
            (Required) Channel ID for the channel of interest.
        field_id : <string>
            (Required) Field ID for the channel of interest.
        format : <string>
            (Required) Format for the HTTP response, specified as json, xml, or csv.
        results : <integer>
            (Optional) Number of entries to retrieve. The maximum number is 8,000.
        days: <integer>
            (Optional) Number of 24-hour periods before now to include in response. The default is 1.
        minutes : <integer>
            (Optional) Number of 60-second periods before now to include in response. The default is 1440.
        start : <datetime>
            (Optional) Start date in format YYYY-MM-DD%20HH:NN:SS
        end : <datetime>
            (Optional) End date in format YYYY-MM-DD%20HH:NN:SS.
        timezone : <integer>
            (Optional) Identifier from Time Zones Reference for this request.
            https://it.mathworks.com/help/thingspeak/time-zones-reference.html
        offset :
            (Optional) Timezone offset that results are displayed in. Use the timezone parameter for greater accuracy.
        status : <true/false>
            (Optional) Include status updates in feed by setting "status=true".
        metadata : <true/false>
            (Optional) Include metadata for a channel by setting "metadata=true".
        location : 	<true/false>
            (Optional) Include latitude, longitude, and elevation in feed by setting "location=true".
        min : <decimal>
            (Optional) Minimum value to include in response.
        max : <decimal>
            (Optional) Maximum value to include in response.
        round : <integer>
            (Optional) Round to this many decimal places.
        timescale : <integer> or <string>
            (Optional) Get first value in this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        sum : <integer> or <string>
            (Optional) Get sum of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        average : <integer> or <string>
            (Optional) Get average of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        median : <integer> or <string>
            (Optional) Get median of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
        callback : <string>
            (Optional) Function name to be used for JSONP cross-domain requests.
        Returns
        -------
        strings
            The response is a JSON object of the channel feed.
            Error Codes: https://it.mathworks.com/help/thingspeak/error-codes.html

        Examples
        --------
        """

        locs = locals()
        params = [
            'chanel_id', 'format', 'field_id', 'results', 'days', 'minutes', 'start', 'end', 'timezone', 'offset', 'status',
            'metadata', 'location', 'min', 'max', 'round', 'timescale', 'sum', 'average', 'median', 'callback'
                 ]
        params = [param for param in params if eval(param, locs) != DEFAULT]
        if 'chanel_id' in params and 'field_id' in params and \
                (format == 'json' or format == 'xml' or format == 'csv'):
            pass
        else:
            return 'Required parameter: chanel_id and/or field_id and/or format.'

        shape_list = [(i, self._check_shape(eval(i, locs))) for i in params]  # By using list comprehension,
        # you actually define a new scope. This list comprehension disconsiders all parameters with value DEFAULT.
        shape_dict = {}
        shape_dict.update(shape_list)

        keys = [key for key, value in shape_dict.items()]
        for key in keys:
            if shape_dict[key][0] != 0 or shape_dict[key][1] != 0:
                del shape_dict[key]

        try:  # if chanel_id does not exist in shape dict, it means it has been already deleted, hence it had a wrong shape (!=[0,0] (scalar))
            del shape_dict['chanel_id']
        except:
            return 'chanel_id not valid'

        keys = [key for key, value in shape_dict.items()]

        url = 'https://api.thingspeak.com/channels/{}/fields/{}.{}'.format(chanel_id, field_id, format)
        query_str_begin = '?'
        query_str_separator = '&'
        paramNames_equalSign_paramValues = ['{}={}'.format(key, eval(key, locs)) for key in keys]
        s = query_str_separator.join(paramNames_equalSign_paramValues)
        y = url+query_str_begin+s
        r = requests.get(y)
        print(r.status_code, r.reason, r.json())

    def ReadStatus(self, chanel_id=DEFAULT, format='json', results=DEFAULT, timezone=DEFAULT, offset=DEFAULT, callback=DEFAULT):
        """Read status field of a channel with HTTP GET
        Webpage: https://it.mathworks.com/help/thingspeak/readstatus.html

        Parameters
        ----------
        chanel_id : <string>
            (Required) Channel ID for the channel of interest.
        format : <string>
            (Optional) Format for the HTTP response, specified as json, xml, or csv.
        results : <integer>
            (Optional) Number of entries to retrieve. The maximum number is 8,000.
        timezone : <integer>
            (Optional) Identifier from Time Zones Reference for this request.
            https://it.mathworks.com/help/thingspeak/time-zones-reference.html
        offset :
            (Optional) Timezone offset that results are displayed in. Use the timezone parameter for greater accuracy.
        callback : <string>
            (Optional) Function name to be used for JSONP cross-domain requests.
        Returns
        -------
        strings
            The response is a JSON object of the channel feed.
            Error Codes: https://it.mathworks.com/help/thingspeak/error-codes.html
        Examples
        --------
        """

        locs = locals()
        params = ['chanel_id', 'format', 'results', 'timezone', 'offset', 'callback']
        params = [param for param in params if eval(param, locs) != DEFAULT]
        if 'chanel_id' in params and 'format' in params and \
                (format == 'json' or format == 'csv' or format == 'xml'):
            pass
        else:
            return 'Required parameter: chanel_id and/or field_id and/or format not found.'

        shape_list = [(i, self._check_shape(eval(i, locs))) for i in params]  # By using list comprehension,
        # you actually define a new scope. This list comprehension disconsiders all parameters with value DEFAULT.
        shape_dict = {}
        shape_dict.update(shape_list)

        keys = [key for key, value in shape_dict.items()]
        for key in keys:
            if shape_dict[key][0] != 0 or shape_dict[key][1] != 0:
                del shape_dict[key]

        try:  # if chanel_id does not exist in shape dict, it means it has been already deleted, hence it had a wrong shape (!=[0,0] (scalar))
            del shape_dict['chanel_id']
        except:
            return 'chanel_id not valid'

        keys = [key for key, value in shape_dict.items()]

        url = 'https://api.thingspeak.com/channels/{}/status.{}'.format(chanel_id, 'json')
        query_str_begin = '?'
        query_str_separator = '&'
        paramNames_equalSign_paramValues = ['{}={}'.format(key, eval(key, locs)) for key in keys]
        s = query_str_separator.join(paramNames_equalSign_paramValues)
        y = url+query_str_begin+s
        r = requests.get(y)
        print(r.status_code, r.reason, r.json())

    def _check_shape(self, value):
        value = np.asarray(value)
        if len(value.shape) == 1:
            c = value.shape[0]  # if numpy array
            number_of_fields = c
            number_of_blocks = 1
            shape = [number_of_blocks, number_of_fields]
            return shape

        elif len(value.shape) == 2:
            l, c = value.shape
            number_of_fields = c
            number_of_blocks = l
            shape = [number_of_blocks, number_of_fields]
            return shape

        else:
            shape = [0, 0]
            return shape

class LedModule:
    def __init__(self, pin_vdd):
        self.pin_vdd = pin_vdd

    def config(self):
        GPIO.setup(self.pin_vdd, GPIO.OUT)

    def start(self):
        GPIO.output(self.pin_vdd, 1)

    def stop(self):
        GPIO.output(self.pin_vdd, 0)

    def blink(self, t, times):
        for i in range(times):
            GPIO.output(self.pin_vdd, 1)
            time.sleep(t)
            GPIO.output(self.pin_vdd, 0)
            time.sleep(t)


class MicModule:
    def __init__(self, pin_vdd, pin_dig, url_thingspeak, key_thingspeak):
        self.pin_vdd = pin_vdd
        self.pin_dig = pin_dig
        self.url = url_thingspeak
        self.key = key_thingspeak
        self.count_control = True

    def config(self):
        GPIO.setup(self.pin_vdd, GPIO.OUT)
        GPIO.setup(self.pin_dig, GPIO.IN)

    def start(self):
        GPIO.output(self.pin_vdd, 1)

    def stop(self):
        GPIO.output(self.pin_vdd, 0)

    def get(self):
        data = GPIO.input(self.pin_dig)
        print(data)

    def set_event_detector(self, inst_led):
        self.inst_led = inst_led
        self.int_request = ThingSpeakRequests(api_key=self.key)
        GPIO.add_event_detect(self.pin_dig, GPIO.RISING, callback=self.event_callback, bouncetime=1000)  # add rising edge detection on a channel, ignoring further edges for 200ms for switch bounce handling
        # GPIO.add_event_callback(self.pin_dig, self.event_callback)

    def event_callback(self, channel):
        print('Noise Detected in channel {}'.format(channel))
        if self.count_control:
            self.count_control = False
            self.inst_led.start()
            self.field1 = 1
        else:
            self.count_control = True
            self.inst_led.stop()
            self.field1 = 0


#chanel_id = '746133'#
#api_key = 'F6G7Y748RPVAK8L9'

#inst_thingspeak = ThingSpeakRequests(api_key=api_key)
# inst_thingspeak.Bulk_Write_JSON_Data(chanel_id=chanel_id, values=[[1, 2, 3], [4, 5, 6]], created_at=[datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()])
#res = inst_thingspeak.write_data_json([1, 3], [0, 1], created_at=DEFAULT)
# res = inst_thingspeak.ReadData(chanel_id=chanel_id, results=50)
#res = inst_thingspeak.ReadField(chanel_id=chanel_id, field_id=1)
# res = inst_thingspeak.ReadStatus(chanel_id=chanel_id)

#print(res)
# ledVDD = 7
# led_inst = LedModule(ledVDD)
# led_inst.config()
# led_inst.blink(0.1, 3)
#
# micVDD = 11
# micIN = 13
# mic_inst = MicModule(micVDD, micIN, url, api_key)
# mic_inst.config()
# mic_inst.start()
# mic_inst.set_event_detector(led_inst)

# while True:
#     time.sleep(0.1)