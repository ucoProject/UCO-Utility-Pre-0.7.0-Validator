# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
Toolkit V4_to-V5 main program

Invocation:
    v4_to_v5 [-o output_jsonld_v5] input_jsonld_v4
'''
import argparse
import re
import sys

# Substitutions
# If you see the first string, substitute the second
substitutions = [
 ('https://unifiedcyberontology.org/ontology/uco/investigation',
  'https://caseontology.org/ontology/case/investigation'),
 ('https://unifiedcyberontology.org/ontology/uco/investigation-da',
  'https://caseontology.org/ontology/case/investigation-da'),
 ('uco-vocabulary:InvestigationFormVocab',
  'case-vocabulary:InvestigationFormVocab'),
 ('CyberItem', 'ObservableObject'),
 ('observable:CyberAction', 'observable:ObservableAction'),
 ('observable:CyberObservablePattern', 'observable:ObservablePattern'),
 ('observable:CyberRelationship', 'observable:ObservableRelationship'),
 ('core:facets', 'core:hasFacet'),
]



# Insertion
# If you match this pattern, insert the next string before this line
insertions = [
 (re.compile('"uco-vocabulary": *"https://unifiedcyberontology.org/ontology/uco/vocabulary#"'),
             '"case-vocabulary": "https://caseontology.org/ontology/case/vocabulary#"')
]

# New "Facets" in these
# If you see this string, but not this string with Facet appended,
# replace this string with this string with Facet appended
# These are ordered in reverse alphabetical to avoid errors like adding "Facet" to a class name twice.
facets = [
  ('observable:X509V3Extensions', 'observable:X509V3ExtensionsFacet'),
  ('observable:X509Certificate', 'observable:X509CertificateFacet'),
  ('observable:WirelessNetworkConnection', 'observable:WirelessNetworkConnectionFacet'),
  ('observable:WindowsVolume', 'observable:WindowsVolumeFacet'),
  ('observable:WindowsThread', 'observable:WindowsThreadFacet'),
  ('observable:WindowsTask', 'observable:WindowsTaskFacet'),
  ('observable:WindowsService', 'observable:WindowsServiceFacet'),
  ('observable:WindowsRegistryKey', 'observable:WindowsRegistryKeyFacet'),
  ('observable:WindowsRegistryHive', 'observable:WindowsRegistryHiveFacet'),
  ('observable:WindowsProcess', 'observable:WindowsProcessFacet'),
  ('observable:WindowsPrefetch', 'observable:WindowsPrefetchFacet'),
  ('observable:WindowsPEBinaryFile', 'observable:WindowsPEBinaryFileFacet'),
  ('observable:WindowsComputerSpecification', 'observable:WindowsComputerSpecificationFacet'),
  ('observable:WindowsActiveDirectoryAccount', 'observable:WindowsActiveDirectoryAccountFacet'),
  ('observable:WindowsAccount', 'observable:WindowsAccountFacet'),
  ('observable:WifiAddress', 'observable:WifiAddressFacet'),
  ('observable:WhoIs', 'observable:WhoIsFacet'),
  ('observable:Volume', 'observable:VolumeFacet'),
  ('observable:ValuesEnumeratedEffect', 'observable:ValuesEnumeratedEffectFacet'),
  ('observable:UserSession', 'observable:UserSessionFacet'),
  ('observable:UserAccount', 'observable:UserAccountFacet'),
  ('observable:URL', 'observable:URLFacet'),
  ('observable:UNIXVolume', 'observable:UNIXVolumeFacet'),
  ('observable:UNIXProcess', 'observable:UNIXProcessFacet'),
  ('observable:UNIXFilePermissions', 'observable:UNIXFilePermissionsFacet'),
  ('observable:UNIXAccount', 'observable:UNIXAccountFacet'),
  ('observable:TCPConnection', 'observable:TCPConnectionFacet'),
  ('observable:SymbolicLink', 'observable:SymbolicLinkFacet'),
  ('observable:StateChangeEffect', 'observable:StateChangeEffectFacet'),
  ('observable:SQLiteBlob', 'observable:SQLiteBlobFacet'),
  ('observable:Software', 'observable:SoftwareFacet'),
  ('observable:SMSMessage', 'observable:SMSMessageFacet'),
  ('observable:SIMCard', 'observable:SIMCardFacet'),
  ('observable:SendControlCodeEffect', 'observable:SendControlCodeEffectFacet'),
  ('observable:RasterPicture', 'observable:RasterPictureFacet'),
  ('observable:PropertyReadEffect', 'observable:PropertyReadEffectFacet'),
  ('observable:PropertiesEnumeratedEffect', 'observable:PropertiesEnumeratedEffectFacet'),
  ('observable:Process', 'observable:ProcessFacet'),
  ('observable:PhoneCall', 'observable:PhoneCallFacet'),
  ('observable:PhoneAccount', 'observable:PhoneAccountFacet'),
  ('observable:PDFFile', 'observable:PDFFileFacet'),
  ('observable:PathRelation', 'observable:PathRelationFacet'),
  ('observable:OperatingSystem', 'observable:OperatingSystemFacet'),
  ('observable:NTFSFileSystem', 'observable:NTFSFileSystemFacet'),
  ('observable:NTFSFilePermissions', 'observable:NTFSFilePermissionsFacet'),
  ('observable:Note', 'observable:NoteFacet'),
  ('observable:NetworkInterface', 'observable:NetworkInterfaceFacet'),
  ('observable:NetworkFlow', 'observable:NetworkFlowFacet'),
  ('observable:NetworkConnection', 'observable:NetworkConnectionFacet'),
  ('observable:Mutex', 'observable:MutexFacet'),
  ('observable:MobileDevice', 'observable:MobileDeviceFacet'),
  ('observable:MobileAccount', 'observable:MobileAccountFacet'),
  ('observable:MftRecord', 'observable:MftRecordFacet'),
  ('observable:MessageThread', 'observable:MessageThreadFacet'),
  ('observable:Message', 'observable:MessageFacet'),
  ('observable:Memory', 'observable:MemoryFacet'),
  ('observable:MACAddress', 'observable:MACAddressFacet'),
  ('observable:Library', 'observable:LibraryFacet'),
  ('observable:IPv6Address', 'observable:IPv6AddressFacet'),
  ('observable:IPv4Address', 'observable:IPv4AddressFacet'),
  ('observable:Image', 'observable:ImageFacet'),
  ('observable:ICMPConnection', 'observable:ICMPConnectionFacet'),
  ('observable:HTTPConnection', 'observable:HTTPConnectionFacet'),
  ('observable:GeoLocationTrack', 'observable:GeoLocationTrackFacet'),
  ('observable:GeoLocationLog', 'observable:GeoLocationLogFacet'),
  ('observable:GeoLocationEntry', 'observable:GeoLocationEntryFacet'),
  ('observable:Fragment', 'observable:FragmentFacet'),
  ('observable:FileSystem', 'observable:FileSystemFacet'),
  ('observable:FilePermissions', 'observable:FilePermissionsFacet'),
  ('observable:File', 'observable:FileFacet'),
  ('observable:ExtractedStrings', 'observable:ExtractedStringsFacet'),
  ('observable:ExtInode', 'observable:ExtInodeFacet'),
  ('observable:EXIF', 'observable:EXIFFacet'),
  ('observable:Event', 'observable:EventFacet'),
  ('observable:EncryptedStream', 'observable:EncryptedStreamFacet'),
  ('observable:EncodedStream', 'observable:EncodedStreamFacet'),
  ('observable:EmailMessage', 'observable:EmailMessageFacet'),
  ('observable:EmailAddress', 'observable:EmailAddressFacet'),
  ('observable:EmailAccount', 'observable:EmailAccountFacet'),
  ('observable:DomainName', 'observable:DomainNameFacet'),
  ('observable:DiskPartition', 'observable:DiskPartitionFacet'),
  ('observable:Disk', 'observable:DiskFacet'),
  ('observable:DigitalSignatureInfo', 'observable:DigitalSignatureInfoFacet'),
  ('observable:DigitalAccount', 'observable:DigitalAccountFacet'),
  ('observable:Device', 'observable:DeviceFacet'),
  ('observable:DataRange', 'observable:DataRangeFacet'),
  ('observable:ContentData', 'observable:ContentDataFacet'),
  ('observable:Contact', 'observable:ContactFacet'),
  ('observable:ComputerSpecification', 'observable:ComputerSpecificationFacet'),
  ('observable:CompressedStream', 'observable:CompressedStreamFacet'),
  ('observable:CalendarEntry', 'observable:CalendarEntryFacet'),
  ('observable:Calendar', 'observable:CalendarFacet'),
  ('observable:BrowserCookie', 'observable:BrowserCookieFacet'),
  ('observable:BrowserBookmark', 'observable:BrowserBookmarkFacet'),
  ('observable:BluetoothAddress', 'observable:BluetoothAddressFacet'),
  ('observable:AutonomousSystem', 'observable:AutonomousSystemFacet'),
  ('observable:Audio', 'observable:AudioFacet'),
  ('observable:Attachment', 'observable:AttachmentFacet'),
  ('observable:ArchiveFile', 'observable:ArchiveFileFacet'),
  ('observable:ApplicationAccount', 'observable:ApplicationAccountFacet'),
  ('observable:Application', 'observable:ApplicationFacet'),
  ('observable:AccountAuthentication', 'observable:AccountAuthenticationFacet'),
  ('observable:Account', 'observable:AccountFacet'),
]


def parse_args(args):
    '''
    Arguments:
        args   argument list, usually sys.argv[1:]

    Return:
        Namespace with these attributes:
            input_filepath   Full path to input (version 4) file
            output_filepath  Full path to output (version 5) file
    '''
    parser = argparse.ArgumentParser(
        prog='v4_to_v5',
        description='Convert version 4 jsonld to version 5.')

    # Optional output_file
    parser.add_argument(
        '-o',
        type=str,
        required=False,
        default=None,
        action='store',
        dest='output_filepath',
        help='Full path to output (version 5) jsonld file [default: STDOUT]')

    # REQUIRED POSITIONAL ARGUMENT: input_file
    parser.add_argument(
        type=str,
        dest='input_filepath',
        help='Full path to input (version 4) jsonld file')

    # Parse and return namespace
    return parser.parse_args(args)




def main():
    '''
    Command line invocation:
        python v4-to-v5.py [-o output_filepath] input_filepath
    '''
    # Start with empty error messages
    error_messages = set()

    # Parse command line
    args = parse_args(sys.argv[1:])

    # Do the conversion
    outfile = None
    try:

        # Open output file, if any
        if args.output_filepath:
            outfile = open(args.output_filepath, 'w')
        else:
            outfile = None

        # Do for each line of input:
        for line in open(args.input_filepath).readlines():
            line = line.rstrip()

            # Do insertions
            for matcher, replacement in insertions:
                if matcher.search(line):
                    extra_line = re.sub(matcher.pattern, replacement, line)
                    if not extra_line.endswith(','):
                        extra_line += ','
                    print(extra_line, file=outfile)

            # Do substitutions
            for old, new in substitutions:
                line = re.sub(old, new, line)

            # Do facet appends
            for old, new in facets:
                if old in line and 'Facet' not in line:
                    line = re.sub(old, new, line)

            # Write the line
            print(line, file=outfile)   # if outfile is None, this prints to stdout


    # Always clean up
    finally:
        if outfile:
            outfile.close()

    # Write error messages, if any, to stderr
    if error_messages:
        print('\n\n', file=sys.stderr)
    for errmsg in error_messages:
        print(errmsg, file=sys.stderr)


main()
