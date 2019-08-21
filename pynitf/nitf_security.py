class NitfSecurity(object):
    '''There are a number of NITF elements that have security/classification
    information. This single class allows a common interface for these items
    to be set, collected, read and written. The individual elements will have
    functions to set/read these values, so for example NitfFile has the 
    "security" property to read and write this and the file level.
    '''
    def __init__(self):
        self.classification = "U"
        self.classification_system = ""
        self.codewords = ""
        self.control_and_handling = ""
        self.release_instructions = ""
        self.declassification_type = ""
        self.declassification_date = ""
        self.declassification_exemption = ""
        self.downgrade = ""
        self.downgrade_date = ""
        self.classification_text = ""
        self.classification_authority_type = ""
        self.classification_authority = ""
        self.classification_reason = ""
        self.security_source_date = ""
        self.security_control_number = ""
        self.copy_number = 0
        self.number_of_copies = 0
        self.encryption = 0

    def get_security(elem, prefix):
        '''Create a NitfSecurity that goes with the given NITF element
        (e.g., a NitfFileHeader). There are a small number of fields that
        aren't in every NITF element (e.g., File Copy Number) - if these
        values are found in this particular NITF element we set them to 
        a default value of 0.  The prefix is the name prefix for the 
        NITF element fields (e.g., "f" for NitfFileHeader).'''
        res = NitfSecurity()
        for field_name, attribute_name in [
                  ['sclas', 'classification'],
                  ['sclsy', 'classification_system'],
                  ['scode', 'codewords'],
                  ['sctlh', 'control_and_handling'],
                  ['srel', 'release_instructions'],
                  ['sdctp', 'declassification_type'],
                  ['sdcdt', 'declassification_date'],
                  ['sdcxm', 'declassification_exemption'],
                  ['sdg', 'downgrade'],
                  ['sdgdt', 'downgrade_date'],
                  ['scltx', 'classification_text'],
                  ['scatp', 'classification_authority_type'],
                  ['scaut', 'classification_authority'],
                  ['scrsn', 'classification_reason'],
                  ['ssrdt', 'security_source_date'],
                  ['sctln', 'security_control_number'],
                  ['scop', 'copy_number'],
                  ['scpys', 'number_of_copies']]:
            if(hasattr(elem, prefix + field_name)):
                setattr(res, attribute_name, getattr(elem, prefix + field_name))
        if(hasattr(elem, 'encryp')):
            res.encryption = elem.encryp
        return res

    def set_security(self, elem, prefix):
        '''Set security fields in NITF element (e.g., a NitfFileHeader).  The
        prefix is the name prefix for the NITF element fields (e.g.,
        "f" for NitfFileHeader).
        '''
        for field_name, attribute_name in [
                  ['sclas', 'classification'],
                  ['sclsy', 'classification_system'],
                  ['scode', 'codewords'],
                  ['sctlh', 'control_and_handling'],
                  ['srel', 'release_instructions'],
                  ['sdctp', 'declassification_type'],
                  ['sdcdt', 'declassification_date'],
                  ['sdcxm', 'declassification_exemption'],
                  ['sdg', 'downgrade'],
                  ['sdgdt', 'downgrade_date'],
                  ['scltx', 'classification_text'],
                  ['scatp', 'classification_authority_type'],
                  ['scaut', 'classification_authority'],
                  ['scrsn', 'classification_reason'],
                  ['ssrdt', 'security_source_date'],
                  ['sctln', 'security_control_number'],
                  ['scop', 'copy_number'],
                  ['scpys', 'number_of_copies']]:
            if(hasattr(elem, prefix + field_name)):
                setattr(elem, prefix + field_name,
                        getattr(self, attribute_name))
        if(hasattr(elem, 'encryp')):
            elem.encryp = self.encryption

security_unclassified = NitfSecurity()
__all__ = ["NitfSecurity", "security_unclassified"]
        
