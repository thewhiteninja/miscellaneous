# dslib imports

# local imports
from general_types import *


class Extension(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('extnID', univ.ObjectIdentifier()),
        namedtype.DefaultedNamedType('critical', univ.Boolean('False')),
        namedtype.NamedType('extnValue', univ.OctetString())
        # namedtype.NamedType('extnValue', ExtensionValue())
    )


class Extensions(univ.SequenceOf):
    componentType = Extension()
    sizeSpec = univ.SequenceOf.sizeSpec


class SubjectPublicKeyInfo(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('algorithm', AlgorithmIdentifier()),
        namedtype.NamedType('subjectPublicKey', ConvertibleBitString())
    )


class UniqueIdentifier(ConvertibleBitString):
    pass


class Time(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('utcTime', useful.UTCTime()),
        namedtype.NamedType('generalTime', useful.GeneralizedTime())
    )

    def __str__(self):
        return str(self.getComponent())


class Validity(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('notBefore', Time()),
        namedtype.NamedType('notAfter', Time())
    )


class CertificateSerialNumber(univ.Integer):
    pass


class Version(univ.Integer):
    namedValues = namedval.NamedValues(
        ('v1', 0), ('v2', 1), ('v3', 2)
    )


class TBSCertificate(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.DefaultedNamedType('version', Version('v1', tagSet=Version.tagSet.tagExplicitly(
            tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0)))),
        namedtype.NamedType('serialNumber', CertificateSerialNumber()),
        namedtype.NamedType('signature', AlgorithmIdentifier()),
        namedtype.NamedType('issuer', Name()),
        namedtype.NamedType('validity', Validity()),
        namedtype.NamedType('subject', Name()),
        namedtype.NamedType('subjectPublicKeyInfo', SubjectPublicKeyInfo()),
        namedtype.OptionalNamedType('issuerUniqueID', UniqueIdentifier().subtype(
            implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 1))),
        namedtype.OptionalNamedType('subjectUniqueID', UniqueIdentifier().subtype(
            implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 2))),
        namedtype.OptionalNamedType('extensions', Extensions().subtype(
            explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3)))
    )


class Certificate(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('tbsCertificate', TBSCertificate()),
        namedtype.NamedType('signatureAlgorithm', AlgorithmIdentifier()),
        namedtype.NamedType('signatureValue', ConvertibleBitString())
    )


class Certificates(univ.SetOf):
    componentType = Certificate()
