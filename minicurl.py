import re
import pycurl
import sys
from io import BytesIO

# ref: https://github.com/pycurl/pycurl/blob/master/examples/quickstart/response_headers.py

class MiniCurl:
    # parameters
    url = None
    method = None  # TODO use this
    verbose_flag = False
    show_header_flag = False
    hide_result_flag = False

    # middle
    response_encoding = None
    response_headers = None

    # results
    bytes = None
    text = None

    def set_url(self, url):
        self.url = url

    def set_verbose(self, flag=True):
        self.verbose_flag = flag

    def set_show_header(self, flag=True):
        self.show_header_flag = flag

    def set_hide_result(self, flag=True):
        self.hide_result_flag = flag

    def verbose_print(self, *args, **kwargs):
        if self.verbose_flag:
            print(args, kwargs)

    def __header_function(self, header_line):

        header_line = header_line.decode('iso-8859-1')

        if ':' not in header_line:
            return

        name, value = header_line.split(':', 1)

        name = name.strip()
        value = value.strip()

        if self.show_header_flag:
            print('header >> {}: {}'.format(name, value))

        name = name.lower()

        self.response_headers[name] = value

    def __parse_response_headers(self):
        self.response_encoding = None

        if 'content-type' in self.response_headers:
            content_type = self.response_headers['content-type'].lower()
            match = re.search('charset=(\\S+)', content_type)
            if match:
                self.response_encoding = match.group(1)
                self.verbose_print('Decoding using %s' % self.response_encoding)

        if self.response_encoding is None:
            self.response_encoding = 'iso-8859-1'
            self.verbose_print('Assuming encoding is %s' % self.response_encoding)

    def launch(self):
        buffer = BytesIO()

        self.response_headers = {}

        pc = pycurl.Curl()
        pc.setopt(pc.URL, self.url)
        pc.setopt(pc.WRITEFUNCTION, buffer.write)
        pc.setopt(pc.HEADERFUNCTION, self.__header_function)
        pc.perform()
        pc.close()

        self.__parse_response_headers()

        self.bytes = buffer.getvalue()
        self.text = self.bytes.decode(self.response_encoding)

        print('content-bytes: {}'.format(len(self.bytes)))

        if not self.hide_result_flag:
            print(self.text)

        return buffer.getvalue()

    def set_method(self, method):
        self.method = method

def show_example():
    print('python minicurl <web-url> [-X POST] [--hide-result] [--show-header]')
    print('ex) python minicurl.py www.google.com -X POST --hide-result --show-header')

def main(args):
    """
    @type args: list[str]
    """
    if len(args) == 1:
        args = tuple(args[0].split(' '))

    try:
        if (len(args) == 0):
            raise Exception("empty arguments")

        mc = MiniCurl()

        arg_iter = iter(args)

        for arg in arg_iter:
            """
            :type str
            """
            if arg.startswith('--hide-result'):
                mc.set_hide_result()
            elif arg.startswith('--show-header'):
                mc.set_show_header()
            elif arg.startswith('-v'):
                mc.set_verbose()
            elif arg.startswith('-X'):
                value = next(arg_iter).lower()
                mc.set_method(value)
            elif not arg.startswith('-'):
                mc.set_url(arg)

            mc.launch()
    except Exception as e:
        print('error occurred: ' + str(e))
        show_example()

if __name__ == "__main__":
    main(sys.argv[1:])

