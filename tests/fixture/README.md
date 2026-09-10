# joern-mcp test fixture (tiny APK)

A **minimal, offline, reproducible Android APK** used to exercise the joern-mcp
toolchain (call-chain expansion, indexed method lookup, code retrieval) without
loading a 150-300 MB production APK.

The Java sources are written so that every construct that has previously tripped
the tooling is present exactly once, with a stable name to assert on.

Layout:

```
tests/fixture/
├── AndroidManifest.xml              # 3 receivers, one permission-gated
├── app/src/com/example/fixture/     # the crafted sources
├── build_fixture.sh                 # the build (no Gradle, raw SDK tools)
└── out/                             # build output (fixture.apk / fixture.cpg)
```

## Prerequisites

| Need | Verified on this machine |
|---|---|
| JDK 17+ (`javac`, `keytool`) | `javac 21.0.12` |
| Android SDK **build-tools** (`aapt2`, `d8`, `zipalign`, `apksigner`) | `$HOME/Android/Sdk/build-tools/36.1.0` |
| Android platform **android.jar** | `$HOME/Android/Sdk/platforms/android-36/android.jar` (API 36, SDK extension level 17) |
| `zip` (optional - falls back to python3) | `/usr/bin/zip` |
| joern CLI, only for `--cpg` | `$HOME/workspace/joern/joern-cli/target/universal/stage` |
| debug keystore | `$HOME/.android/debug.keystore` (alias `androiddebugkey`, pass `android`) |

If the keystore is missing:

```bash
keytool -genkeypair -v -keystore ~/.android/debug.keystore -storepass android \
        -keypass android -alias androiddebugkey -keyalg RSA -keysize 2048 \
        -validity 10000 -dname 'CN=Android Debug,O=Android,C=US'
```

## Build

```bash
cd tests/fixture
./build_fixture.sh                    # -> out/fixture.apk
./build_fixture.sh --cpg              # -> out/fixture.apk + out/fixture.cpg
```

**SDK level / extension level.** The build targets **API 36 with SDK extension level 17**, which is
what the `android-36` platform package provides (`AndroidVersion.ExtensionLevel=17`) and what a device
reporting `build.version.extensions.b == 17` supports. Both values are declared in
`AndroidManifest.xml`, so the APK carries the requirement itself:

```xml
<uses-sdk android:minSdkVersion="31" android:targetSdkVersion="36">
    <extension-sdk android:sdkVersion="36" android:minExtensionVersion="17" />
</uses-sdk>
```

To build for a different extension level, point `--platform` at that package and raise
`minExtensionVersion` to match: `android-36-ext19` (19), `android-36.1` (API 36.1, ext 20),
`android-37.0` (37.0, ext 22).

Overrides: `--platform <dir>`, `--build-tools <dir>`, or the environment variables
`ANDROID_HOME`, `FIXTURE_PLATFORM`, `FIXTURE_BUILD_TOOLS`, `FIXTURE_KEYSTORE`,
`JOERN_STAGE`.

### What the script does (and why this way)

Gradle is deliberately avoided: it needs the network, a daemon and a full project
skeleton. The raw chain below is what actually produces the APK, in order:

1. **`javac`** - `-source 8 -target 8 -bootclasspath android.jar`. Source/target 8
   keeps the bytecode on the Android floor; android.jar as bootclasspath means the
   code links against real Android APIs, not the JDK's.
2. **`d8`** - `--lib android.jar --min-api 21` compiles the `.class` files to
   `classes.dex` (and desugars).
3. **`aapt2 link`** - turns the manifest into a binary APK shell (no resources in
   this fixture, so this is a single call).
4. **add `classes.dex`** - `aapt2 link` only packs the manifest; the dex has to be
   added to the archive (works from any directory, it lands at the archive root).
5. **`zipalign -f -p 4`** - required before signing.
6. **`apksigner sign`** - with the standard debug key. Signing is not strictly
   required by Soot/jimple2cpg, but a signed APK is a realistic artefact and can be
   installed on a device for spot checks.
7. **(optional) `joern-parse`** - see below.

### Generating the CPG

```bash
$HOME/workspace/joern/joern-cli/target/universal/stage/joern-parse \
    --language java -J-Xmx4G \
    -o out/fixture.cpg out/fixture.apk \
    --frontend-args --android $HOME/Android/Sdk/platforms/android-36/android.jar
```

Notes that cost real debugging time:

- `--language java` is the **bytecode frontend (jimple2cpg)** and reads APK/JAR/class
  files directly. `--language javasrc` is the Java *source* frontend - do not mix them up.
- This build's jimple2cpg flag is **`--android <path-to-android.jar>`**; the widely
  documented `--android-jars <dir>` does not exist here. Without it Soot aborts with
  *"You are analyzing an Android application but did not define android.jar"*.

## Test-case map

| # | Construct | Where | What it exercises |
|---|---|---|---|
| 1 | entry point is `handleBroadCastReceive()`, not `onReceive()` (base receiver dispatches) | `SafeReceiverBase` / `AccountReceiver.handleBroadCastReceive` | indexed lookup must find the non-standard entry; reading only `onReceive` bodies yields an empty shell |
| 2 | 4-hop delegation: `handleBroadCastReceive -> HdMemberManager.call -> Callback.onAccountQuit (MemberCallback) -> StateWriter.updateBySilent` | `AccountReceiver`, `HdMemberManager`, `MemberCallback`, `StateWriter` | one-shot chain expansion across classes and through an interface |
| 2b | anonymous inner class (`SilentInstallReceiver$1`) | `SilentInstallReceiver` | `$1`-style classes survive the chain/lookup |
| 3 | identical simple name `refresh()` in three classes | `AccountReceiver.refresh`, `CacheManager.refresh`, `HdMemberManager.refresh` | `nameExact` must return several hits (picker ambiguity) |
| 4 | business write at the chain end: `SharedPreferences.putInt("hd_member", state)` | `StateWriter.updateBySilent` | the chain must surface the write (assert on `hd_member`) |
| 5 | framework/JDK calls interleaved in the chain (`Log.d`, `List.size/get`, `SharedPreferences.edit/putInt/apply`) | throughout | the chain tool must skip JDK/framework callees |
| 6 | method that does not exist | (test-side only) | error path must return an explicit `ERROR: ...`, never a silent empty result |
| 7 | permission-gated receiver (signature permission in the manifest) | `GatedReceiver` + `AndroidManifest.xml` | receiver/permission triage in the audit pipeline |

Expected size: APK ~15-25 KB, CPG a few MB (a 6 MB APK produces ~65 MB, so this
fixture stays tiny).

`out/` is a build artefact directory and should stay untracked.

## Gotchas

- **Load CPGs through the server's own `load_cpg` tool, not the REPL's bare
  `importCpg(...)`.** The Scala helpers read the script-level `cpg` variable; a bare
  `importCpg` only rebinds the console's, so every helper silently returns an empty
  string while plain `cpg.…` queries keep working. Symptom: `cpg.method.nameExact("refresh")`
  returns 3 hits but `get_methods_by_name("refresh")` returns `""`.
- `--target-sdk-version 36` in the build script is deliberate even though android.jar
  comes from `android-36.1`; raise it only when 36.1-only runtime APIs are needed.
- The APK is signed with the standard debug keystore; signing is not required by
  Soot/jimple2cpg, it just keeps the artefact installable for spot checks.
