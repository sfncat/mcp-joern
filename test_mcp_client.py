#!/usr/bin/env python3
"""Protocol-level test client for the joern MCP server.

Starts ``server.py`` (same directory) over stdio and exercises the MCP tools against
the bundled **fixture CPG** (``tests/fixture/fixture.cpg``, built by
``tests/fixture/build_fixture.sh``), asserting the results. Prints a PASS/FAIL line per
check and exits non-zero if any check fails, so it works as a regression gate.

Usage
-----
    uv run test_mcp_client.py                          # fixture cpg + ./server.py
    uv run test_mcp_client.py --cpg other.cpg          # any other CPG
    python  test_mcp_client.py --server ../server.py    # explicit server path

The fixture carries one instance of every construct that has bitten the tooling:
a custom base receiver whose business entry is ``handleBroadCastReceive()`` (not
``onReceive``), a 4-hop delegation chain across classes and an interface, a duplicated
simple method name, an anonymous inner class, a SharedPreferences write (``hd_member``)
at the end of the chain, framework calls to be skipped, and a permission-gated receiver.
"""
import argparse
import asyncio
import os
import re
import sys

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SERVER = os.path.join(HERE, "server.py")
DEFAULT_CPG = os.path.join(HERE, "tests", "fixture", "fixture.cpg")

# fixture anchors
CLS = "com.example.fixture.AccountReceiver"
BASE = "com.example.fixture.SafeReceiverBase"
ENTRY = CLS + ".handleBroadCastReceive:void(android.content.Context,android.content.Intent)"
INNER = "com.example.fixture.SilentInstallReceiver$1"

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print("%s  %s%s" % ("PASS " if ok else "FAIL ", name, ("   " + str(detail)) if detail else ""))


def text_of(res):
    """Tolerant extraction: fastmcp >=2 returns a CallToolResult with .content,
    older versions return a list of TextContent."""
    if res is None:
        return ""
    content = getattr(res, "content", None)
    if content is None and isinstance(res, (list, tuple)):
        content = res
    if content is None:
        return str(res)
    return "\n".join(getattr(c, "text", None) or getattr(c, "content", None) or str(c)
                     for c in content)


async def main() -> int:
    ap = argparse.ArgumentParser(description="joern MCP protocol test client")
    ap.add_argument("--server", default=DEFAULT_SERVER, help="path to server.py")
    ap.add_argument("--cpg", default=DEFAULT_CPG, help="CPG to load (default: fixture)")
    args = ap.parse_args()

    if not os.path.exists(args.cpg):
        print("ERROR: CPG not found: %s\n       build it with tests/fixture/build_fixture.sh --cpg"
              % args.cpg)
        return 2
    if not os.path.exists(args.server):
        print("ERROR: server not found: %s" % args.server)
        return 2

    transport = PythonStdioTransport(
        args.server,
        env=os.environ.copy(),                    # fastmcp does not inherit env by itself
        cwd=os.path.dirname(os.path.abspath(args.server)),
        python_cmd=sys.executable,
    )

    print("Testing MCP server %s" % args.server)
    print("Using CPG %s" % args.cpg)
    print("=" * 72)

    async with Client(transport) as client:
        tools = {t.name for t in await client.list_tools()}
        print("tools available (%d): %s\n" % (len(tools), ", ".join(sorted(tools))))

        async def call(tool, payload):
            try:
                return text_of(await client.call_tool(tool, payload))
            except Exception as exc:              # surface tool errors as text
                return "ERROR: %s" % exc

        # ---------------------------------------------------------------- basics
        r = await call("check_connection", {})
        check("[check_connection] server connection", "connected" in r.lower(), r[:70].strip())

        r = await call("ping", {})
        check("[ping] server responsive", bool(r.strip()) and "ERROR" not in r, r[:70].strip())

        check("[tool surface] chain helper exposed", "get_callee_chain_server" in tools)
        check("[tool surface] indexed lookup exposed", "get_methods_by_name" in tools)

        r = await call("load_cpg", {"cpg_filepath": args.cpg})
        check("[load_cpg] fixture CPG loaded", "true" in r.lower(), r[:70].strip())

        # ------------------------------------------------- indexed lookup (new tool)
        r = await call("get_methods_by_name", {"method_name": "handleBroadCastReceive"})
        check("[get_methods_by_name] non-standard entry found",
              CLS + ".handleBroadCastReceive" in r, r[:120].replace("\n", " "))

        r = await call("get_methods_by_name", {"method_name": "refresh"})
        hits = set(re.findall(r"com\.example\.fixture\.[\w$]+\.refresh:void\(\)", r))
        check("[get_methods_by_name] duplicated simple name -> 3 classes", len(hits) >= 3,
              "%d distinct classes" % len(hits))

        # ------------------------------------------------- legacy callee/caller tools
        r = await call("get_method_callees", {"method_full_name": ENTRY})
        check("[get_method_callees] first hop resolved", "HdMemberManager.call" in r,
              r[:100].replace("\n", " "))

        r = await call("get_method_callers", {"method_full_name": ENTRY})
        check("[get_method_callers] caller is the base-class onReceive shell",
              "SafeReceiverBase.onReceive" in r, r[:110].replace("\n", " "))

        # ------------------------------------------------- chain helper (new tool)
        r = await call("get_callee_chain_server",
                       {"method_full_name": ENTRY, "depth": 6, "limit": 40})
        check("[get_callee_chain_server] reaches the chain end",
              "StateWriter.updateBySilent" in r, "%d chars" % len(r))
        check("[get_callee_chain_server] surfaces the business write",
              "hd_member" in r)

        # ------------------------------------------------- class level queries
        r = await call("get_class_methods_by_class_full_name", {"class_full_name": CLS})
        check("[get_class_methods] entry + duplicated name present",
              "handleBroadCastReceive" in r and "refresh" in r, r[:110].replace("\n", " "))

        r = await call("get_class_methods_by_class_full_name", {"class_full_name": INNER})
        check("[get_class_methods] anonymous inner class reachable",
              "run" in r and "ERROR" not in r, r[:110].replace("\n", " "))

        r = await call("get_derived_classes_by_class_full_name", {"class_full_name": BASE})
        check("[get_derived_classes] base receiver -> AccountReceiver",
              "AccountReceiver" in r, r[:110].replace("\n", " "))

        # ------------------------------------------------- code / id round trip
        r = await call("get_method_code_by_full_name", {"method_full_name": ENTRY})
        check("[get_method_code_by_full_name] returns the body",
              "handleBroadCastReceive" in r, r[:90].replace("\n", " "))

        r = await call("get_method_callees", {"method_full_name": ENTRY})
        m = re.search(r"method_id=(\d+)", r)
        if m:
            mid = m.group(1) + "L"
            r2 = await call("get_method_full_name_by_id", {"method_id": mid})
            check("[get_method_full_name_by_id] id round trip",
                  "ERROR" not in r2 and len(r2.strip()) > 0, r2[:90].replace("\n", " "))
        else:
            check("[get_method_full_name_by_id] id round trip", False, "no method_id in callees output")

        if "get_method_by_full_name_without_signature" in tools:
            r = await call("get_method_by_full_name_without_signature",
                           {"full_name_without_signature": CLS + ".handleBroadCastReceive"})
            check("[get_method_by_full_name_without_signature] resolves",
                  bool(r.strip()) and "ERROR" not in r, r[:90].replace("\n", " "))
        else:
            print("SKIP   [get_method_by_full_name_without_signature] not exposed by this build")

        # ------------------------------------------------- error path
        r = await call("get_method_callees", {"method_full_name": "no.such.Klass.x:void()"})
        check("[error path] explicit ERROR string, never a silent empty result",
              "ERROR" in r, r[:100].replace("\n", " "))

    failed = [n for n, ok in RESULTS if not ok]
    print("=" * 72)
    print("%d/%d checks passed" % (len(RESULTS) - len(failed), len(RESULTS)))
    if failed:
        print("failed: " + ", ".join(failed))
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
