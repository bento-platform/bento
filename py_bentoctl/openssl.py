import datetime
import pathlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def _create_cert(path: pathlib.Path, pkey: rsa.RSAPrivateKey, crt_name: str, common_name: str) -> None:
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"CA"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Quebec"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Montreal"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"C3G McGill"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"{common_name}")
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(pkey.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), critical=False)
        .sign(pkey, hashes.SHA256())
    )

    with open(path / crt_name, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def _create_private_key(path: pathlib.Path, pkey_name: str) -> rsa.RSAPrivateKey:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with open(path / pkey_name, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    return key
