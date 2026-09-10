#!/usr/bin/env bash
#
# build_fixture.sh - build the tiny Android fixture APK used by the joern-mcp tests.
#
# It deliberately drives the raw SDK tools (javac -> d8 -> aapt2 -> zip -> zipalign
# -> apksigner) instead of Gradle: no network, no Gradle daemon, fully reproducible,
# and it produces exactly the artefact that joern's jimple2cpg frontend consumes.
#
# The APK version (versionName/versionCode) is taken from ../pyproject.toml, so the
# fixture always reports the same version as the MCP server itself.
#
# Prerequisites
#   * JDK 17+ (javac, keytool)                      - verified with javac 21
#   * Android SDK build-tools: aapt2 d8 zipalign apksigner
#   * Android platform android.jar                  - default platforms/android-36 (API 36, ext 17)
#   * zip (falls back to python3's zipfile if absent)
#   * (optional) joern CLI for the --cpg step       - $JOERN_STAGE/joern-parse
#
# Usage
#   ./build_fixture.sh                                             # -> out/fixture.apk + ./fixture.apk
#   ./build_fixture.sh --cpg                                       # + fixture.cpg
#   ./build_fixture.sh --platform $SDK/platforms/android-36 \\
#                      --build-tools $SDK/build-tools/36.1.0
#
# Environment overrides
#   ANDROID_HOME        SDK root                 (default $HOME/Android/Sdk)
#   FIXTURE_PLATFORM    platform dir             (default $ANDROID_HOME/platforms/android-36)
#   FIXTURE_BUILD_TOOLS build-tools dir          (default $ANDROID_HOME/build-tools/36.1.0)
#   FIXTURE_KEYSTORE    signing keystore         (default $HOME/.android/debug.keystore)
#   JOERN_STAGE         joern stage dir          (default $HOME/workspace/joern/joern-cli/target/universal/stage)
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$HERE/out"

SDK="${ANDROID_HOME:-$HOME/Android/Sdk}"
PLATFORM="${FIXTURE_PLATFORM:-$SDK/platforms/android-36}"   # API 36 + SDK extension level 17
BUILD_TOOLS="${FIXTURE_BUILD_TOOLS:-$SDK/build-tools/36.1.0}"
KEYSTORE="${FIXTURE_KEYSTORE:-$HOME/.android/debug.keystore}"
JOERN_STAGE="${JOERN_STAGE:-$HOME/workspace/joern/joern-cli/target/universal/stage}"
MIN_API=31
DO_CPG=0

while [ $# -gt 0 ]; do
    case "$1" in
        --cpg)         DO_CPG=1 ;;
        --platform)    PLATFORM="$2"; shift ;;
        --build-tools) BUILD_TOOLS="$2"; shift ;;
        -h|--help)     sed -n '2,30p' "$0"; exit 0 ;;
        *)             echo "unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done

ANDROID_JAR="$PLATFORM/android.jar"
AAPT2="$BUILD_TOOLS/aapt2"
D8="$BUILD_TOOLS/d8"
ZIPALIGN="$BUILD_TOOLS/zipalign"
APKSIGNER="$BUILD_TOOLS/apksigner"

# --- version: one source of truth (the MCP package version) ---
PYPROJECT="$HERE/../../pyproject.toml"
VERSION_NAME="$(grep -m1 '^version' "$PYPROJECT" 2>/dev/null | cut -d'"' -f2 || true)"
VERSION_NAME="${VERSION_NAME:-0.0.0}"
VERSION_CODE="$(echo "$VERSION_NAME" | awk -F. '{printf "%d%02d%02d", $1, $2, $3}')"

log() { printf '\n=== %s ===\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

log "0/7 prerequisites"
for f in "$ANDROID_JAR" "$AAPT2" "$D8" "$ZIPALIGN" "$APKSIGNER"; do
    [ -e "$f" ] || die "missing: $f"
done
command -v javac >/dev/null || die "javac not found (install a JDK 17+)"
[ -f "$KEYSTORE" ] || die "debug keystore not found: $KEYSTORE
create one with:
  keytool -genkeypair -v -keystore $KEYSTORE -storepass android -keypass android \\
          -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 \\
          -dname 'CN=Android Debug,O=Android,C=US'"
echo "platform    : $PLATFORM"
echo "build-tools : $BUILD_TOOLS"
echo "android.jar : $ANDROID_JAR ($(stat -c %s "$ANDROID_JAR") bytes)"
echo "javac       : $(javac -version 2>&1)"
echo "version     : $VERSION_NAME (code $VERSION_CODE)"

rm -rf "$OUT"
mkdir -p "$OUT/classes" "$OUT/dex"

log "1/7 javac (source/target 8, bootclasspath = android.jar)"
find "$HERE/app/src" -name '*.java' | sort > "$OUT/sources.txt"
javac -encoding UTF-8 -source 8 -target 8 -Xlint:-options \
      -bootclasspath "$ANDROID_JAR" \
      -d "$OUT/classes" @"$OUT/sources.txt"

log "2/7 d8 -> classes.dex (min-api $MIN_API)"
# shellcheck disable=SC2046
"$D8" --lib "$ANDROID_JAR" --min-api "$MIN_API" --output "$OUT/dex" \
      $(find "$OUT/classes" -name '*.class' | sort)

log "3/7 aapt2 link -> base APK (manifest only, no resources)"
# minSdk/targetSdk and the required SDK extension level live in AndroidManifest.xml
# (<uses-sdk> + <extension-sdk>), so aapt2 must not inject them again.
"$AAPT2" link --manifest "$HERE/AndroidManifest.xml" -I "$ANDROID_JAR" \
       --version-code "$VERSION_CODE" --version-name "$VERSION_NAME" \
       -o "$OUT/base.apk"

log "4/7 add classes.dex to the APK"
if command -v zip >/dev/null 2>&1; then
    ( cd "$OUT/dex" && zip -q "$OUT/base.apk" classes.dex )
else
    python3 - "$OUT/base.apk" "$OUT/dex/classes.dex" <<'PY'
import sys, zipfile
apk, dex = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(apk, "a", zipfile.ZIP_STORED) as z:
    z.write(dex, "classes.dex")
PY
fi

log "5/7 zipalign"
"$ZIPALIGN" -f -p 4 "$OUT/base.apk" "$OUT/fixture-unsigned.apk"

log "6/7 apksigner (debug key)"
"$APKSIGNER" sign --ks "$KEYSTORE" --ks-pass pass:android --key-pass pass:android \
            --ks-key-alias androiddebugkey \
            --out "$OUT/fixture.apk" "$OUT/fixture-unsigned.apk"
"$APKSIGNER" verify --print-certs "$OUT/fixture.apk" | head -3

log "7/7 publish"
cp -f "$OUT/fixture.apk" "$HERE/fixture.apk"
unzip -l "$OUT/fixture.apk" | head -10
ls -la "$HERE/fixture.apk"

if [ "$DO_CPG" = "1" ]; then
    log "extra: joern-parse --language java -> fixture.cpg"
    [ -x "$JOERN_STAGE/joern-parse" ] || die "joern-parse not found at $JOERN_STAGE (set JOERN_STAGE)"
    "$JOERN_STAGE/joern-parse" --language java -J-Xmx4G \
        -o "$OUT/fixture.cpg" "$OUT/fixture.apk" \
        --frontend-args --android "$ANDROID_JAR"
    cp -f "$OUT/fixture.cpg" "$HERE/fixture.cpg"
    ls -la "$HERE/fixture.cpg"
fi

log "done"
echo "APK : $HERE/fixture.apk   (out/ keeps the intermediates)"
[ "$DO_CPG" = "1" ] && echo "CPG : $HERE/fixture.cpg"
exit 0
