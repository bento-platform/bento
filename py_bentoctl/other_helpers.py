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

def init_web():
    # TODO
    pass


def init_public():
    # TODO
    pass


def init_self_signed_certs(force: bool):
    cert_domains_vars = {
        "public": {
            "var": "BENTOV2_DOMAIN",
            "priv_key_name": "privkey1.key",
            "crt": "fullchain1.crt"
        },
        "portal": {
            "var": "BENTOV2_PORTAL_DOMAIN",
            "priv_key_name": "portal_privkey1.key",
            "crt": "portal_fullchain1.crt"
        },
        "auth": {
            "var": "BENTOV2_AUTH_DOMAIN",
            "priv_key_name": "auth_privkey1.key",
            "crt": "auth_fullchain1.crt"
        }
    }

    # Init cert directory in gateway
    certs_dir = (pathlib.Path.cwd() / "certs")
    print("Creating certs directory if needed... ", end="")
    certs_dir.mkdir(parents=True, exist_ok=True)
    cprint("done.", "green")

    # Check for existing cert files first
    cert_files = list(certs_dir.glob('*.crt')) + list(certs_dir.glob('*.key')) + list(certs_dir.glob("*.pem"))
    if not force and any(cert_files):
        cprint("WARNING: Cert files detected in the target directory, new cert creation skipped.", "yellow")
        cprint("To create new certs, remove all \".crt\" and \".key\" files in target directory first.", "yellow")
        for f in cert_files:
            cprint("Cert file path: {}".format(f), "yellow")
        return
    
    for domain in cert_domains_vars.keys():
        domain_var, priv_key_name, crt_name = cert_domains_vars[domain].values()
        domain_val = os.getenv(domain_var)

        #  Create private key for domain
        print("Creating .key file for domain: {} -> {} ... ".format(domain, domain_val), end="")
        pkey = create_private_key(certs_dir, priv_key_name)
        cprint("done.", "green")

        # Create signed cert for domain 
        print("Creating certificate file for domain: {} -> {} ... ".format(domain, domain_val), end="")
        create_cert(certs_dir, pkey, crt_name, domain_val)
        cprint("done.", "green")

def create_cert(path: pathlib.Path, pkey: rsa.RSAPrivateKey, crt_name: str, common_name: str):
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
    

def create_private_key(path: pathlib.Path, pkey_name: str):

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    pkey_path = (path / pkey_name)
    with open((pkey_path), "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
        ))
    return key

def clean_self_signed_certs():
    pass

def init_dirs():
    data_dir_vars = {
        "root": "BENTOV2_ROOT_DATA_DIR",

        "auth": "BENTOV2_AUTH_VOL_DIR",
        "drop-box": "BENTOV2_DROP_BOX_VOL_DIR",
        "katsu-db": "BENTOV2_KATSU_DB_PROD_VOL_DIR",
        "notification": "BENTOV2_NOTIFICATION_VOL_DIR",
        "redis": "BENTOV2_REDIS_VOL_DIR",
        "wes": "BENTOV2_WES_VOL_DIR",
    }

    print("Creating temporary secrets directory if needed... ", end="")
    (pathlib.Path.cwd() / "tmp" / "secrets").mkdir(parents=True, exist_ok=True)
    cprint("done.", "green")

    print("Creating data directories...")
    for dir_for, dir_var in data_dir_vars.items():
        print(f"  {dir_for} ", end="")

        data_dir = os.getenv(dir_var)
        if data_dir is None:
            cprint(f"error: {dir_for} data directory ({dir_var}) is not set", "red")
            exit(1)

        pathlib.Path(os.getenv(dir_var)).mkdir(parents=True, exist_ok=True)
        cprint("done.", "green")


def init_docker():
    # TODO: docker swarm (ignore / suppress error)

    # TODO: create network(s) if needed
    pass


def init_secrets():
    # TODO
    pass


def clean_secrets():
    # TODO
    pass


def clean_logs():
    # TODO
    pass
