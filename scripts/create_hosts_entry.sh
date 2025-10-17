#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root to edit /etc/hosts"
  echo "Run: sudo ./scripts/create_hosts_entry.sh"
  exit 1
fi
HOSTS_FILE="/etc/hosts"
echo "Adding local subdomains to $HOSTS_FILE"
cat >> $HOSTS_FILE <<EOF

# Erano Consulting local dev
127.0.0.1   eranoconsulting.local www.eranoconsultinggh.local clients.eranoconsultinggh.local admin.eranoconsultinggh.local
EOF
echo "Done."
