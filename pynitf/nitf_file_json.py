from .nitf_file import NitfFile

# I don't think we actually want this to be a NitfFile.
#class NitfFileJson(NitfFile):
class NitfFileJson():
    '''This is a simple NITF file where we just save the data using jsonpickle
    (which must be on the system)'''
    def __init__(self, file_name = None):
        '''Create a NitfFileJson for reading or writing.'''
        self.file_header = None
        self._image_segment = None
        self.graphic_segment = None
        self.text_segment = None
        self.des_segment = None
        self.res_segment = None
        self.tre_list = None
        if(file_name is not None):
            self.read(file_name)
        self.base_file = None

    def notify_file_merge(self, file_list):
        cnt = 0
        for f in file_list:
            if not self is f:
                self.base_file = f
                cnt += 1
        if(cnt > 1):
            raise RuntimeError("We don't currently handle merging with more than one file. Could probably do this, but would need to work out the logic for this. Right now we treat this as an error.")

    @property
    def image_segment(self):
        #print("Pretending to replace")
        return self.base_file.image_segment
    
    def read(self, file_name):
        import jsonpickle
        (self.file_header,
         self._image_segment,
         self.graphic_segment,
         self.text_segment,
         self.des_segment,
         self.res_segment,
         self.tre_list) = jsonpickle.decode(open(file_name).read())
        # TODO - Do we want to process after_read_hook?
        
    def write(self, file_name):
        import jsonpickle
        jsonpickle.set_encoder_options('json', sort_keys=True, 
                                       indent=4, separators=(',', ': '))
        with open(file_name, "w") as fh:
            fh.write(jsonpickle.encode((self.file_header,
                                        self._image_segment,
                                        self.graphic_segment,
                                        self.text_segment,
                                        self.des_segment,
                                        self.res_segment,
                                        self.tre_list)))
            
__all__ = ["NitfFileJson", ]

        
        
        
    
