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
                  ['clas', 'classification'],
                  ['clsy', 'classification_system'],
                  ['code', 'codewords'],
                  ['ctlh', 'control_and_handling'],
                  ['rel', 'release_instructions'],
                  ['dctp', 'declassification_type'],
                  ['dcdt', 'declassification_date'],
                  ['dcxm', 'declassification_exemption'],
                  ['dg', 'downgrade'],
                  ['dgdt', 'downgrade_date'],
                  ['cltx', 'classification_text'],
                  ['catp', 'classification_authority_type'],
                  ['caut', 'classification_authority'],
                  ['crsn', 'classification_reason'],
                  ['srdt', 'security_source_date'],
                  ['ctln', 'security_control_number'],
                  ['cop', 'copy_number'],
                  ['cpys', 'number_of_copies']]:
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
                  ['clas', 'classification'],
                  ['clsy', 'classification_system'],
                  ['code', 'codewords'],
                  ['ctlh', 'control_and_handling'],
                  ['rel', 'release_instructions'],
                  ['dctp', 'declassification_type'],
                  ['dcdt', 'declassification_date'],
                  ['dcxm', 'declassification_exemption'],
                  ['dg', 'downgrade'],
                  ['dgdt', 'downgrade_date'],
                  ['cltx', 'classification_text'],
                  ['catp', 'classification_authority_type'],
                  ['caut', 'classification_authority'],
                  ['crsn', 'classification_reason'],
                  ['srdt', 'security_source_date'],
                  ['ctln', 'security_control_number'],
                  ['cop', 'copy_number'],
                  ['cpys', 'number_of_copies']]:
            if(hasattr(elem, prefix + field_name)):
                setattr(elem, prefix + field_name,
                        getattr(self, attribute_name))
        if(hasattr(elem, 'encryp')):
            elem.encryp = self.encryption

    def __str__(self):
        return f'''classification: {self.classification}
classification_system: {self.classification_system}
codewords: {self.codewords}
control_and_handling: {self.control_and_handling}
release_instructions: {self.release_instructions}
declassification_type: {self.declassification_type}
declassification_date: {self.declassification_date}
declassification_exemption: {self.declassification_exemption}
downgrade: {self.downgrade}
downgrade_date: {self.downgrade_date}
classification_text: {self.classification_text}
classification_authority_type: {self.classification_authority_type}
classification_authority: {self.classification_authority}
classification_reason: {self.classification_reason}
security_source_date: {self.security_source_date}
security_control_number: {self.security_control_number}
copy_number: {self.copy_number}
number_of_copies: {self.number_of_copies}
encryption: {self.encryption}
'''

    def __eq__(self, other):
        return (
            self.classification == other.classification and
            self.classification_system == other.classification_system and
            self.control_and_handling == other.control_and_handling and
            self.release_instructions == other.release_instructions and
            self.declassification_type == other.declassification_type and
            self.declassification_date == other.declassification_date and
            self.declassification_exemption == other.declassification_exemption and
            self.downgrade == other.downgrade and
            self.downgrade_date == other.downgrade_date and
            self.classification_text == other.classification_text and
            self.classification_authority_type == other.classification_authority_type and
            self.classification_authority == other.classification_authority and
            self.classification_reason == other.classification_reason and
            self.security_source_date == other.security_source_date and
            self.security_control_number == other.security_control_number and
            self.copy_number == other.copy_number and
            self.number_of_copies == other.number_of_copies 
            # Only some element with security support encryption, so don't fail
            # if this is different
            #and self.encryption == other.encryption
        )
        
    
    
security_unclassified = NitfSecurity()
__all__ = ["NitfSecurity", "security_unclassified"]
        
