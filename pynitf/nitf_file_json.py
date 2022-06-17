from .nitf_file import NitfFile
from .nitf_segment import NitfSegment, NitfSharedHeader
import copy

class NitfSegmentJson(NitfSegment):
    '''NitfSegment where much of the content is stored as Json data.
    Used by NitfFileJson'''
    def __init__(self, nitf_file=None):
        self._shared_header = NitfSharedHeader(int, int)
        self._shared_header.subheader = None
        self._shared_header.user_subheader = None
        self.tre_list = []
        self._short_desc = None
        if(nitf_file is not None):
            self._nitf_file = weakref.ref(nitf_file)
        else:
            self._nitf_file = None
        self._segment_type = None
        self._data = None
        self._merge_seg = None
        self._primary_key = None

    def primary_key(self):
        return self._primary_key

    def notify_segment_merge(self, seg_list):
        # Don't need to worry about this if we are managing
        # the data in this class
        if(self._data):
            return
        slist = []
        if(self.primary_key() is not None):
            slist = [s for s in seg_list
                     if s.primary_key() == self.primary_key()]
        if(len(slist) != 1):
            raise RuntimeError("Couldn't uniquely match primary_key to seg_list")
        self._merge_seg = slist[0]

    @property
    def data(self):
        if(self._data):
            return self._data
        if(self._merge_seg):
            return self._merge_seg.data
        
    @classmethod
    def create_delta(cls, segin, include_data=False):
        s = cls()
        s.subheader = copy.deepcopy(segin.subheader)
        s.user_subheader = copy.deepcopy(segin.user_subheader)
        s.tre_list = copy.deepcopy(segin.tre_list)
        s._short_desc = segin.short_desc()
        s._segment_type = segin.segment_type()
        s._primary_key = segin.primary_key()
        if(include_data):
            s._data = copy.deepcopy(segin.data)
        else:
            s._data = None
        return s

    def short_desc(self):
        return self._short_desc

    def segment_type(self):
        return self._segment_type

    def __getstate__(self):
        return {"shared_header" : self._shared_header,
         "tre_list" : self.tre_list,
         "short_desc" : self.short_desc(),
         "segment_type" : self.segment_type(),
         "data" : self._data,
         "primary_key": self.primary_key()
         }
    def __setstate__(self, d):
        self._shared_header = d["shared_header"]
        self.tre_list = d["tre_list"]
        self._short_desc = d["short_desc"]
        self._segment_type = d["segment_type"]
        self._data = d["data"]
        self._primary_key = d["primary_key"]
                
    
# I don't think we actually want this to be a NitfFile.
#class NitfFileJson(NitfFile):
class NitfFileJson():
    '''This is a simple NITF file where we just save the data using jsonpickle
    (which must be on the system)'''
    def __init__(self, file_name = None):
        '''Create a NitfFileJson for reading or writing.'''
        self.file_header = None
        self.image_segment = None
        self.graphic_segment = None
        self.text_segment = None
        self.des_segment = None
        self.res_segment = None
        self.tre_list = None
        if(file_name is not None):
            self.read(file_name)
        self.base_file = None

    @classmethod
    def create_delta(cls, fin):
        f = cls()
        f.tre_list = copy.deepcopy(fin.tre_list)
        f.file_header = copy.deepcopy(fin.file_header)
        f.image_segment = []
        f.text_segment = []
        f.des_segment = []
        for iseg in fin.image_segment:
            f.image_segment.append(NitfSegmentJson.create_delta(iseg))
        for tseg in fin.text_segment:
            # TODO Do we need to play with the writing out of text data?
            # Is the JSON something that is easy to diff?
            f.text_segment.append(NitfSegmentJson.create_delta(tseg, include_data=True))
        for dseg in fin.des_segment:
            # Skip TRE_OVERFLOW, we already handle the TREs separately
            if(dseg.subheader.desid != "TRE_OVERFLOW"):
                # TODO Logic for when to copy the data
                f.des_segment.append(NitfSegmentJson.create_delta(dseg))
        return f
    
    def notify_file_merge(self, file_list):
        cnt = 0
        for f in file_list:
            if not self is f:
                self.base_file = f
                cnt += 1
        if(cnt > 1):
            raise RuntimeError("We don't currently handle merging with more than one file. Could probably do this, but would need to work out the logic for this. Right now we treat this as an error.")
        for seglist, base_seglist in (
                (self.image_segment, self.base_file.image_segment),
                (self.graphic_segment, self.base_file.graphic_segment),
                (self.text_segment, self.base_file.text_segment),
                (self.des_segment, self.base_file.des_segment),
                (self.res_segment, self.base_file.res_segment)):
            if(seglist is not None):
                for s in seglist:
                    s.notify_segment_merge(base_seglist)

    def read(self, file_name):
        import jsonpickle
        (self.file_header,
         self.image_segment,
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
                                        self.image_segment,
                                        self.graphic_segment,
                                        self.text_segment,
                                        self.des_segment,
                                        self.res_segment,
                                        self.tre_list)))
            
__all__ = ["NitfFileJson", ]

        
        
        
    
