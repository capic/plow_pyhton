class DownloadsList(list):

    def __init__(self, callback=None):
        list.__init__(self)
        self.callback = callback

    def set_callback(self, callback):
        self.callback = callback

    def set_values(self, values):
        print("######################################")
        super(DownloadsList, self).extend(values)

        if self.callback is not None:
            print("callback")
            self.callback()

    def __len__(self):
        return super(DownloadsList, self).__len__()

    def __iter__(self):
        return super(DownloadsList, self).__iter__()
