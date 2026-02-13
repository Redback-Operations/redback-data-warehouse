import streamlit as st, os, shutil

try:
    import psutil
except ImportError:
    psutil = None

st.title("💾 Local Storage")
st.markdown("---")
def human_bytes(n):
    for unit in ["B","KB","MB","GB","TB","PB"]:
        if abs(n) < 1024: return f"{n:3.1f} {unit}"
        n /= 1024
    return f"{n:.1f} EB"

disks = []
if psutil:
    for part in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(part.mountpoint)
            disks.append((part.mountpoint, u.used, u.total))
        except Exception:
            pass
else:
    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        path = f"{letter}:/"
        if os.path.exists(path):
            t,u,f = shutil.disk_usage(path)
            disks.append((path, u, t))

if not disks:
    st.warning("No disk info found.")
else:
    for mount, used, total in disks:
        pct = (used/total*100) if total else 0
        st.write(f"**{mount}** — {pct:.1f}% used ({human_bytes(used)} / {human_bytes(total)})")
        st.progress(int(pct))
