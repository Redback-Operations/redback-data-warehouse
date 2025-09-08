<?php
header("Content-Type: text/html");
$output = shell_exec('sudo ufw status 2>&1');
if ($output === null) {
    echo "<p class='status-warning'>⚠ Unable to retrieve UFW status.</p>";
    exit;
}
$lines = explode("\n", trim($output));
$statusLine = $lines[0] ?? 'Unknown status';
if (stripos($statusLine, 'inactive') !== false) {
    echo "<p class='status-bad'> UFW is not running.</p>";
} elseif (stripos($statusLine, 'active') !== false) {
    echo "<p class='status-ok'> UFW is running.</p>";
    echo "<p><strong>Open Firewall Ports:</strong></p>";
    echo "<pre class='firewall-block'>";
    foreach (array_slice($lines, 1) as $line) {
        echo htmlspecialchars($line) . "\n";
    }
    echo "</pre>";
} else {
    echo "<p class='status-warning'>Could not determine UFW status: $statusLine</p>";
}
$ip = shell_exec("hostname -I");
$gateway = shell_exec("ip route | grep default | awk '{print $3}'");
$dnsList = shell_exec("grep 'nameserver' /etc/resolv.conf | grep -v 127.0.0.53");
$dns = trim($dnsList) ?: "⚠ No external DNS server found.";
echo "<hr>";
echo '<div class="net-info">';
echo '  <h3>Network Configuration Details:</h3>';
echo '  <p> <strong>IP Address:</strong> ' . htmlspecialchars(trim($ip)) . '</p>';
echo '</div>';
?>
