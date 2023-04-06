We have a sample TRE that is based on xml, as part the ILLUMA TRE.

The schema for this is avaibable in the NITF TRE documentation 
(STDI-0002-1 Appendix AL: ILLUM v1.0).

We've stored this in the file "illuma.xsd", which is just a cut and pase from the appendix.
It imports another standard used for security markings. This is available at
https://www.dni.gov/index.php/who-we-are/organizations/ic-cio/ic-cio-related-menus/ic-cio-related-links/ic-technical-specifications/information-security-marking-metadata

We've copied this data here, just so we can use pynitf without needing web access.

Note that the ILLUMA xml is actually pretty simple, using the full schema definition is
really over kill. But this is useful as an example for working with XML in NITF.
