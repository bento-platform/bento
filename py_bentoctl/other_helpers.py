import os
import pathlib
import shutil
import sys
import json
import subprocess
import uuid
import docker
import docker.errors

from termcolor import cprint
from datetime import datetime, timezone

from . import config as c
from .services import BENTO_USER_EXCLUDED_SERVICES
from .openssl import create_cert, create_private_key
from .utils import info, task_print, task_print_done, warn, err

__all__ = [
    "init_web",
    "init_docker",
    "init_dirs",
    "init_self_signed_certs",
    "init_config",
]


def init_web(service: str, force: bool):
    if service not in ("public", "private"):
        err("You must specify the service type (public or private)")
        exit(1)

    if service == "public":
        _init_web_public(force)
    else:  # private
        _init_web_private(force)


def _init_web_public(force: bool):
    root_path = pathlib.Path.cwd()
    etc_path = root_path / "etc"

    # Init lib dir
    public_path = (root_path / "lib" / "public")
    translation_path = (public_path / "translations")
    translation_path.mkdir(parents=True, exist_ok=True)

    # About html page (English)
    _file_copy(
        (etc_path / "default.en_about.html"),
        (public_path / "en_about.html"),
        force=force,
    )

    # About html page (French)
    _file_copy(
        (etc_path / "default.fr_about.html"),
        (public_path / "fr_about.html"),
        force=force,
    )

    # Branding image
    # - dark background / default
    _file_copy(
        (etc_path / "default.branding.png"),
        (public_path / "branding.png"),
        force=force,
    )
    # - light background
    _file_copy(
        (etc_path / "default.branding.lightbg.png"),
        (public_path / "branding.lightbg.png"),
        force=force,
    )

    # - favicon
    _file_copy(
        (etc_path / "default.favicon.png"),
        (public_path / "favicon.png"),
        force=force,
    )

    # English translations
    _file_copy(
        (etc_path / "templates" / "translations" / "en.example.json"),
        (translation_path / "en.json"),
        force=force,
    )
    # French translations
    _file_copy(
        (etc_path / "templates" / "translations" / "fr.example.json"),
        (translation_path / "fr.json"),
        force=force,
    )


def _file_copy(src_path: pathlib.Path, dst_path: pathlib.Path, force: bool = False):
    task_print(f"Copying {src_path} to {dst_path}...")

    if dst_path.is_file():
        if not force:
            warn("destination exists, skipping copy.")
            return

        cprint("destination exists, overwriting... ", "yellow", file=sys.stderr, end="")

    shutil.copyfile(src_path, dst_path)
    task_print_done()


def _init_web_private(force: bool):
    task_print("Init public web folder with branding image...")

    root_path = pathlib.Path.cwd()
    web_path = (root_path / "lib" / "web")
    web_path.mkdir(parents=True, exist_ok=True)

    src_branding = (root_path / "etc" / "default.branding.darkbg.png")
    dst_branding = (web_path / "branding.png")

    if dst_branding.is_file():
        if not force:
            warn(f"file {dst_branding} exists, skipping copy.")
            return

        cprint(f"file {dst_branding} exists, overwriting... ", "yellow", file=sys.stderr, end="")

    shutil.copyfile(src=src_branding, dst=dst_branding)
    task_print_done()


def init_self_signed_certs(force: bool):
    certs_dir = pathlib.Path(os.environ["BENTOV2_CERTS_DIR"])
    auth_certs_dir = (certs_dir / "auth")
    gateway_certs_dir = (certs_dir / "gateway")

    cert_domains_vars = {
        "public": {
            "var": "BENTOV2_DOMAIN",
            "priv_key_name": "privkey1.key",
            "crt": "fullchain1.crt",
            "dir": gateway_certs_dir,
        },
        "portal": {
            "var": "BENTOV2_PORTAL_DOMAIN",
            "priv_key_name": "portal_privkey1.key",
            "crt": "portal_fullchain1.crt",
            "dir": gateway_certs_dir,
        },
        "auth": {
            "var": "BENTOV2_AUTH_DOMAIN",
            "priv_key_name": "auth_privkey1.key",
            "crt": "auth_fullchain1.crt",
            "dir": auth_certs_dir,
        },

        # MinIO
        **({"minio": {
            "var": "BENTO_MINIO_DOMAIN",
            "priv_key_name": "minio_privkey1.key",
            "crt": "minio_fullchain1.crt",
            "dir": gateway_certs_dir,
        }} if c.BENTO_FEATURE_MINIO.enabled else {}),

        # If cBioPortal is enabled, generate a cBioPortal self-signed certificate as well
        **({"cbioportal": {
            "var": "BENTOV2_CBIOPORTAL_DOMAIN",
            "priv_key_name": "cbioportal_privkey1.key",
            "crt": "cbioportal_fullchain1.crt",
            "dir": gateway_certs_dir,
        }} if c.BENTO_FEATURE_CBIOPORTAL.enabled else {}),

        # If a domain is configured for redirect (e.g. preserve a published reference)
        **({"redirect": {
            "var": "BENTO_DOMAIN_REDIRECT",
            "priv_key_name": "redirect_privkey1.key",
            "crt": "redirect_fullchain1.crt",
            "dir": gateway_certs_dir,
        }} if c.BENTO_FEATURE_REDIRECT.enabled else {}),
    }

    # Init cert directories

    task_print("Creating certs directories if needed...")
    auth_certs_dir.mkdir(parents=True, exist_ok=True)
    gateway_certs_dir.mkdir(parents=True, exist_ok=True)
    task_print_done()

    # Check for existing cert files first
    cert_files = [
        *auth_certs_dir.glob('*.crt'),
        *auth_certs_dir.glob('*.key'),
        *auth_certs_dir.glob("*.pem"),
        *gateway_certs_dir.glob('*.crt'),
        *gateway_certs_dir.glob('*.key'),
        *gateway_certs_dir.glob("*.pem"),
    ]
    if not force and any(cert_files):
        warn("WARNING: Cert files detected in the target directory, new cert creation skipped.")
        warn("To create new certs, remove all \".crt\" and \".key\" files in target directory first.")
        for f in cert_files:
            warn(f"Cert file path: {f}")
        return

    for domain in cert_domains_vars.keys():
        domain_var, priv_key_name, crt_name, crt_pk_dir = cert_domains_vars[domain].values()
        domain_val = os.getenv(domain_var)

        if domain_val is None:
            err(f"error: {domain_var} env variable ({domain}) is not set")
            exit(1)

        #  Create private key for domain
        task_print(f"Creating .key file for domain: {domain} -> {domain_val} ...")
        pkey = create_private_key(crt_pk_dir, priv_key_name)
        task_print_done()

        # Create signed cert for domain
        task_print(f"Creating certificate file for domain: {domain} -> {domain_val} ...")
        create_cert(crt_pk_dir, pkey, crt_name, domain_val)
        task_print_done()


def init_dirs():
    data_dir_vars = {
        "root_fast": "BENTO_FAST_DATA_DIR",
        "root_slow": "BENTO_SLOW_DATA_DIR",
        "authz-db": "BENTO_AUTHZ_DB_VOL_DIR",
        "drs-data": "BENTO_DRS_DATA_VOL_DIR",
        "drs-tmp": "BENTO_DRS_TMP_VOL_DIR",
        "drop-box": "BENTOV2_DROP_BOX_VOL_DIR",
        "gohan": "BENTOV2_GOHAN_DATA_ROOT",
        "gohan-elasticsearch": "BENTOV2_GOHAN_ES_DATA_DIR",
        "gohan-api-drs-bridge": "BENTOV2_GOHAN_API_DRS_BRIDGE_HOST_DIR",
        "gohan-vcfs": "BENTOV2_GOHAN_API_VCF_PATH",
        "gohan-gtfs": "BENTOV2_GOHAN_API_GTF_PATH",
        "katsu-db": "BENTOV2_KATSU_DB_PROD_VOL_DIR" if c.DEV_MODE else "BENTOV2_KATSU_DB_DEV_VOL_DIR",
        "notification": "BENTOV2_NOTIFICATION_VOL_DIR",
        "redis": "BENTOV2_REDIS_VOL_DIR",
        "reference": "BENTO_REFERENCE_TMP_VOL_DIR",
        "reference-db": "BENTO_REFERENCE_DB_VOL_DIR",
        "wes": "BENTOV2_WES_VOL_DIR",
        "wes-tmp": "BENTOV2_WES_VOL_TMP_DIR",

        # Feature-specific volume dirs - only if the relevant feature is enabled.
        #  - internal IdP
        **({"auth": "BENTOV2_AUTH_VOL_DIR"} if not c.BENTOV2_USE_EXTERNAL_IDP else {}),
        #  - cBioPortal
        **({"cbioportal": "BENTO_CBIOPORTAL_STUDY_DIR"} if c.BENTO_FEATURE_CBIOPORTAL.enabled else {}),
        #  - MinIO
        **({"minio": "BENTO_MINIO_DATA_DIR"} if c.BENTO_FEATURE_MINIO.enabled else {}),
        #  - Monitoring: Grafana/Loki
        **({"grafana": "BENTO_GRAFANA_LIB_DIR"} if c.BENTO_FEATURE_MONITORING else {}),
        **({"loki": "BENTO_LOKI_TEMP_DIR"} if c.BENTO_FEATURE_MONITORING else {}),
    }

    # Some of these don't use the Bento user inside their containers, so ignore if need be
    ignore_permissions_for = set(BENTO_USER_EXCLUDED_SERVICES)

    task_print("Creating temporary secrets directory if needed...")
    secrets_dir = pathlib.Path.cwd() / "tmp" / "secrets"
    secrets_dir_exists = secrets_dir.exists()
    secrets_dir.mkdir(parents=True, exist_ok=True)
    task_print_done(msg="already exists." if secrets_dir_exists else "done.")

    print("Creating data directories if needed... this may ask you for your password to set permissions.")
    for dir_for, dir_var in data_dir_vars.items():
        task_print(f"  {dir_for}")

        data_dir = os.getenv(dir_var)
        if data_dir is None:
            err(f"error: {dir_for} data directory environment variable '{dir_var}' is not set")
            exit(1)

        data_dir_path = pathlib.Path(data_dir)
        already_exists = data_dir_path.exists()

        if already_exists and dir_for not in ignore_permissions_for and \
                (data_dir_owner := data_dir_path.owner()) != c.BENTO_USERNAME:
            err(f"error: data directory {data_dir_path} exists, but is owned by {data_dir_owner} instead of "
                f"{c.BENTO_USERNAME}. please fix this!")
            exit(1)

        data_dir_path.mkdir(parents=True, exist_ok=True)
        task_print_done(msg="already exists." if already_exists else "done.")


def init_docker(client: docker.DockerClient):
    # Init swarm
    #
    # try:
    #     task_print("Initializing Docker Swarm, if necessary...")
    #     swarm_id = client.swarm.init()
    #     task_print_done()
    #     info(f"Swarm ID: {swarm_id}")
    # except docker.errors.APIError as e:
    #     warn(" error encountered, skipping.")  # continues on the task_print line
    #     warn(f"    Likely due to Docker already being in Swarm mode ({e})")

    # Init Docker network(s)

    # network environment variable, kwargs
    networks = (
        ("BENTO_AGGREGATION_NETWORK", dict(driver="bridge")),
        ("BENTO_AUTH_NETWORK", dict(driver="bridge")),
        ("BENTO_AUTH_DB_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_AUTHZ_NETWORK", dict(driver="bridge")),
        ("BENTO_AUTHZ_DB_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_BEACON_NETWORK", dict(driver="bridge")),
        ("BENTO_CBIOPORTAL_NETWORK", dict(driver="bridge")),
        ("BENTO_CBIOPORTAL_DATABASE_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_CBIOPORTAL_SESSION_NETWORK", dict(driver="bridge")),
        ("BENTO_DROP_BOX_NETWORK", dict(driver="bridge")),
        ("BENTO_DRS_NETWORK", dict(driver="bridge")),
        ("BENTO_EVENT_RELAY_NETWORK", dict(driver="bridge")),
        ("BENTO_GOHAN_API_NETWORK", dict(driver="bridge")),
        ("BENTO_GOHAN_ES_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_KATSU_NETWORK", dict(driver="bridge")),
        ("BENTO_KATSU_DB_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_MINIO_NETWORK", dict(driver="bridge")),
        ("BENTO_MONITORING_NETWORK", dict(driver="bridge")),
        ("BENTO_NOTIFICATION_NETWORK", dict(driver="bridge")),
        ("BENTO_PUBLIC_NETWORK", dict(driver="bridge")),
        ("BENTO_REDIS_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_REFERENCE_NETWORK", dict(driver="bridge")),
        ("BENTO_REFERENCE_DB_NETWORK", dict(driver="bridge", internal=True)),  # Does not need to access the web
        ("BENTO_SERVICE_REGISTRY_NETWORK", dict(driver="bridge")),
        ("BENTO_WEB_NETWORK", dict(driver="bridge")),
        ("BENTO_WES_NETWORK", dict(driver="bridge")),
    )

    for net_var, net_kwargs in networks:
        task_print(f"Creating Docker network (var: {net_var}) if needed...")

        net_name = os.getenv(net_var)
        if not net_name:
            cprint(f"failed ({net_var} not set).", "red")

        try:
            client.networks.get(net_name)
            task_print_done(f"exists already (name: {net_name}).", color="blue")
        except docker.errors.NotFound:
            client.networks.create(net_name, **net_kwargs)
            task_print_done(f"network created (name: {net_name}).")


EXTRA_PROPERTIES_KEY = "extra_properties"
EXTRA_PROPERTIES_ELEMENTS = [
    "subject",
    "biosamples",
    "diseases",
    "phenotypic_features",
    EXTRA_PROPERTIES_KEY,  # phenopacket.extra_properties
]


def stash_element_extra_properties(phenopacket: dict, element_name: str, stash: dict):
    element = phenopacket.get(element_name, {})
    if type(element) is list:
        # Stash with indexes if phenopacket[element_name] is a list
        for idx, item in enumerate(element):
            # Align with item index if no "id" in the element item
            item_id = item.get("id", idx)
            if extra_properties := item.pop(EXTRA_PROPERTIES_KEY, None):
                stash[element_name][item_id] = extra_properties

    elif extra_properties := element.pop(EXTRA_PROPERTIES_KEY, None):
        # Stash object if phenopacket[element_name] is not empty
        stash[element_name] = extra_properties
    elif element_name == EXTRA_PROPERTIES_KEY and element:
        # Stash object if phenopacket.extra_properties
        stash[element_name] = phenopacket.pop(EXTRA_PROPERTIES_KEY)


def apply_element_extra_properties(phenopacket: dict, element_name: str, stash: dict):
    element_stash = stash.get(element_name)
    if not element_stash:
        # Exit if no stash to apply
        return

    if element_name == EXTRA_PROPERTIES_KEY:
        # Early exit for non-nested phenopacket.extra_properties
        phenopacket[EXTRA_PROPERTIES_KEY] = element_stash
        return

    # Continue for phenopacket[element_name].extra_properties
    element = phenopacket.get(element_name)

    if element_stash and not element:
        error_msg = f"Stash exists for element_name {element_name} but key is not in phenopacket {phenopacket['id']}"
        raise ValueError(error_msg)

    if type(element) is list:
        for idx, item in enumerate(element):
            if "id" in item and item["id"] in element_stash:
                item[EXTRA_PROPERTIES_KEY] = element_stash[item["id"]]
            elif idx in element_stash:
                item[EXTRA_PROPERTIES_KEY] = element_stash[idx]

    else:
        element[EXTRA_PROPERTIES_KEY] = element_stash


def stash_phenopacket_extra_properties(phenopacket: dict):
    stash = {}
    for element_name in EXTRA_PROPERTIES_ELEMENTS:
        stash[element_name] = {}
        stash_element_extra_properties(phenopacket, element_name, stash)
    return stash


def apply_extra_properties(phenopacket: dict, stash: dict):
    for element_name in EXTRA_PROPERTIES_ELEMENTS:
        apply_element_extra_properties(phenopacket, element_name, stash)
    return phenopacket


def format_biosample_variants(biosample: dict):
    if "variants" not in biosample:
        return biosample

    formated_variants = []
    for variant in biosample.get("variants", []):
        if (allele := variant.pop("allele", None)) and (allele_type := variant.pop("allele_type", None)):
            formated_variants.append({
                allele_type: allele
            })
    biosample["variants"] = formated_variants
    return biosample


SUBJECT_MCODE_FIELDS = ["comorbid_condition", "ecog_performance_status", "karnofsky", "race", "ethnicity"]


def format_subject_mcode(subject: dict):
    extra_properties = subject.get("extra_properties", {})
    for mcode_field in SUBJECT_MCODE_FIELDS:
        if value := subject.pop(mcode_field, None):
            extra_properties[mcode_field] = value
    if extra_properties:
        subject["extra_properties"] = extra_properties
    return subject


def format_phenov1(phenopacket: dict):
    # SUBJECT
    subject: dict = phenopacket["subject"]

    # subject.date_of_birth ISO8601 formating
    # dob = subject["date_of_birth"]
    if dob := subject.get("date_of_birth", None):
        iso_dob = datetime.fromisoformat(dob).astimezone(timezone.utc).isoformat()
        phenopacket["subject"]["date_of_birth"] = iso_dob

    # subject.age
    age = subject.pop("age", None)
    if age:
        subject["age_at_collection"] = age

    # subject MCode fields are moved to extra_properties
    subject = format_subject_mcode(subject)

    phenopacket["subject"] = subject

    # BIOSAMPLES
    biosamples = phenopacket.get("biosamples", [])
    for sample in biosamples:
        sample = format_biosample_variants(sample)
        if age_at_collection := sample.pop("individual_age_at_collection", None):
            sample["age_of_individual_at_collection"] = age_at_collection

    # DISEASES
    diseases = phenopacket.get("diseases", [])
    for disease in diseases:
        if onset := disease.pop("onset", None):
            disease["age_of_onset"] = onset

    phenopacket["subject"] = subject
    phenopacket["biosamples"] = biosamples
    phenopacket["diseases"] = diseases
    return phenopacket


def remove_null_none_empty(obj: dict):
    clean_obj = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            clean_v = remove_null_none_empty(v)
            if len(clean_v.keys()) > 0:
                clean_obj[k] = clean_v

        elif isinstance(v, list):
            clean_list = []
            for item in v:
                if isinstance(item, dict):
                    clean_item = remove_null_none_empty(item)
                    if len(clean_item.keys()) > 0:
                        clean_list.append(clean_item)
                elif item is not None and item != '':
                    clean_list.append(item)
            clean_obj[k] = clean_list
        elif v is not None and v != '':
            clean_obj[k] = v
    return clean_obj


def _convert_phenopacket(phenopacket: dict, idx: int | None = None):
    """
    Runs the equivalent of 'cat some_file.json | pxf convert -f json -e phenopacket'
    Phenopacket-tools docs: http://phenopackets.org/phenopacket-tools/stable/cli.html#commands
    """
    import humps

    # Put all keys in snake_case for concistency
    phenopacket = humps.decamelize(phenopacket)

    # Preprocessing
    formated_pheno = format_phenov1(phenopacket)

    # Stash extra_properties before conversion
    stashed_extra_properties = stash_phenopacket_extra_properties(formated_pheno)

    pxf_cmd = ("java", "-jar", c.PHENOTOOL_PATH, "convert", "-f", "json", "-e", "phenopacket")
    # Pipe pheno_pipe.stdout as stdin of async convert command
    conversion_process = subprocess.Popen(pxf_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    stdout, stderr = conversion_process.communicate(input=json.dumps(formated_pheno))
    if conversion_process.returncode != 0:
        # Conversion encountered an error
        raise ValueError(
            (stderr if stderr else "") +
            f"\nOn phenopacket element {idx} of array document."
            if idx is not None else "",
        )

    # Load converted output
    converted = json.loads(stdout)

    # Post conversion decamelize, phenotool may put keys in camelCase, which can break extra_properties
    converted = humps.decamelize(converted)

    # Apply stashed extra_properties
    apply_extra_properties(converted, stashed_extra_properties)

    # Katsu only accepts "2.0"
    converted["meta_data"]["phenopacket_schema_version"] = "2.0"

    # remove empty/none keys
    converted = remove_null_none_empty(converted)

    # Create a phenopacket ID if none
    if "id" not in converted:
        converted["id"] = str(uuid.uuid4())

    return converted


def convert_phenopacket_file(source: str, target: str):
    from tqdm import tqdm

    if c.PHENOTOOL_PATH == "":
        # Abort if phenotool path is not available
        err("A Phenopacket-tools jar path is required to use this command.")

    # Read source file
    source_path = pathlib.Path.cwd() / source
    with open(source_path, 'r') as source_file:
        pheno_v1 = json.load(source_file)

    try:
        if isinstance(pheno_v1, list):
            # Phenopacket-tools can only handle single JSON objects
            info(f"Converting Phenopackets V1 array document to V2: {source}")
            converted = [
                _convert_phenopacket(phenopacket, idx)
                for idx, phenopacket in tqdm(enumerate(pheno_v1), total=len(pheno_v1))
            ]
        else:
            info(f"Converting Phenopacket V1 object document: {source}")
            converted = _convert_phenopacket(pheno_v1)
    except ValueError as e:
        # Display error and abort
        err(str(e))
        exit(1)

    if target:
        target_path = pathlib.Path.cwd() / target
    else:
        target_file_name = source_path.name.split(".json")[0] + "_pheno_v2.json"
        target_path = source_path.parent / target_file_name

    with open(target_path, 'w') as output_file:
        json.dump(converted, output_file)

    task_print_done(f"Phenopacket V2 conversion done: {source} -> {target_path}")

    return converted

# def init_secrets(force: bool):
#     client = docker.from_env()
#     katsu_vars = {
#         "user": {
#             "env_var": "BENTOV2_KATSU_DB_USER",
#             "secret_name": "metadata-db-user"
#         },
#         "pw": {
#             "env_var": "BENTOV2_KATSU_DB_PASSWORD",
#             "secret_name": "metadata-db-secret"
#         },
#         "secret": {
#             "env_var": "BENTOV2_KATSU_DB_APP_SECRET",
#             "secret_name": "metadata-app-secret"
#         }
#     }
#
#     for secret_type in katsu_vars.keys():
#         env_var, secret_name = katsu_vars[secret_type].values()
#         val = os.getenv(env_var)
#         val_bytes = bytes(val, "UTF-8")
#         path = (pathlib.Path.cwd() / "tmp" / "secrets" / secret_name)
#
#         task_print(f"Creating secret for {secret_type}: {secret_name} ...")
#
#         existing_secrets = [scrt for scrt in client.secrets.list(filters={"name": secret_name}) if scrt is not None]
#
#         if not existing_secrets:
#             with open(path, "wb") as f:
#                 f.write(val_bytes)
#             client.secrets.create(name=secret_name, data=val_bytes)
#             task_print_done()
#
#         elif force:
#             for scrt in existing_secrets:
#                 client.api.remove_secret(scrt.id)
#             with open(path, "wb") as f:
#                 f.write(val_bytes)
#             client.secrets.create(name=secret_name, data=val_bytes)
#             task_print_done()
#
#         else:
#             warn(f"  {secret_name} already exists, skipping.")
#
#     # TODO: Use Hashicorp/Vault for more secure secret mgmt?
#
#
# def clean_secrets():
#     client = docker.from_env()
#     for secret in client.secrets.list():
#         task_print(f"Removing secret: {secret.id} ...")
#         success = client.api.remove_secret(secret.id)
#         if success:
#             task_print_done()
#         else:
#             err("failed.")


def init_config(service: str, force: bool = False):
    if service == "katsu":
        _init_katsu_config(force)
    elif service == "beacon":
        _init_beacon_config(force)
    elif service == "beacon-network":
        _init_beacon_network_config(force)


def _init_beacon_config(force: bool):
    root_path = pathlib.Path.cwd()
    template_dir = (root_path / "etc" / "templates" / "beacon")
    dest_dir = pathlib.Path(os.environ["BENTO_BEACON_CONFIG_DIR"])

    config_template_path = (template_dir / "beacon_config.example.json")
    config_dest_path = (dest_dir / "beacon_config.json")

    cohort_template_path = (template_dir / "beacon_cohort.example.json")
    cohort_dest_path = (dest_dir / "beacon_cohort.json")

    _file_copy(config_template_path, config_dest_path, force)
    _file_copy(cohort_template_path, cohort_dest_path, force)


def _init_beacon_network_config(force: bool):
    root_path = pathlib.Path.cwd()
    template_dir = (root_path / "etc" / "templates" / "beacon")
    dest_dir = pathlib.Path(os.environ["BENTO_BEACON_CONFIG_DIR"])

    network_config_template_path = (template_dir / "beacon_network_config.example.json")
    network_config_dest_path = (dest_dir / "beacon_network_config.json")

    _file_copy(network_config_template_path, network_config_dest_path, force)


def _init_katsu_config(force: bool):
    root_path = pathlib.Path.cwd()
    katsu_config_template_path = (root_path / "etc" / "katsu.config.example.json")
    katsu_config_dest_path = (root_path / "lib" / "katsu" / "config.json")

    _file_copy(katsu_config_template_path, katsu_config_dest_path, force)


def clean_logs():
    # TODO
    pass
