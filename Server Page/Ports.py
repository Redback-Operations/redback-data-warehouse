import streamlit as st
import socket
import pandas as pd
from typing import List, Tuple

# Try psutil (best method)
try:
    import psutil
except ImportError:
    psutil = None

#--------------------------------------------------------------
# Page setup
#--------------------------------------------------------------
st.set_page_config(page_title="Open Ports Viewer", layout="wide")
st.title("🔓 Open Ports")
st.markdown("Automatically showing all listening TCP/UDP ports on this machine.")

#--------------------------------------------------------------
# Helper: Convert rows into DataFrame
#--------------------------------------------------------------
def human_ports_df(rows: List[Tuple]) -> pd.DataFrame:
    # Removed PID column from the table
    return pd.DataFrame(rows, columns=["Protocol", "Local IP", "Port", "Process"])

#--------------------------------------------------------------
# Method 1: psutil listing
#--------------------------------------------------------------
def list_open_ports_psutil():
    rows = []
    for c in psutil.net_connections(kind="inet"):
        if hasattr(c, "status") and c.status != psutil.CONN_LISTEN:
            continue
        if not c.laddr:
            continue

        ip = getattr(c.laddr, "ip", c.laddr[0])
        port = getattr(c.laddr, "port", c.laddr[1])
        proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
        pid = c.pid or None

        # Resolve process name only (no PID)
        pname = "-"
        if pid:
            try:
                pname = psutil.Process(pid).name()
            except:
                pname = "-"

        # No PID added to the row
        rows.append((proto, ip, port, pname))

    return human_ports_df(rows)

#--------------------------------------------------------------
# Method 2: netstat fallback (Windows)
#--------------------------------------------------------------
def list_open_ports_netstat():
    import subprocess, re
    try:
        output = subprocess.check_output(["netstat", "-ano"], text=True)
    except:
        return pd.DataFrame(columns=["Protocol", "Local IP", "Port", "Process"])

    rows = []
    for line in output.splitlines():
        match = re.search(r"^(TCP|UDP)\s+(\S+):(\d+)\s+.*LISTENING\s+(\d+)", line, re.I)
        if match:
            proto, ip, port, _pid = match.groups()
            rows.append((proto, ip, int(port), "-"))  # No PID kept

    return human_ports_df(rows)

#--------------------------------------------------------------
# Select method & display
#--------------------------------------------------------------
if psutil:
    df = list_open_ports_psutil()
else:
    df = list_open_ports_netstat()

df = df.sort_values(["Protocol", "Port"]).reset_index(drop=True)

if df.empty:
    st.info("No open ports detected or missing permissions.")
else:
    st.success(f"Found {len(df)} listening ports:")

    # Full page table, scrolls with the page
    st.table(df)
