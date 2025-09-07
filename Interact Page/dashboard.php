<?php
header("Content-Type: text/plain");

echo "System Uptime\n";
echo shell_exec("uptime -p");

echo "\nCPU Load\n";
echo shell_exec("top -bn1 | grep 'Cpu' | head -n 1");

echo "\nMemory Usage\n";
echo shell_exec("free -h");

echo "\nDisk Usage (/ partition)\n";
echo shell_exec("df -h /");

echo "\nSSH Login Attempts\n";
echo shell_exec("last -a | head -n 5");
?>

