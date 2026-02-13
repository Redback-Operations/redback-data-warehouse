import streamlit as st
import psutil
import datetime

st.title("🗄️ Server Info")
st.markdown("---")

boot_time_timestamp = psutil.boot_time()
boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)

now = datetime.datetime.now()
uptime = now - boot_time

st.subheader("🖥 PC/Server Boot Time:")
st.write(boot_time.strftime("%Y-%m-%d %H:%M:%S"))
st.markdown("---")
st.subheader("⏱ Current Uptime:")
days = uptime.days
hours, remainder = divmod(uptime.seconds, 3600)
minutes, seconds = divmod(remainder, 60)
st.write(f"**{days} days, {hours} hours, {minutes} minutes, {seconds} seconds**")
st.markdown("---")
