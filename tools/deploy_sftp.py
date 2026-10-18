#!/usr/bin/env python3
"""Upload EXO RP FiveM resources over verified SFTP.

Writes only files under resources/[local] and the EXO-managed block of server.cfg.
Never delete unrelated server data. Never print secrets.
"""
import base64
import hashlib
import hmac
import os
import posixpath
import re
import stat
from pathlib import Path

import paramiko


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_RESOURCES = REPO_ROOT / "resources" / "[local]"
BEGIN = "# BEGIN EXO-RP GITHUB MANAGED"
END = "# END EXO-RP GITHUB MANAGED"


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing GitHub Actions secret: {name}")
    return value


def main() -> None:
    host = required("SFTP_HOST")
    username = required("SFTP_USERNAME")
    password = required("SFTP_PASSWORD")
    expected_key = required("SFTP_HOST_FINGERPRINT")
    port = int(required("SFTP_PORT"))
    if not expected_key.startswith("SHA256:"):
        raise RuntimeError("SFTP_HOST_FINGERPRINT must begin with SHA256:")
    remote_root = os.getenv("SFTP_REMOTE_ROOT", "").strip() or "."
    if not LOCAL_RESOURCES.is_dir():
        raise RuntimeError("No resources/[local] folder found.")

    resources = sorted(
        p for p in LOCAL_RESOURCES.iterdir()
        if p.is_dir() and not p.is_symlink() and (p / "fxmanifest.lua").is_file()
    )
    if not resources:
        raise RuntimeError("No valid resources found (fxmanifest.lua required).")
    for folder in resources:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", folder.name):
            raise RuntimeError(f"Unsafe resource name: {folder.name}")
    print(f"Uploading {len(resources)} own resources to Gaming4Free.")

    transport = paramiko.Transport((host, port))
    try:
        # Verify server identity BEFORE sending the password.
        transport.start_client(timeout=25)
        key = transport.get_remote_server_key()
        actual_key = "SHA256:" + base64.b64encode(
            hashlib.sha256(key.asbytes()).digest()
        ).decode("ascii").rstrip("=")
        if not hmac.compare_digest(actual_key, expected_key):
            raise RuntimeError(
                "SFTP server fingerprint mismatch. Check the verified host key."
            )
        transport.auth_password(username=username, password=password)
        if not transport.is_authenticated():
            raise RuntimeError("SFTP login failed.")
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            def remote_path(relative: str) -> str:
                return posixpath.join(remote_root, relative)

            def mkdirs(path: str) -> None:
                if path in ("", ".", "/"):
                    return
                try:
                    attributes = sftp.stat(path)
                    if not stat.S_ISDIR(attributes.st_mode):
                        raise RuntimeError(f"Remote path is not a directory: {path}")
                    return
                except FileNotFoundError:
                    pass
                parent = posixpath.dirname(path.rstrip("/"))
                if parent and parent != path:
                    mkdirs(parent)
                sftp.mkdir(path)

            # Upload only files belonging to our own FiveM resources.
            for folder in resources:
                for local in sorted(folder.rglob("*")):
                    if local.is_symlink():
                        raise RuntimeError(f"Symlink not allowed: {local}")
                    relative = local.relative_to(REPO_ROOT).as_posix()
                    destination = remote_path(relative)
                    if local.is_dir():
                        mkdirs(destination)
                    elif local.is_file():
                        mkdirs(posixpath.dirname(destination))
                        sftp.put(str(local), destination)
                print(f"Uploaded resource: {folder.name}")

            # Keep other configuration intact; add only the managed ensure block.
            config_path = remote_path("server.cfg")
            with sftp.open(config_path, "rb") as file:
                original_bytes = file.read()
            original = original_bytes.decode("utf-8")
            block = BEGIN + "\n" + "\n".join(
                f"ensure {folder.name}" for folder in resources
            ) + "\n" + END
            if BEGIN in original or END in original:
                if original.count(BEGIN) != 1 or original.count(END) != 1:
                    raise RuntimeError("Invalid managed section in server.cfg; stopping.")
                begin_idx = original.index(BEGIN)
                end_idx = original.index(END) + len(END)
                if begin_idx > end_idx:
                    raise RuntimeError("Invalid managed section order.")
                updated = original[:begin_idx] + block + original[end_idx:]
            else:
                updated = original.rstrip("\n") + "\n\n" + block + "\n"
            if updated != original:
                backup_path = remote_path("server.cfg.bak.before-exo-deploy")
                try:
                    sftp.stat(backup_path)
                except FileNotFoundError:
                    with sftp.open(backup_path, "wb") as backup:
                        backup.write(original_bytes)
                with sftp.open(config_path, "wb") as config:
                    config.write(updated.encode("utf-8"))
                print("Updated EXO managed section in server.cfg (backup kept).")
            print("SFTP upload completed. Restart server to load new resources.")
        finally:
            sftp.close()
    finally:
        transport.close()


if __name__ == "__main__":
    main()
