import datetime
import os
import pathlib
import glob
from termcolor import cprint
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def _create_cert(path: pathlib.Path, pkey: rsa.RSAPrivateKey, crt_name: str, common_name: str):
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"CA"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Quebec"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Montreal"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"C3G McGill"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"{}".format(common_name))
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        pkey.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False
    ).sign(pkey, hashes.SHA256())

    cert_path = (path / crt_name)
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def _create_private_key(path: pathlib.Path, pkey_name: str):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    pkey_path = (path / pkey_name)
    with open((pkey_path), "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    return key
