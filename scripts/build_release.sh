#!/usr/bin/env bash
# Build the signalhub Docker image and produce a compressed tarball for offline distribution.
# Usage: bash scripts/build_release.sh [tag]
set -euo pipefail

TAG="${1:-latest}"
IMAGE="signalhub:${TAG}"
DATE=$(date +%Y%m%d)
OUT_DIR="dist"
OUT_FILE="${OUT_DIR}/signalhub-${TAG}-${DATE}.tar.gz"

mkdir -p "${OUT_DIR}"

echo "==> building ${IMAGE}"
docker build -t "${IMAGE}" .

echo "==> saving -> ${OUT_FILE}"
docker save "${IMAGE}" | gzip -9 > "${OUT_FILE}"

echo
echo "done: ${OUT_FILE} ($(du -h "${OUT_FILE}" | cut -f1))"
echo "load on a target host: docker load < ${OUT_FILE##*/}"
