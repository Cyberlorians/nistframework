#!/usr/bin/env python3
"""Generate the ATO Logging Validation workbook JSON - v4.
Component filter, NIST 800-53 controls, row-click drill-down log viewer."""
import json, uuid

def uid():
    return str(uuid.uuid4())

# ── Table Definitions ──────────────────────────────────────────────
# (Component, DisplayName, CheckTable, ResourceTypeFilter, EnableLink, Controls)
CHECKS = [
    # ── Entra ID ──
    ("Entra ID", "Sign-in Logs", "SigninLogs", None,
     "https://learn.microsoft.com/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs",
     "AC-2, IA-2, AU-2, AU-3"),
    ("Entra ID", "Non-Interactive Sign-ins", "AADNonInteractiveUserSignInLogs", None,
     "https://learn.microsoft.com/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs",
     "AC-2, IA-2, AU-2, AU-3"),
    ("Entra ID", "Audit Logs", "AuditLogs", None,
     "https://learn.microsoft.com/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs",
     "AC-2, AC-6, AU-2, AU-3, AU-12"),
    ("Entra ID", "Service Principal Sign-ins", "AADServicePrincipalSignInLogs", None,
     "https://learn.microsoft.com/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs",
     "AC-2, IA-2, AU-2"),
    ("Entra ID", "Managed Identity Sign-ins", "AADManagedIdentitySignInLogs", None,
     "https://learn.microsoft.com/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs",
     "AC-2, IA-2, IA-4, AU-2"),
    ("Entra ID", "Provisioning Logs", "AADProvisioningLogs", None,
     "https://learn.microsoft.com/entra/identity/monitoring-health/howto-integrate-activity-logs-with-azure-monitor-logs",
     "AC-2, AU-2, AU-12"),
    ("Entra ID", "Risky Users", "AADRiskyUsers", None,
     "https://learn.microsoft.com/entra/id-protection/howto-export-risk-data",
     "AC-2, IA-5, SI-4, RA-5"),
    ("Entra ID", "User Risk Events", "AADUserRiskEvents", None,
     "https://learn.microsoft.com/entra/id-protection/howto-export-risk-data",
     "AC-2, IA-5, SI-4, RA-5"),
    ("Entra ID", "Risky Service Principals", "AADRiskyServicePrincipals", None,
     "https://learn.microsoft.com/entra/id-protection/howto-export-risk-data",
     "AC-2, IA-5, SI-4"),
    ("Entra ID", "SP Risk Events", "AADServicePrincipalRiskEvents", None,
     "https://learn.microsoft.com/entra/id-protection/howto-export-risk-data",
     "AC-2, IA-5, SI-4, RA-5"),
    ("Entra ID", "Graph Activity Logs", "MicrosoftGraphActivityLogs", None,
     "https://learn.microsoft.com/graph/microsoft-graph-activity-logs-overview",
     "AC-2, AC-6, AU-2, AU-3, SI-4"),

    # ── Azure Activity ──
    ("Azure Activity", "Activity Logs", "AzureActivity", None,
     "https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log",
     "AU-2, AU-3, AU-6, AU-12, CM-3"),

    # ── Azure Firewall (Secured Hub) ──
    ("Azure Firewall", "Application Rules", "AZFWApplicationRule", None,
     "https://learn.microsoft.com/azure/firewall/firewall-structured-logs",
     "SC-7, AU-2, SI-4, AC-4"),
    ("Azure Firewall", "Network Rules", "AZFWNetworkRule", None,
     "https://learn.microsoft.com/azure/firewall/firewall-structured-logs",
     "SC-7, AU-2, SI-4, AC-4"),
    ("Azure Firewall", "Threat Intel", "AZFWThreatIntel", None,
     "https://learn.microsoft.com/azure/firewall/firewall-structured-logs",
     "SC-7, SI-4, SI-3"),
    ("Azure Firewall", "DNS Queries", "AZFWDnsQuery", None,
     "https://learn.microsoft.com/azure/firewall/firewall-structured-logs",
     "SC-7, SC-20, SI-4"),
    ("Azure Firewall", "NAT Rules", "AZFWNatRule", None,
     "https://learn.microsoft.com/azure/firewall/firewall-structured-logs",
     "SC-7, AU-2, AC-4"),
    ("Azure Firewall", "IDPS Signatures", "AZFWIdpsSignature", None,
     "https://learn.microsoft.com/azure/firewall/firewall-structured-logs",
     "SC-7, SI-3, SI-4"),
    ("Azure Firewall", "Flow Trace", "AZFWFlowTrace", None,
     "https://learn.microsoft.com/azure/firewall/firewall-structured-logs",
     "SC-7, AU-2, SI-4, AC-4"),

    # ── VPN Gateway ──
    ("VPN Gateway", "Gateway Diagnostics", "AzureDiagnostics", "VPNGATEWAYS",
     "https://learn.microsoft.com/azure/vpn-gateway/monitor-vpn-gateway",
     "SC-7, AC-17, AU-2, SC-8"),

    # ── ExpressRoute ──
    ("ExpressRoute", "ER Gateway Diagnostics", "AzureDiagnostics", "EXPRESSROUTEGATEWAYS",
     "https://learn.microsoft.com/azure/expressroute/monitor-expressroute",
     "SC-7, AC-17, AU-2"),
    ("ExpressRoute", "ER Circuit Diagnostics", "AzureDiagnostics", "EXPRESSROUTECIRCUITS",
     "https://learn.microsoft.com/azure/expressroute/monitor-expressroute",
     "SC-7, AC-17, AU-2"),

    # ── Virtual WAN ──
    ("Virtual WAN", "vWAN Diagnostics", "AzureDiagnostics", "VIRTUALWANS",
     "https://learn.microsoft.com/azure/virtual-wan/monitor-virtual-wan",
     "SC-7, AU-2, AC-4"),
    ("Virtual WAN", "vHub Diagnostics", "AzureDiagnostics", "VIRTUALHUBS",
     "https://learn.microsoft.com/azure/virtual-wan/monitor-virtual-wan",
     "SC-7, AU-2, AC-4"),

    # ── Key Vault ──
    ("Key Vault", "Key Vault Audit Events", "AzureDiagnostics", "VAULTS",
     "https://learn.microsoft.com/azure/key-vault/general/logging",
     "SC-12, SC-28, AU-2, AU-3, AC-6"),
    ("Key Vault", "KV Audit Logs (Resource)", "AZKVAuditLogs", None,
     "https://learn.microsoft.com/azure/key-vault/general/logging",
     "SC-12, SC-28, AU-2, AU-3, AC-6"),
    ("Key Vault", "KV Policy Evaluation", "AZKVPolicyEvaluationDetailsLogs", None,
     "https://learn.microsoft.com/azure/key-vault/general/logging",
     "SC-12, CM-6, AU-2"),

    # ── Storage Account ──
    ("Storage Account", "Blob Logs", "StorageBlobLogs", None,
     "https://learn.microsoft.com/azure/storage/blobs/monitor-blob-storage",
     "AU-2, AU-3, SC-28, AC-3"),
    ("Storage Account", "Queue Logs", "StorageQueueLogs", None,
     "https://learn.microsoft.com/azure/storage/queues/monitor-queue-storage",
     "AU-2, AU-3, SC-28, AC-3"),
    ("Storage Account", "Table Logs", "StorageTableLogs", None,
     "https://learn.microsoft.com/azure/storage/tables/monitor-table-storage",
     "AU-2, AU-3, SC-28, AC-3"),
    ("Storage Account", "File Logs", "StorageFileLogs", None,
     "https://learn.microsoft.com/azure/storage/files/storage-files-monitoring",
     "AU-2, AU-3, SC-28, AC-3"),

    # ── Recovery Services Vault ──
    ("Recovery Services", "Core Backup", "CoreAzureBackup", None,
     "https://learn.microsoft.com/azure/backup/backup-azure-diagnostic-events",
     "CP-9, CP-10, AU-2"),
    ("Recovery Services", "Backup Jobs", "AddonAzureBackupJobs", None,
     "https://learn.microsoft.com/azure/backup/backup-azure-diagnostic-events",
     "CP-9, CP-10, AU-2"),
    ("Recovery Services", "Backup Policy", "AddonAzureBackupPolicy", None,
     "https://learn.microsoft.com/azure/backup/backup-azure-diagnostic-events",
     "CP-9, CP-10, CM-6"),
    ("Recovery Services", "Backup Storage", "AddonAzureBackupStorage", None,
     "https://learn.microsoft.com/azure/backup/backup-azure-diagnostic-events",
     "CP-9, CP-10, AU-2"),
    ("Recovery Services", "Backup Alerts", "AddonAzureBackupAlerts", None,
     "https://learn.microsoft.com/azure/backup/backup-azure-diagnostic-events",
     "CP-9, CP-10, SI-4"),
    ("Recovery Services", "Protected Instances", "AddonAzureBackupProtectedInstance", None,
     "https://learn.microsoft.com/azure/backup/backup-azure-diagnostic-events",
     "CP-9, CP-10, CM-8"),
    ("Recovery Services", "Backup Operations", "AzureBackupOperations", None,
     "https://learn.microsoft.com/azure/backup/backup-azure-diagnostic-events",
     "CP-9, CP-10, AU-2"),
    ("Recovery Services", "ASR Events", "AzureDiagnostics", "VAULTS/REPLICATIONEVENTS",
     "https://learn.microsoft.com/azure/site-recovery/monitor-log-analytics",
     "CP-9, CP-10, AU-2"),
    ("Recovery Services", "ASR Jobs", "ASRJobs", None,
     "https://learn.microsoft.com/azure/site-recovery/monitor-log-analytics",
     "CP-9, CP-10, AU-2"),
    ("Recovery Services", "ASR Replicated Items", "ASRReplicatedItems", None,
     "https://learn.microsoft.com/azure/site-recovery/monitor-log-analytics",
     "CP-9, CP-10, CM-8"),

    # ── NSG / Network ──
    ("NSG Flow Logs", "Network Analytics", "AzureNetworkAnalytics_CL", None,
     "https://learn.microsoft.com/azure/network-watcher/nsg-flow-logs-overview",
     "SC-7, AU-2, AU-3, SI-4, AC-4"),
    ("NSG Flow Logs", "NTA Net Analytics", "NTANetAnalytics", None,
     "https://learn.microsoft.com/azure/network-watcher/traffic-analytics",
     "SC-7, AU-2, SI-4, AC-4"),

    # ── Private DNS ──
    ("DNS", "DNS Resolver Queries", "AzureDiagnostics", "DNSRESOLVERS",
     "https://learn.microsoft.com/azure/dns/private-resolver-endpoints-rulesets",
     "SC-7, SC-20, SC-21, AU-2"),
    ("DNS", "Private DNS Zones", "AzureDiagnostics", "PRIVATEDNSZONES",
     "https://learn.microsoft.com/azure/dns/private-dns-logging",
     "SC-7, SC-20, SC-21, AU-2"),

    # ── Event Hub ──
    ("Event Hub", "Event Hub Diagnostics", "AzureDiagnostics", "NAMESPACES",
     "https://learn.microsoft.com/azure/event-hubs/monitor-event-hubs",
     "AU-2, AU-9, AU-4"),

    # ── Automation Account ──
    ("Automation Account", "Automation Diagnostics", "AzureDiagnostics", "AUTOMATIONACCOUNTS",
     "https://learn.microsoft.com/azure/automation/automation-manage-send-joblogs-log-analytics",
     "CM-3, CM-6, AU-2, AU-12"),

    # ── AVD ──
    ("AVD", "Connections", "WVDConnections", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "AC-2, AC-17, AU-2, AU-3"),
    ("AVD", "Checkpoints", "WVDCheckpoints", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "AU-2, AU-3, SI-4"),
    ("AVD", "Errors", "WVDErrors", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "AU-2, SI-4, SI-11"),
    ("AVD", "Management", "WVDManagement", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "CM-3, CM-6, AU-2"),
    ("AVD", "Host Registrations", "WVDHostRegistrations", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "CM-3, CM-8, AU-2"),
    ("AVD", "Agent Health Status", "WVDAgentHealthStatus", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "SI-4, CM-8, AU-2"),
    ("AVD", "Connection Network Data", "WVDConnectionNetworkData", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "AC-17, SC-7, AU-2"),
    ("AVD", "Connection Graphics Preview", "WVDConnectionGraphicsDataPreview", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "AC-17, AU-2"),
    ("AVD", "Session Host Mgmt", "WVDSessionHostManagement", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "CM-3, CM-6, AU-2"),
    ("AVD", "Autoscale Pooled", "WVDAutoscaleEvaluationPooled", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "CM-6, AU-2"),
    ("AVD", "Feeds", "WVDFeeds", None,
     "https://learn.microsoft.com/azure/virtual-desktop/diagnostics-log-analytics",
     "AC-2, AU-2, CM-6"),

    # ── VMs / Session Hosts ──
    ("VMs / Hosts", "Windows Security Events", "SecurityEvent", None,
     "https://learn.microsoft.com/azure/sentinel/data-connectors/windows-security-events-via-ama",
     "AU-2, AU-3, AU-6, SI-4, AC-2"),
    ("VMs / Hosts", "Windows Events", "Event", None,
     "https://learn.microsoft.com/azure/azure-monitor/agents/data-collection-windows-events",
     "AU-2, AU-3, AU-12"),
    ("VMs / Hosts", "Heartbeat (Agent)", "Heartbeat", None,
     "https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-overview",
     "CM-8, SI-4"),
    ("VMs / Hosts", "Performance Counters", "Perf", None,
     "https://learn.microsoft.com/azure/azure-monitor/agents/data-collection-performance",
     "AU-2, SI-4, CM-8"),
    ("VMs / Hosts", "VM Insights Metrics", "InsightsMetrics", None,
     "https://learn.microsoft.com/azure/azure-monitor/vm/vminsights-overview",
     "SI-4, CM-8"),

    # ── SD-WAN / NVA ──
    ("SD-WAN / NVA", "Syslog", "Syslog", None,
     "https://learn.microsoft.com/azure/sentinel/connect-syslog",
     "SC-7, AU-2, AU-3, SI-4"),
    ("SD-WAN / NVA", "CEF (CommonSecurityLog)", "CommonSecurityLog", None,
     "https://learn.microsoft.com/azure/sentinel/connect-common-event-format",
     "SC-7, AU-2, AU-3, SI-4"),

    # ── Defender for Cloud ──
    ("Defender for Cloud", "Security Alerts", "SecurityAlert", None,
     "https://learn.microsoft.com/azure/sentinel/connect-defender-for-cloud",
     "SI-4, RA-5, IR-4, IR-5"),
    ("Defender for Cloud", "Recommendations", "SecurityRecommendation", None,
     "https://learn.microsoft.com/azure/sentinel/connect-defender-for-cloud",
     "RA-5, SI-4, CM-6"),
    ("Defender for Cloud", "Regulatory Compliance", "SecurityRegulatoryCompliance", None,
     "https://learn.microsoft.com/azure/defender-for-cloud/regulatory-compliance-dashboard",
     "RA-5, CM-6, AU-2"),

    # ── Sentinel / Workspace ──
    ("Sentinel", "Incidents", "SecurityIncident", None,
     "https://learn.microsoft.com/azure/sentinel/investigate-incidents",
     "IR-4, IR-5, AU-6, SI-4"),
    ("Sentinel", "Health Diagnostics", "SentinelHealth", None,
     "https://learn.microsoft.com/azure/sentinel/monitor-sentinel-health",
     "AU-2, SI-4, AU-9"),
    ("Sentinel", "Audit Logs", "SentinelAudit", None,
     "https://learn.microsoft.com/azure/sentinel/audit-sentinel-data",
     "AU-2, AU-3, AU-12, AC-6"),
    ("Sentinel", "Workspace Query Audit", "LAQueryLogs", None,
     "https://learn.microsoft.com/azure/azure-monitor/logs/query-audit",
     "AU-2, AU-3, AU-12, AC-6"),
    ("Sentinel", "Threat Intelligence", "ThreatIntelligenceIndicator", None,
     "https://learn.microsoft.com/azure/sentinel/understand-threat-intelligence",
     "SI-4, SI-3, RA-5"),
    ("Sentinel", "Anomalies (ML)", "Anomalies", None,
     "https://learn.microsoft.com/azure/sentinel/anomalies-reference",
     "SI-4, RA-5, IR-4"),
]

# Build unique check IDs
def check_id(check_table, res_filter):
    if res_filter:
        return f"AzDiag_{res_filter.replace('/', '_')}"
    return check_table

# Deduplicate checks (same table+filter)
unique_checks = {}
for comp, display, table, res_filter, link, controls in CHECKS:
    cid = check_id(table, res_filter)
    if cid not in unique_checks:
        unique_checks[cid] = (table, res_filter)

# Get unique raw tables (for getschema)
unique_raw_tables = list(dict.fromkeys(c[2] for c in CHECKS))

# All component names
components = list(dict.fromkeys(c[0] for c in CHECKS))


def build_main_query():
    """Main query with Controls and ResourceFilter columns."""
    time_expr = "ago({TimeRange})"
    lines = []

    lines.append("let Expected = datatable(Component:string, DisplayName:string, CheckId:string, SentinelTable:string, EnableLink:string, Controls:string, ResourceFilter:string) [")
    for i, (comp, display, table, res_filter, link, controls) in enumerate(CHECKS):
        cid = check_id(table, res_filter)
        rf = res_filter.split("/")[0] if res_filter else ""
        comma = "," if i < len(CHECKS) - 1 else ""
        lines.append(f"    '{comp}', '{display}', '{cid}', '{table}', '{link}', '{controls}', '{rf}'{comma}")
    lines.append("];")

    lines.append("let SchemaCheck = union isfuzzy=true")
    for i, table in enumerate(unique_raw_tables):
        comma = "," if i < len(unique_raw_tables) - 1 else ""
        lines.append(f"    ({table} | getschema | take 1 | project T='{table}'){comma}")
    lines.append("| distinct T;")

    check_list = list(unique_checks.items())
    lines.append("let DataCheck = union isfuzzy=true")
    for i, (cid, (table, res_filter)) in enumerate(check_list):
        comma = "," if i < len(check_list) - 1 else ""
        if res_filter:
            rt = res_filter.split("/")[0]
            lines.append(f"    ({table} | where ResourceType == \"{rt}\" | where TimeGenerated > {time_expr} | take 1 | summarize Last=max(TimeGenerated) | extend CheckId='{cid}'){comma}")
        else:
            lines.append(f"    ({table} | where TimeGenerated > {time_expr} | take 1 | summarize Last=max(TimeGenerated) | extend CheckId='{cid}'){comma}")
    lines.append(";")

    lines.append("Expected")
    lines.append("| join kind=leftouter (DataCheck) on CheckId")
    lines.append("| extend TableInSchema = SentinelTable in (SchemaCheck)")
    lines.append("| extend Status = case(")
    lines.append("    isnotnull(Last), 'Ingesting',")
    lines.append("    TableInSchema, 'Validated - No Data',")
    lines.append("    'Not Configured')")
    lines.append("| extend LastSeen = case(")
    lines.append("    isnotnull(Last), format_datetime(Last, 'yyyy-MM-dd HH:mm'),")
    lines.append("    TableInSchema, 'schema only, no data in range',")
    lines.append("    'not in workspace')")
    lines.append("| where '{SelectedComponent}' == 'All' or Component == '{SelectedComponent}'")
    lines.append("| extend _sort = case(Status has 'Not', 0, Status has 'Validated', 1, 2)")
    lines.append("| sort by _sort asc, Component asc, DisplayName asc")
    lines.append("| project Component, ['Log Source']=DisplayName, ['Table']=SentinelTable, Status, ['Last Record']=LastSeen, ['NIST 800-53']=Controls, ['Enable']=EnableLink, ResourceFilter")

    return "\r\n".join(lines)


def build_summary_query():
    """Summary counts per component for bar chart."""
    time_expr = "ago({TimeRange})"
    lines = []

    lines.append("let Expected = datatable(Component:string, CheckId:string, SentinelTable:string) [")
    for i, (comp, display, table, res_filter, link, controls) in enumerate(CHECKS):
        cid = check_id(table, res_filter)
        comma = "," if i < len(CHECKS) - 1 else ""
        lines.append(f"    '{comp}', '{cid}', '{table}'{comma}")
    lines.append("];")

    lines.append("let SchemaCheck = union isfuzzy=true")
    for i, table in enumerate(unique_raw_tables):
        comma = "," if i < len(unique_raw_tables) - 1 else ""
        lines.append(f"    ({table} | getschema | take 1 | project T='{table}'){comma}")
    lines.append("| distinct T;")

    check_list = list(unique_checks.items())
    lines.append("let DataCheck = union isfuzzy=true")
    for i, (cid, (table, res_filter)) in enumerate(check_list):
        comma = "," if i < len(check_list) - 1 else ""
        if res_filter:
            rt = res_filter.split("/")[0]
            lines.append(f"    ({table} | where ResourceType == \"{rt}\" | where TimeGenerated > {time_expr} | take 1 | summarize Last=max(TimeGenerated) | extend CheckId='{cid}'){comma}")
        else:
            lines.append(f"    ({table} | where TimeGenerated > {time_expr} | take 1 | summarize Last=max(TimeGenerated) | extend CheckId='{cid}'){comma}")
    lines.append(";")

    lines.append("Expected")
    lines.append("| join kind=leftouter (DataCheck) on CheckId")
    lines.append("| extend TableInSchema = SentinelTable in (SchemaCheck)")
    lines.append("| extend State = case(isnotnull(Last), 'Ingesting', TableInSchema, 'Validated', 'Not Configured')")
    lines.append("| summarize ['Ingesting']=countif(State=='Ingesting'), ['Validated No Data']=countif(State=='Validated'), ['Not Configured']=countif(State=='Not Configured') by Component")
    lines.append("| sort by ['Not Configured'] desc, Component asc")

    return "\r\n".join(lines)


def build_tile_query():
    """Summary tiles — respects {SelectedComponent} filter."""
    time_expr = "ago({TimeRange})"
    lines = []

    lines.append("let Expected = datatable(Component:string, CheckId:string, SentinelTable:string) [")
    for i, (comp, display, table, res_filter, link, controls) in enumerate(CHECKS):
        cid = check_id(table, res_filter)
        comma = "," if i < len(CHECKS) - 1 else ""
        lines.append(f"    '{comp}', '{cid}', '{table}'{comma}")
    lines.append("];")

    lines.append("let Filtered = Expected | where '{SelectedComponent}' == 'All' or Component == '{SelectedComponent}';")
    lines.append("let TotalExpected = toscalar(Filtered | count);")

    lines.append("let SchemaCheck = union isfuzzy=true")
    for i, table in enumerate(unique_raw_tables):
        comma = "," if i < len(unique_raw_tables) - 1 else ""
        lines.append(f"    ({table} | getschema | take 1 | project T='{table}'){comma}")
    lines.append("| distinct T;")

    check_list = list(unique_checks.items())
    lines.append("let DataCheck = union isfuzzy=true")
    for i, (cid, (table, res_filter)) in enumerate(check_list):
        comma = "," if i < len(check_list) - 1 else ""
        if res_filter:
            rt = res_filter.split("/")[0]
            lines.append(f"    ({table} | where ResourceType == \"{rt}\" | where TimeGenerated > {time_expr} | take 1 | project CheckId='{cid}'){comma}")
        else:
            lines.append(f"    ({table} | where TimeGenerated > {time_expr} | take 1 | project CheckId='{cid}'){comma}")
    lines.append("| distinct CheckId;")

    lines.append("Filtered")
    lines.append("| extend TableInSchema = SentinelTable in (SchemaCheck)")
    lines.append("| extend HasData = CheckId in (DataCheck)")
    lines.append("| extend State = case(HasData, 'Ingesting', TableInSchema, 'Validated', 'NotConfigured')")
    lines.append("| summarize Ingesting=countif(State=='Ingesting'), Validated=countif(State=='Validated'), NotConfigured=countif(State=='NotConfigured')")
    lines.append("| extend Total = Ingesting + Validated + NotConfigured")
    lines.append("| extend Coverage = strcat(round(todouble(Ingesting) / Total * 100, 0), '%')")
    lines.append("| project ['✅ Ingesting']=Ingesting, ['⚠️ Validated']=Validated, ['❌ Not Configured']=NotConfigured, Total, ['Coverage %']=Coverage")

    return "\r\n".join(lines)


def build_drilldown_query():
    """Drill-down query using exported SelectedTable and SelectedResourceFilter.
    Handles tables that don't have a ResourceType column gracefully."""
    lines = []
    lines.append("{SelectedTable}")
    lines.append("| where TimeGenerated > ago({TimeRange})")
    lines.append("| extend _hasRT = column_ifexists('ResourceType', '')")
    lines.append("| where '{SelectedResourceFilter}' == '' or _hasRT == '{SelectedResourceFilter}'")
    lines.append("| project-away _hasRT")
    lines.append("| project-reorder TimeGenerated")
    lines.append("| sort by TimeGenerated desc")
    lines.append("| take 50")
    return "\r\n".join(lines)


# ── Build Workbook JSON ───────────────────────────────────────────

component_options_json = json.dumps(
    [{"value": "All", "label": "All", "selected": True}] +
    [{"value": c, "label": c} for c in components]
)

workbook = {
    "version": "Notebook/1.0",
    "items": [
        # ── Header ──
        {
            "type": 1,
            "content": {
                "json": (
                    "## ATO Logging Validation\n"
                    "Validates every architecture component from the Azure Gov landing zone is sending logs to Sentinel.  \n"
                    "✅ Ingesting &nbsp;|&nbsp; "
                    "⚠️ Validated (table exists, no data) &nbsp;|&nbsp; "
                    "❌ Not Configured (enable connector)  \n"
                    "**Click any row** to preview log records from that table."
                )
            },
            "customWidth": "100",
            "name": "Header"
        },
        # ── Subscription / Workspace / Time Range ──
        {
            "type": 9,
            "content": {
                "version": "KqlParameterItem/1.0",
                "parameters": [
                    # Hidden param: auto-detect default subscription from ARG
                    {
                        "id": uid(),
                        "version": "KqlParameterItem/1.0",
                        "name": "DefaultSubscription_Internal",
                        "type": 1,
                        "isRequired": True,
                        "query": "where type =~ 'microsoft.operationalinsights/workspaces'\r\n| take 1\r\n| project subscriptionId",
                        "crossComponentResources": ["value::selected"],
                        "isHiddenWhenLocked": True,
                        "queryType": 1,
                        "resourceType": "microsoft.resourcegraph/resources"
                    },
                    # Subscription picker – ARG-backed, multi-select
                    {
                        "id": uid(),
                        "version": "KqlParameterItem/1.0",
                        "name": "Subscription",
                        "type": 6,
                        "isRequired": True,
                        "multiSelect": True,
                        "quote": "'",
                        "delimiter": ",",
                        "query": "summarize by subscriptionId\r\n| project value = strcat('/subscriptions/', subscriptionId), label = subscriptionId, selected = iff(subscriptionId =~ '{DefaultSubscription_Internal}', true, false)",
                        "crossComponentResources": ["value::all"],
                        "typeSettings": {
                            "additionalResourceOptions": ["value::all"],
                            "showDefault": False
                        },
                        "queryType": 1,
                        "resourceType": "microsoft.resourcegraph/resources",
                        "value": ["value::all"]
                    },
                    # Workspace picker – ARG-backed, multi-select, auto-selects first 10
                    {
                        "id": uid(),
                        "version": "KqlParameterItem/1.0",
                        "name": "Workspace",
                        "label": "Log Analytics Workspace",
                        "type": 5,
                        "isRequired": True,
                        "multiSelect": True,
                        "quote": "'",
                        "delimiter": ",",
                        "query": "resources\r\n| where type =~ 'microsoft.operationalinsights/workspaces'\r\n| order by name asc\r\n| summarize Selected = makelist(id, 10), All = makelist(id, 1000)\r\n| mvexpand All limit 100\r\n| project value = tostring(All), label = tostring(All), selected = iff(Selected contains All, true, false)",
                        "crossComponentResources": ["{Subscription}"],
                        "typeSettings": {
                            "additionalResourceOptions": ["value::all"],
                            "showDefault": False
                        },
                        "queryType": 1,
                        "resourceType": "microsoft.resourcegraph/resources",
                        "value": ["value::all"]
                    },
                    {
                        "id": uid(),
                        "version": "KqlParameterItem/1.0",
                        "name": "TimeRange",
                        "label": "Time Range",
                        "type": 2,
                        "isRequired": True,
                        "jsonData": json.dumps([
                            {"value": "1d",  "label": "Last 1 day"},
                            {"value": "3d",  "label": "Last 3 days"},
                            {"value": "7d",  "label": "Last 7 days"},
                            {"value": "14d", "label": "Last 14 days", "selected": True},
                            {"value": "30d", "label": "Last 30 days"},
                            {"value": "90d", "label": "Last 90 days"}
                        ]),
                        "value": "14d"
                    }
                ],
                "style": "pills",
                "queryType": 0,
                "resourceType": "microsoft.operationalinsights/workspaces"
            },
            "name": "Global Parameters"
        },
        # ── Component Filter (left 20%) ──
        {
            "type": 9,
            "content": {
                "version": "KqlParameterItem/1.0",
                "parameters": [
                    {
                        "id": uid(),
                        "version": "KqlParameterItem/1.0",
                        "name": "SelectedComponent",
                        "label": "Component",
                        "type": 2,
                        "isRequired": True,
                        "typeSettings": {
                            "additionalResourceOptions": [],
                            "showDefault": False
                        },
                        "jsonData": component_options_json,
                        "value": "All"
                    }
                ],
                "style": "pills",
                "queryType": 0,
                "resourceType": "microsoft.operationalinsights/workspaces"
            },
            "customWidth": "15",
            "name": "Component Filter"
        },
        # ── Summary Tiles (middle 40%) ──
        {
            "type": 3,
            "content": {
                "version": "KqlItem/1.0",
                "query": build_tile_query(),
                "size": 4,
                "title": "ATO Readiness",
                "queryType": 0,
                "resourceType": "microsoft.operationalinsights/workspaces",
                "crossComponentResources": ["{Workspace}"],
                "visualization": "table",
                "gridSettings": {
                    "formatters": [
                        {
                            "columnMatch": "Ingesting",
                            "formatter": 18,
                            "formatOptions": {
                                "thresholdsOptions": "colors",
                                "thresholdsGrid": [
                                    {"operator": "Default", "representation": "green", "text": "{0}{1}"}
                                ],
                                "customColumnWidthSetting": "125px"
                            }
                        },
                        {
                            "columnMatch": "Validated",
                            "formatter": 18,
                            "formatOptions": {
                                "thresholdsOptions": "colors",
                                "thresholdsGrid": [
                                    {"operator": "Default", "representation": "yellow", "text": "{0}{1}"}
                                ],
                                "customColumnWidthSetting": "125px"
                            }
                        },
                        {
                            "columnMatch": "Not Configured",
                            "formatter": 18,
                            "formatOptions": {
                                "thresholdsOptions": "colors",
                                "thresholdsGrid": [
                                    {"operator": "Default", "representation": "redBright", "text": "{0}{1}"}
                                ],
                                "customColumnWidthSetting": "155px"
                            }
                        },
                        {
                            "columnMatch": "Total",
                            "formatter": 0,
                            "formatOptions": {
                                "customColumnWidthSetting": "70px"
                            }
                        },
                        {
                            "columnMatch": "Coverage",
                            "formatter": 18,
                            "formatOptions": {
                                "thresholdsOptions": "colors",
                                "thresholdsGrid": [
                                    {"operator": "Default", "representation": "blue", "text": "{0}{1}"}
                                ],
                                "customColumnWidthSetting": "115px"
                            }
                        }
                    ]
                }
            },
            "customWidth": "50",
            "name": "Readiness Summary"
        },
        # ── Coverage Bar Chart (right 45%) ──
        {
            "type": 3,
            "content": {
                "version": "KqlItem/1.0",
                "query": build_summary_query(),
                "size": 1,
                "title": "Coverage by Component",
                "queryType": 0,
                "resourceType": "microsoft.operationalinsights/workspaces",
                "crossComponentResources": ["{Workspace}"],
                "visualization": "barchart",
                "chartSettings": {
                    "xAxis": "Component",
                    "yAxis": ["Ingesting", "Validated No Data", "Not Configured"],
                    "showLegend": True,
                    "seriesLabelSettings": [
                        {"seriesName": "Ingesting", "color": "green"},
                        {"seriesName": "Validated No Data", "color": "yellow"},
                        {"seriesName": "Not Configured", "color": "redBright"}
                    ]
                }
            },
            "customWidth": "35",
            "name": "Coverage Bar Chart"
        },
        # ── Main Status Table (exports row click) ──
        {
            "type": 3,
            "content": {
                "version": "KqlItem/1.0",
                "query": build_main_query(),
                "size": 0,
                "showAnalytics": True,
                "showExportToExcel": True,
                "title": "Table Ingestion Status",
                "queryType": 0,
                "resourceType": "microsoft.operationalinsights/workspaces",
                "crossComponentResources": ["{Workspace}"],
                "visualization": "table",
                "gridSettings": {
                    "formatters": [
                        {
                            "columnMatch": "Component",
                            "formatter": 0,
                            "formatOptions": {
                                "customColumnWidthSetting": "130px"
                            }
                        },
                        {
                            "columnMatch": "Log Source",
                            "formatter": 0,
                            "formatOptions": {
                                "customColumnWidthSetting": "200px"
                            }
                        },
                        {
                            "columnMatch": "Table",
                            "formatter": 0,
                            "formatOptions": {
                                "customColumnWidthSetting": "250px"
                            }
                        },
                        {
                            "columnMatch": "Status",
                            "formatter": 18,
                            "formatOptions": {
                                "thresholdsOptions": "icons",
                                "thresholdsGrid": [
                                    {"operator": "contains", "thresholdValue": "Ingesting", "representation": "success", "text": "{0}{1}"},
                                    {"operator": "contains", "thresholdValue": "Validated", "representation": "warning", "text": "{0}{1}"},
                                    {"operator": "contains", "thresholdValue": "Not Configured", "representation": "4", "text": "{0}{1}"},
                                    {"operator": "Default", "representation": "question", "text": "{0}{1}"}
                                ],
                                "customColumnWidthSetting": "190px"
                            }
                        },
                        {
                            "columnMatch": "Last Record",
                            "formatter": 0,
                            "formatOptions": {
                                "customColumnWidthSetting": "185px"
                            }
                        },
                        {
                            "columnMatch": "NIST 800-53",
                            "formatter": 0,
                            "formatOptions": {
                                "customColumnWidthSetting": "190px"
                            }
                        },
                        {
                            "columnMatch": "Enable",
                            "formatter": 7,
                            "formatOptions": {
                                "linkTarget": "Url",
                                "linkLabel": "Docs →",
                                "customColumnWidthSetting": "80px"
                            }
                        },
                        {
                            "columnMatch": "ResourceFilter",
                            "formatter": 5
                        }
                    ],
                    "filter": True,
                    "sortBy": [
                        {"itemKey": "Status", "sortOrder": 1}
                    ]
                },
                "exportedParameters": [
                    {"fieldName": "Table", "parameterName": "SelectedTable", "parameterType": 1},
                    {"fieldName": "ResourceFilter", "parameterName": "SelectedResourceFilter", "parameterType": 1},
                    {"fieldName": "Log Source", "parameterName": "SelectedLogSource", "parameterType": 1}
                ]
            },
            "name": "Ingestion Status Table"
        },
        # ── Drill-down Log Viewer (hidden until row click) ──
        {
            "type": 3,
            "content": {
                "version": "KqlItem/1.0",
                "query": build_drilldown_query(),
                "size": 0,
                "showAnalytics": True,
                "title": "Log Preview — {SelectedLogSource} ({SelectedTable})",
                "noDataMessage": "⚠️ Check Validation — this table has no records in the selected time range or is not yet configured. Use the 'Docs →' link to enable.",
                "queryType": 0,
                "resourceType": "microsoft.operationalinsights/workspaces",                "crossComponentResources": ["{Workspace}"],                "visualization": "table",
                "gridSettings": {
                    "filter": True
                }
            },
            "conditionalVisibilities": [
                {
                    "parameterName": "SelectedTable",
                    "comparison": "isNotEqualTo",
                    "value": ""
                },
                {
                    "parameterName": "SelectedTable",
                    "comparison": "isNotEqualTo",
                    "value": "null"
                }
            ],
            "name": "Log Drill-Down"
        }
    ],
    "fallbackResourceIds": [],
    "fromTemplateId": "custom-ato-logging-validation",
    "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json"
}

# Write output
output_path = r"C:\tools\nistframework\ato\ato_workbook.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(workbook, f, indent=2, ensure_ascii=False)

# Stats
print(f"Generated: {output_path}")
print(f"  Total checks: {len(CHECKS)}")
print(f"  Unique data checks: {len(unique_checks)} (incl {sum(1 for _,(t,r) in unique_checks.items() if r)} AzureDiagnostics subtypes)")
print(f"  Unique raw tables: {len(unique_raw_tables)}")
print(f"  Components: {len(components)}")
print(f"  Component list: {', '.join(components)}")

# Unique NIST controls
all_controls = set()
for _,_,_,_,_,c in CHECKS:
    for ctrl in c.split(", "):
        all_controls.add(ctrl.strip())
print(f"  Unique NIST 800-53 controls: {len(all_controls)} ({', '.join(sorted(all_controls))})")
print(f"  File size: {len(json.dumps(workbook, ensure_ascii=False)):,} bytes")
